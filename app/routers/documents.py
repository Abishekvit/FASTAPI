import hashlib, re, pymupdf,math
from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import get_db
from ..chunking import split_text
from .vector import embed_texts
import pytesseract

from google import genai
from google.genai import types
from ..config import settings

client = genai.Client(api_key=settings.gemini_api_key)


router = APIRouter(prefix="/documents", tags=["Documents"])
BATCH = 50
#send 50 chunks to gpt to get vector embeddings 
VECTOR_WEIGHT, KEYWORD_WEIGHT = 1.0, 1.0

def clean(t: str) -> str:
    t = re.sub(r"-\n(\w)", r"\1", t)      # fix hyphenated line breaks
    return re.sub(r"[ \t]+", " ", t).strip()

def extract_text(page):
    text = page.get_text()
    #firstly try page.get_text(), if less than 50 got for ocr
    if len(text.strip()) < 50:
        text = pytesseract.image_to_string(
            page.get_pixmap(dpi=300).pil_image()
        )
    return clean(text)

@router.post("/", status_code=status.HTTP_201_CREATED,response_model=schemas.DocumentUploadOut)
async def upload(file: UploadFile, db: Session = Depends(get_db),
                 current_user=Depends(oauth2.get_current_user)):
    data = await file.read()
    h = hashlib.sha256(data).hexdigest()
    #this creates a particular hash value to identify the file
    if db.query(models.Document).filter_by(file_hash=h, owner_id=current_user.id).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Already uploaded")

    pdf = pymupdf.open(stream=data, filetype="pdf")
    #pymupdf only for pdf opening and page contents in text, not ocr
    doc = models.Document(filename=file.filename, file_hash=h, owner_id=current_user.id)
    db.add(doc); db.flush()

    rows, idx = [], 0
    for pno, page in enumerate(pdf, start=1):
        for text in split_text(extract_text(page)):
            #now it goes to extract_text function
            rows.append(models.Chunk(document_id=doc.id, page=pno, chunk_index=idx,
                                     content=f"{file.filename}\n{text}"))  # contextual prefix
            idx += 1
    if not rows:
        raise HTTPException(400, "No text found (scanned PDF? needs OCR)")

    for i in range(0, len(rows), BATCH):
        b = rows[i:i + BATCH]
        for r, v in zip(b, embed_texts([r.content for r in b])):
            r.embedding = v
    db.add_all(rows); db.commit()
    return {"document_id": doc.id, "chunks": rows}

@router.post("/search", response_model=list[schemas.ChunkOut])
def search(body: schemas.ProjectSearch, db: Session = Depends(get_db),
           current_user=Depends(oauth2.get_current_user)):
    C, D = models.Chunk, models.Document
    qv = embed_texts([body.query], "RETRIEVAL_QUERY")[0]
    tsq = func.websearch_to_tsquery("english", " or ".join(body.query.split()))
    base = db.query(C.id).join(D, D.id == C.document_id).filter(D.owner_id == current_user.id)
    N = base.count()
    vec_ids = [r.id for r in base.filter(C.embedding.isnot(None))
               .order_by(C.embedding.cosine_distance(qv)).limit(20)]
    df = base.filter(C.search_tsv.op("@@")(tsq)).count()

    idf = math.log(1 + (N - df + 0.5) / (df + 0.5))
    #formula to make rare elements in tsvector more valued
    #idf stands for inverse document frequency, which is a measure of how important a term is in the context of the entire document collection. The formula calculates the idf value based on the total number of documents (N) and the number of doc containing df term

    fts_ids = [r.id for r in base.filter(C.search_tsv.op("@@")(tsq))
           .order_by((func.ts_rank_cd(C.search_tsv, tsq) * idf).desc()).limit(20)]
    #here we multiply by idf
    scores = {}
    for ids, w in ((vec_ids, 1), (fts_ids, 10)):
        for rank, cid in enumerate(ids, start=1):
            scores[cid] = scores.get(cid, 0) + w / (60 + rank)
    top = sorted(scores, key=scores.get, reverse=True)[:body.limit]
    rows = {c.id: c for c in db.query(C).filter(C.id.in_(top))}
    return [rows[i] for i in top]

@router.post("/rag", response_model=schemas.RAGResponse)
def search(body: schemas.ProjectSearch, db: Session = Depends(get_db),
           current_user=Depends(oauth2.get_current_user)):

    C, D = models.Chunk, models.Document
    qv = embed_texts([body.query], "RETRIEVAL_QUERY")[0]
    tsq = func.websearch_to_tsquery("english", " or ".join(body.query.split()))
    base = db.query(C.id).join(D, D.id == C.document_id).filter(D.owner_id == current_user.id)
    N = base.count()
    vec_ids = [r.id for r in base.filter(C.embedding.isnot(None))
               .order_by(C.embedding.cosine_distance(qv)).limit(20)]
    df = base.filter(C.search_tsv.op("@@")(tsq)).count()
    idf = math.log(1 + (N - df + 0.5) / (df + 0.5))
    fts_ids = [r.id for r in base.filter(C.search_tsv.op("@@")(tsq))
               .order_by((func.ts_rank_cd(C.search_tsv, tsq) * idf).desc()).limit(20)]
    # Reciprocal Rank Fusion
    scores = {}
    for ids, w in ((vec_ids, 1), (fts_ids, 10)):
        for rank, cid in enumerate(ids, start=1):
            scores[cid] = scores.get(cid, 0) + w / (60 + rank)
    top = sorted(scores, key=scores.get, reverse=True)[:body.limit]
    rows = {c.id: c for c in db.query(C).filter(C.id.in_(top))}
    chunks = [rows[i] for i in top]

    # -------- RAG GENERATION STARTS HERE --------

    context = "\n\n".join(
        f"Source {i+1}:\n{chunk.content}"
        for i, chunk in enumerate(chunks)
    )
    prompt = f"""
    Answer the user's question using the provided context.
    CONTEXT:
    {context}
    QUESTION:
    {body.query}

    Instructions:
    1. Answer using the provided context.
    2. Do not invent information.
    3. If the answer is not available in the context, explicitly say so.
    4. Give a clear and well-structured answer.
    """

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.3
        )
    )
    if not response.text:
        raise HTTPException(500, "Gemini failed to generate an answer")

    return {
        "answer": response.text,
        "chunks": chunks
    }