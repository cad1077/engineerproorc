from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import torch
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
import faiss
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens (útil para desenvolvimento)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos
    allow_headers=["*"],  # Permite todos os headers
)

# Dados do SINAPI com embeddings
items_db = []
with open("dados_sinapi_com_embeddings.json", "r", encoding="utf-8") as f:
    items_db = json.load(f)

if items_db:
    print("Estrutura do primeiro item no items_db:")
    print(items_db[0])

# Carregar composições
composicoes_db = {}
with open("composicoes.json", encoding="utf-8") as f:
    composicoes_db = json.load(f)

# Carregar modelo SentenceTransformer
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_name = "paraphrase-multilingual-MiniLM-L12-v2"
model = SentenceTransformer(model_name)
model.to(device)

# Variáveis para o índice FAISS
embeddings_index: Optional[faiss.IndexFlatL2] = None
embedding_dimension = 384  # Ajuste para a dimensão do seu modelo

class Item(BaseModel):
    id: str
    categoria: str
    descricao: str
    unidade: str
    preco: float
    precos_por_uf: Optional[dict] = None
    embedding_descricao: Optional[List[float]] = None
    tipo: str = "insumo"
    codigo_da_composicao: Optional[str] = None

class CustoMaoDeObra(BaseModel):
    grupo: str
    codigo_da_composicao: str
    descricao: str
    unidade: str
    custos_por_uf: dict

mao_de_obra_db = {}

def carregar_custos_mao_de_obra():
    global mao_de_obra_db
    arquivo_mao_de_obra = "SINAPI_mao_de_obra_2025_02.xlsx"
    abas = ["SEM Desoneração", "COM Desoneração"]
    mao_de_obra_db = {}
    for aba in abas:
        try:
            df = pd.read_excel(arquivo_mao_de_obra, sheet_name=aba, header=5)
            for _, row in df.iterrows():
                grupo = str(row["Grupo"]).strip()
                codigo = str(row["Código da\nComposição"]).strip()
                descricao = str(row["Descrição"]).strip()
                unidade = str(row["Unidade"]).strip()
                custos_por_uf = {}
                for uf in ["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO"]:
                    if uf in row:
                        try:
                            custos_por_uf[uf] = float(row[uf])
                        except (ValueError, TypeError):
                            custos_por_uf[uf] = None
                chave = f"{codigo}-{aba}"
                mao_de_obra_db[chave] = {
                    "grupo": grupo,
                    "codigo_da_composicao": codigo,
                    "descricao": descricao,
                    "unidade": unidade,
                    "custos_por_uf": custos_por_uf,
                    "tipo_custo": aba
                }
        except FileNotFoundError:
            print(f"Arquivo {arquivo_mao_de_obra} não encontrado.")
        except Exception as e:
            print(f"Erro ao carregar dados da planilha de mão de obra ({aba}): {e}")

carregar_custos_mao_de_obra()

@app.on_event("startup")
async def startup_event():
    global embeddings_index
    global embedding_dimension
    global items_db

    if items_db:
        embeddings_list = [item.get("embedding_descricao") for item in items_db if item.get("embedding_descricao")]
        if embeddings_list:
            embeddings_array = np.array(embeddings_list).astype('float32')
            embedding_dimension = embeddings_array.shape[1]
            embeddings_index = faiss.IndexFlatL2(embedding_dimension)
            embeddings_index.add(embeddings_array)
            print("Índice FAISS carregado com sucesso.")
        else:
            print("Nenhum embedding encontrado nos dados do SINAPI.")
    else:
        print("Dados do SINAPI não carregados.")

@app.get("/items", response_model=List[Item])
def get_all_items():
    return items_db

@app.get("/items/{item_id}", response_model=Item)
def get_item_by_id(item_id: str, uf: str = None):
    print(f"Buscando item com ID: {item_id}")
    for item in items_db:
        print(f"ID do item no banco de dados: {item['id']}")
        if str(item["id"]) == item_id:
            item_retorno = item.copy()
            if uf and item.get("precos_por_uf") and uf.upper() in item["precos_por_uf"]:
                item_retorno["preco"] = item["precos_por_uf"][uf.upper()]
            if item_retorno.get("tipo") == "mao_de_obra":
                for chave, mao_de_obra_item in mao_de_obra_db.items():
                    if item_retorno["descricao"].strip() in mao_de_obra_item["descricao"] and item_retorno["unidade"] == mao_de_obra_item["unidade"]:
                        item_retorno["codigo_da_composicao"] = mao_de_obra_item["codigo_da_composicao"]
                        break
            return item_retorno
    raise HTTPException(status_code=404, detail="Item não encontrado")

@app.get("/items/categoria/{categoria}", response_model=List[Item])
def get_items_by_categoria(categoria: str):
    filtered = [item for item in items_db if item["categoria"].lower() == categoria.lower()]
    return filtered

@app.get("/composicoes")
def get_all_composicoes():
    return composicoes_db

@app.get("/composicoes/{codigo}")
def get_composicao_by_codigo(codigo: str):
    composicao = composicoes_db.get(codigo)
    if composicao:
        return composicao
    raise HTTPException(status_code=404, detail="Composição não encontrada")

@app.get("/items/search_semantic/", response_model=List[Item])
def search_items_by_description(query: str = Query(..., description="Termo de busca"), k: int = Query(10, description="Número de resultados")):
    global embeddings_index
    global items_db

    if embeddings_index is None or not items_db:
        return {"message": "Índice de embeddings ou dados do SINAPI não carregados."}

    query_embedding = model.encode(query).astype('float32')
    query_embedding = np.expand_dims(query_embedding, axis=0)

    distances, indices = embeddings_index.search(query_embedding, k)

    results = []
    for index in indices[0]:
        if index < len(items_db):
            results.append(items_db[index])

    return results

@app.get("/items/id/{item_id}/similar/", response_model=List[Item])
def get_similar_items(item_id: int):
    target_item = None
    for item in items_db:
        if item["id"] == item_id and item["embedding_descricao"]:
            target_item = item
            break

    if not target_item:
        raise HTTPException(status_code=404, detail="Item não encontrado ou sem embedding")

    target_embedding = target_item["embedding_descricao"]
    results = []
    for item in items_db:
        if item["id"] != item_id and item["embedding_descricao"]:
            similarity = cosine_similarity([target_embedding], [item["embedding_descricao"]])[0][0]
            results.append({"item": item, "similarity": similarity})

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return [result["item"] for result in results[:5]]

@app.get("/custos_mao_de_obra", response_model=List[CustoMaoDeObra])
def get_custos_mao_de_obra():
    return list(mao_de_obra_db.values())

@app.get("/custos_mao_de_obra/{codigo_composicao}/{uf}")
def get_custo_mao_de_obra_por_codigo_uf(codigo_composicao: str, uf: str, desonerado: bool = False):
    tipo_custo = "SEM Desoneração" if not desonerado else "COM Desoneração"
    chave = f"{codigo_composicao}-{tipo_custo}"
    if chave in mao_de_obra_db:
        custos = mao_de_obra_db[chave]["custos_por_uf"]
        if uf.upper() in custos:
            return {"codigo_da_composicao": codigo_composicao, "uf": uf.upper(), "custo": custos[uf.upper()], "tipo_custo": tipo_custo}
        else:
            raise HTTPException(status_code=404, detail=f"Custo de mão de obra não encontrado para o código {codigo_composicao} e UF {uf.upper()} ({tipo_custo})")
    else:
        raise HTTPException(status_code=404, detail=f"Composição de mão de obra com código {codigo_composicao} não encontrada ({tipo_custo})")