import pandas as pd
import json
from sentence_transformers import SentenceTransformer
import torch

def generate_sinapi_data(referencia_file, familias_file, mao_de_obra_file, output_sinapi, output_embeddings):
    items_db = []

    # Processar SINAPI_Referência_2025_02.xlsx
    try:
        df_referencia = pd.read_excel(referencia_file, sheet_name="Analítico", header=9)
        for index, row in df_referencia.iterrows():
            item_id = str(row['Código do\nItem']).strip()
            descricao = str(row['Descrição']).strip()
            unidade = str(row['Unidade']).strip()
            # O nome da coluna de preço pode variar, confira na sua planilha
            preco_coluna = 'Valor R$'
            if preco_coluna in row:
                preco = row[preco_coluna]
                items_db.append({
                    "id": item_id,
                    "categoria": "Referência",
                    "descricao": descricao,
                    "unidade": unidade,
                    "preco": preco,
                    "tipo": "insumo" if row['Tipo Item'].strip() == 'INSUMO' else 'composicao',
                    "codigo_da_composicao": str(row['Código da\nComposição']).strip()
                })
    except FileNotFoundError:
        print(f"Arquivo {referencia_file} não encontrado.")
    except Exception as e:
        print(f"Erro ao processar {referencia_file}: {e}")

    # Processar SINAPI_familias_e_coeficientes_2025_02.xlsx (aba "Coeficientes")
    try:
        df_familias = pd.read_excel(familias_file, sheet_name="Coeficientes", header=5)
        for index, row in df_familias.iterrows():
            item_id = str(row['Código do\nInsumo']).strip()
            descricao = str(row['Descrição do Insumo']).strip()
            unidade = str(row['Unidade']).strip()
            preco = row['MG'] if 'MG' in row else 0.0 # Pegando o preço de MG como exemplo
            categoria = str(row['Categoria']).strip()
            items_db.append({
                "id": item_id,
                "categoria": f"Família e Coeficientes - {categoria}",
                "descricao": descricao,
                "unidade": unidade,
                "preco": preco,
                "tipo": "insumo"
            })
    except FileNotFoundError:
        print(f"Arquivo {familias_file} não encontrado.")
    except Exception as e:
        print(f"Erro ao processar {familias_file}: {e}")

    # Processar SINAPI_mao_de_obra_2025_02.xlsx
    abas_mao_de_obra = ["SEM Desoneração", "COM Desoneração"]
    for aba in abas_mao_de_obra:
        try:
            df_mao_de_obra = pd.read_excel(mao_de_obra_file, sheet_name=aba, header=5)
            for index, row in df_mao_de_obra.iterrows():
                codigo_composicao = str(row['Código da\nComposição']).strip()
                descricao = str(row['Descrição']).strip()
                unidade = str(row['Unidade']).strip()
                # Usando um ID combinado para garantir unicidade
                item_id = f"MOB-{codigo_composicao}-{aba}"
                preco = row['MG'] if 'MG' in row else 0.0 # Pegando o preço de MG como exemplo
                items_db.append({
                    "id": item_id,
                    "categoria": "Mão de Obra",
                    "descricao": descricao,
                    "unidade": unidade,
                    "preco": preco,
                    "tipo": "mao_de_obra",
                    "codigo_da_composicao": codigo_composicao
                })
        except FileNotFoundError:
            print(f"Arquivo {mao_de_obra_file} não encontrado.")
        except Exception as e:
            print(f"Erro ao processar {mao_de_obra_file} aba {aba}: {e}")

    # Salvar dados SINAPI sem embeddings
    with open(output_sinapi, "w", encoding="utf-8") as f:
        json.dump(items_db, f, ensure_ascii=False, indent=4)

    # Gerar embeddings
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_name = "paraphrase-multilingual-MiniLM-L12-v2"
    model = SentenceTransformer(model_name)
    model.to(device)

    items_db_with_embeddings = []
    for item in items_db:
        embedding = model.encode(item["descricao"]).tolist()
        items_db_with_embeddings.append({**item, "embedding_descricao": embedding})

    # Salvar dados SINAPI com embeddings
    with open(output_embeddings, "w", encoding="utf-8") as f:
        json.dump(items_db_with_embeddings, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    referencia_file = "SINAPI_Referência_2025_02.xlsx"
    familias_file = "SINAPI_familias_e_coeficientes_2025_02.xlsx"
    mao_de_obra_file = "SINAPI_mao_de_obra_2025_02.xlsx"
    output_sinapi_file = "dados_sinapi.json"
    output_embeddings_file = "dados_sinapi_com_embeddings.json"

    generate_sinapi_data(referencia_file, familias_file, mao_de_obra_file, output_sinapi_file, output_embeddings_file)
    print(f"Arquivos {output_sinapi_file} e {output_embeddings_file} gerados com sucesso.")