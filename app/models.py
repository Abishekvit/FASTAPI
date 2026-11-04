#We are gonna define schema
from sqlalchemy import Column, Integer, String,Boolean,ForeignKey,Index
from .database import Base
from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
#we imported relationship 
from pgvector.sqlalchemy import Vector
#we have imported vector from pgvector.sqlalchemy to use vector data type in our models

#Inherited properties and object mapping of Base class

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer,primary_key=True,nullable=False)
    title = Column(String,nullable=False)
    content = Column(String,nullable=False)
    published = Column(Boolean,server_default='TRUE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False,server_default=func.now())
    #there we has primary key and is null in postgre
    #we use alembic to create migration file and it can change the existing table also ulike rn, where if table exists it wont alter
    owner_id = Column(Integer,ForeignKey("users.id",ondelete="CASCADE"),nullable=False)
    #owner id Foreign key
    owner = relationship("User")
    #relationship is like NATURAL JOIN, automatically joins based on foreign key

class User(Base):
    __tablename__ = "users"
    id = Column(Integer,primary_key=True,nullable=False)
    email = Column(String,nullable=False,unique=True)
    password = Column(String,nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False,server_default=func.now())

class Vote(Base):
    __tablename__ = "votes"
    user_id = Column(Integer,ForeignKey(
        "users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer,ForeignKey(
            "posts.id", ondelete="CASCADE"), primary_key=True)


from sqlalchemy import Column, Integer, String, ForeignKey, Index, Computed, func
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.sql.sqltypes import TIMESTAMP
from pgvector.sqlalchemy import Vector

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    tech_stack = Column(String, nullable=False)
    description = Column(String, nullable=False)
    embedding = Column(Vector(768))
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())
    search_tsv = Column(
        TSVECTOR,
        Computed("to_tsvector('english', name || ' ' || tech_stack || ' ' || description)",
                 persisted=True),
        # It stores only the words present, with positions: 'analyz':1 'genom':2
        #automatically updates gin
    )
    #table_args is another way to define indexes, constraints, etc. It is a tuple of Index objects
    __table_args__ = (
        Index(
            "ix_projects_embedding_hnsw",
            "embedding",
            postgresql_using="hnsw",
            postgresql_with={"m": 4, "ef_construction": 8},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
        #TEXT SEARCH VECTOR
        Index("ix_projects_tsv", "search_tsv", postgresql_using="gin"),
        #Generalised inverted index, analyz  → [1, 4]
        # genom   → [1]
        # python  → [1, 3]
        # bus     → [2]
        #usually it is row -> words, this is reverse, word -> rows, so we can search for a word and get all rows
    )
#     __table_args__ = (
#     Index(
#         "ix_projects_embedding_ivf",
#         "embedding",
#         postgresql_using="ivfflat",
#         postgresql_with={"lists": 100},
#         postgresql_ops={"embedding": "vector_cosine_ops"},
#     ),
# )
#for ivfflat: which is basically forming cluster centroid, then addig the new data to closese centroid , and then we take mean of vectors inside the cluster and find centroid and check if it is close to any and add that
#so we have bags to look into , optimised search, may not be true

#Chunking and document
class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=func.now())

class Chunk(Base):
    __tablename__ = "chunks"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page = Column(Integer)
    chunk_index = Column(Integer)
    content = Column(String, nullable=False)
    embedding = Column(Vector(768))
    search_tsv = Column(TSVECTOR, Computed("to_tsvector('english', content)", persisted=True))
    document = relationship("Document")

    __table_args__ = (
        Index("ix_chunks_embedding_hnsw", "embedding", postgresql_using="hnsw",
              postgresql_with={"m": 16, "ef_construction": 64},
              postgresql_ops={"embedding": "vector_cosine_ops"}),
        Index("ix_chunks_tsv", "search_tsv", postgresql_using="gin"),
    )