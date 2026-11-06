from fastapi import APIRouter, Depends , status
from sqlalchemy.orm import Session
from sqlalchemy import or_,func
from google import genai
from google.genai import types
from .. import models, oauth2, schemas
from ..database import get_db
from ..config import settings

router = APIRouter(prefix="/vectors", tags=["Vectors"])

client = genai.Client(api_key=settings.gemini_api_key)

def embed_texts(texts: list[str], task: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    res = client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts,
        config=types.EmbedContentConfig(task_type=task, output_dimensionality=768),
    )
    return [e.values for e in res.embeddings]


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ProjectOut)
def create_project_vector(p: schemas.ProjectCreate,
                          db: Session = Depends(get_db),
                          current_user=Depends(oauth2.get_current_user)):
    vec = embed_texts([f"{p.name}\n{p.tech_stack}\n{p.description}"])[0]
    new = models.Project(**p.model_dump(), owner_id=current_user.id, embedding=vec)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new


@router.post("/search", response_model=list[schemas.ProjectOut])
def search_projects(body: schemas.ProjectSearch,
                    db: Session = Depends(get_db),
                    current_user=Depends(oauth2.get_current_user)):
    qv = embed_texts([body.query], "RETRIEVAL_QUERY")[0]
    return (db.query(models.Project)
              .filter(models.Project.owner_id == current_user.id,
                      models.Project.embedding.isnot(None))
              .order_by(models.Project.embedding.cosine_distance(qv))
              #there is something called as query planner, it sees whose costs is less, if hsnw is worth after its overhead, it will be used else NSW
              .limit(body.limit)
              .all())

@router.post("/keyword", response_model=list[schemas.ProjectOut])
def keyword_search(body: schemas.ProjectSearch,
                   db: Session = Depends(get_db),
                   current_user=Depends(oauth2.get_current_user)):
    words = body.query.split()
    # words = " or ".join(body.query.split())
    # use commented line when you want any words mathcing in query , if all words in query should be there in matching sentence, dont uncomment it, as it will be AND operator by default

    tsq = func.websearch_to_tsquery("english", words)
    #to say that query is in englihs, we first construct words and indexes and pass to search_tsv
    return (db.query(models.Project)
              .filter(models.Project.owner_id == current_user.id,
                      models.Project.search_tsv.op("@@")(tsq))
                      # @@ is a match operator, it checks if the tsvector matches the tsquery
              .order_by(func.ts_rank_cd(models.Project.search_tsv, tsq).desc())
              #ts_rank is to see closeness, if i am abishek , and i abishek are there, it will see difference in index position of i and abishek, and give rank accordingly, if i is at 1 and abishek is at 2, it will be closer than if i is at 1 and abishek is at 4
              .limit(body.limit)
              .all())

from sqlalchemy import func, select, literal

@router.post("/hybrid", response_model=list[schemas.ProjectOut])
def hybrid_search(body: schemas.ProjectSearch,
                  db: Session = Depends(get_db),
                  current_user=Depends(oauth2.get_current_user)):
    qv = embed_texts([body.query], "RETRIEVAL_QUERY")[0]
    tsq = func.websearch_to_tsquery("english", " or ".join(body.query.split()))
    P = models.Project

    vec_ids = [r.id for r in
               db.query(P.id)
                 .filter(P.owner_id == current_user.id, P.embedding.isnot(None))
                 .order_by(P.embedding.cosine_distance(qv))
                 .limit(20).all()]

    fts_ids = [r.id for r in
               db.query(P.id)
                 .filter(P.owner_id == current_user.id, P.search_tsv.op("@@")(tsq))
                 .order_by(func.ts_rank_cd(P.search_tsv, tsq).desc())
                 .limit(20).all()]
    # they extract both keyword and vector nearest with their ranks
    scores = {}
    for ids, w in ((vec_ids, 1), (fts_ids, 1.5)):
        for rank, pid in enumerate(ids, start=1):
            scores[pid] = scores.get(pid, 0) + w / (60 + rank)
    #Reciprocal Rank fusion(RRF) as both ranks are different to get to common ground, bigger rank better score

    top = sorted(scores, key=scores.get, reverse=True)[:body.limit]
    rows = {p.id: p for p in db.query(P).filter(P.id.in_(top))}
    return [rows[i] for i in top]