from fastapi import APIRouter, Depends , status
from sqlalchemy.orm import Session
from google import genai
from google.genai import types
from .. import models, oauth2, schemas
from ..database import get_db
from ..config import settings

router = APIRouter(prefix="/vectors", tags=["Vectors"])

client = genai.Client(api_key=settings.gemini_api_key)
BATCH = 50  # texts per embedding call


def embed_texts(texts: list[str], task: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    res = client.models.embed_content(
        model="gemini-embedding-001",
        contents=texts,
        config=types.EmbedContentConfig(task_type=task, output_dimensionality=768),
    )
    return [e.values for e in res.embeddings]


def project_text(p: models.Project) -> str:
    return f"{p.name}\n{p.tech_stack}\n{p.description}"


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
              .limit(body.limit)
              .all())