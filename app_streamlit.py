from fastapi import FastAPI
from pydantic import BaseModel
import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Criação do banco de dados e modelo
Base = declarative_base()

class SinapiItem(Base):
    __tablename__ = 'sinapi_items'
    id = Column(Integer, primary_key=True)
    codigo = Column(String(50), index=True)
    descricao = Column(String)
    unidade = Column(String(20))
    preco_unitario = Column(Float)
    
engine = create_engine('sqlite:///sinapi.db')
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Carregamento do modelo de embedding OTIMIZADO para economia de memória
# Essa é a mudança mais importante!
model = SentenceTransformer('all-MiniLM-L6-v2')

# Carregamento dos dados e do índice FAISS
sinapi_data = []
try:
    with open("sinapi_dados.json", "r", encoding="utf-8") as f:
        sinapi_data = json.load(f)
except FileNotFoundError:
    print("Arquivo sinapi_dados.json não encontrado. Certifique-se de que ele está no mesmo diretório.")
    
embeddings = np.array([item['embedding'] for item in sinapi_data]).astype("float32")
faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
faiss_index.add(embeddings)

app = FastAPI()

class Query(BaseModel):
    query: str

@app.get("/items")
def get_all_items():
    return sinapi_data

@app.get("/items/search_semantic/")
def search_semantic(query: str):
    try:
        query_embedding = model.encode(query, convert_to_tensor=True)
        query_embedding_np = query_embedding.cpu().numpy().astype("float32").reshape(1, -1)
        distances, indices = faiss_index.search(query_embedding_np, k=5)
        
        results = []
        for i in range(5):
            if indices[0][i] != -1:
                item = sinapi_data[indices[0][i]]
                results.append({
                    "descricao": item["descricao"],
                    "unidade": item["unidade"],
                    "preco_unitario": item["preco_unitario"],
                    "preco_total": item["preco_unitario"],
                    "quantidade": 1,
                })
        return results
    except Exception as e:
        return {"error": str(e)}

# Adicione outros endpoints aqui se houver
# ...
