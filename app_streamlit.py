from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

# A classe BaseModel deve ser a mesma que você já tem para a sua lógica
class Orcamento(BaseModel):
    id: int
    titulo: str
    descricao: str

# Esta é a parte que foi alterada: O modelo é instanciado aqui
# com o nome 'all-MiniLM-L6-v2', que é otimizado para economia de memória.
model = SentenceTransformer('all-MiniLM-L6-v2')

# O restante do seu código, como a conexão com o banco de dados e
# o carregamento do índice FAISS, deve vir aqui.
# Por exemplo:
# ...

app = FastAPI()

class Query(BaseModel):
    user_input: str

@app.post("/buscar_orcamento")
def buscar_orcamento(query: Query):
    # Processa a entrada do usuário para gerar o embedding
    embedding_query = model.encode(query.user_input)

    # Converte o embedding para o formato que o FAISS espera
    embedding_query = np.array([embedding_query]).astype("float32")

    # Realiza a busca por similaridade usando o índice FAISS
    # O código abaixo é um exemplo e deve ser adaptado à sua lógica de busca
    # distances, indices = index.search(embedding_query, k=5) 
    
    # Exemplo de retorno
    return {"resultado": "Seu resultado da busca aqui"}

# O restante dos seus endpoints FastAPI vêm aqui
# ...
