
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import json

app = FastAPI()

# Carregamento dos dados do SINAPI
with open("dados_sinapi.json", encoding="utf-8") as f:
    items_db = json.load(f)

with open("composicoes_com_uf.json", encoding="utf-8") as f:
    composicoes_db = json.load(f)

# Modelos de dados
class Item(BaseModel):
    id: int
    categoria: str
    descricao: str
    unidade: str
    preco: float

class CoeficientesUF(BaseModel):
    coeficientes: Dict[str, float]

class ComposicaoItem(BaseModel):
    codigo_insumo: str
    descricao_insumo: str
    unidade: str
    categoria: str
    coeficientes: Dict[str, float]

class Composicao(BaseModel):
    itens: List[ComposicaoItem]

# Endpoints dos itens
@app.get("/items", response_model=List[Item])
def get_all_items():
    return items_db

@app.get("/items/{item_id}", response_model=Item)
def get_item_by_id(item_id: int):
    for item in items_db:
        if item["id"] == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item não encontrado")

@app.get("/items/categoria/{categoria}", response_model=List[Item])
def get_items_by_categoria(categoria: str):
    filtered = [item for item in items_db if item["categoria"].lower() == categoria.lower()]
    return filtered

# Endpoints das composições
@app.get("/composicoes", response_model=Dict[str, Composicao])
def get_all_composicoes():
    return composicoes_db

@app.get("/composicoes/{codigo}", response_model=Composicao)
def get_composicao_by_codigo(codigo: str):
    composicao = composicoes_db.get(codigo)
    if composicao:
        return composicao
    raise HTTPException(status_code=404, detail="Composição não encontrada")
