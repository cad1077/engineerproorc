import json
from sentence_transformers import SentenceTransformer
import torch

# Verificar se a CUDA está disponível e definir o dispositivo
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Usando dispositivo: {device}")

# Carregar dados do SINAPI
with open("dados_sinapi.json", "r", encoding="utf-8") as f:
    items_db = json.load(f)

# Carregar o modelo SentenceTransformer
model_name = "paraphrase-multilingual-MiniLM-L12-v2"
model = SentenceTransformer(model_name)
model.to(device) # Mover o modelo para a GPU, se disponível

# Gerar embeddings para as descrições
for item in items_db:
    descricao = item["descricao"]
    embedding = model.encode(descricao)
    item["embedding_descricao"] = embedding.tolist() # Converter para lista para serializar em JSON

# Salvar os dados com embeddings em um novo arquivo
with open("dados_sinapi_com_embeddings.json", "w", encoding="utf-8") as f:
    json.dump(items_db, f, ensure_ascii=False, indent=2)

print("Embeddings gerados e salvos em dados_sinapi_com_embeddings.json")