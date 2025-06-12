import pandas as pd
import json

def extract_data_from_excel(file_path):
    all_data = []

    # Planilha de Familias e Coeficientes (pode conter alguns insumos)
    try:
        df_familias = pd.read_excel(file_path, sheet_name="Coeficientes", header=0) # Correção para "Coeficientes"
        for index, row in df_familias.iterrows():
            item = {
                "id": int(row.get("Código", 0)),
                "categoria": "Desconhecida", # Você pode precisar inferir ou adicionar essa informação
                "descricao": str(row.get("Descrição", "")).strip(),
                "unidade": str(row.get("Unidade", "")).strip(),
                "preco": float(row.get("Preço Referencial", 0) or row.get("Preço", 0)), # Tenta diferentes colunas de preço
                "tipo": "insumo"
            }
            if item["id"] != 0 and item["descricao"]:
                all_data.append(item)
    except Exception as e:
        print(f"Erro ao ler 'Coeficientes' de {file_path}: {e}")

    # Planilha de Manutenções (pode conter insumos)
    try:
        file_manutencoes = "SINAPI_Manutenções_2025_02.xlsx"
        df_manutencoes = pd.read_excel(file_manutencoes, sheet_name="Manutenções", header=0) # Correção para "Manutenções"
        for index, row in df_manutencoes.iterrows():
            item = {
                "id": int(row.get("CODIGO", 0)),
                "categoria": "Manutenção",
                "descricao": str(row.get("DESCRICAO", "")).strip(),
                "unidade": str(row.get("UNIDADE", "")).strip(),
                "preco": float(row.get("PRECO MEDIO", 0) or row.get("PREÇO MÉDIO", 0)), # Tenta diferentes colunas de preço
                "tipo": "insumo"
            }
            if item["id"] != 0 and item["descricao"]:
                all_data.append(item)
    except Exception as e:
        print(f"Erro ao ler 'Manutenções' de {file_manutencoes}: {e}")
    except ValueError:
        print(f"Erro de valor ao ler 'Manutenções' de {file_manutencoes}: {e}")


    # Planilha de Mão de Obra
    file_mao_de_obra = "SINAPI_mao_de_obra_2025_02.xlsx"
    abas = ["SEM Desoneração", "COM Desoneração"]
    for aba in abas:
        try:
            df_mao_de_obra = pd.read_excel(file_mao_de_obra, sheet_name=aba, header=5)
            for index, row in df_mao_de_obra.iterrows():
                codigo = str(row.get("Código da\nComposição", "")).strip()
                descricao = str(row.get("Descrição", "")).strip()
                unidade = str(row.get("Unidade", "")).strip()
                # Vamos pegar o preço de MG por padrão (você pode adaptar)
                preco_mg = row.get("MG")
                if pd.notna(preco_mg):
                    item = {
                        "id": hash(f"mao_de_obra-{codigo}-{aba}"), # Cria um ID único
                        "categoria": "Mão de Obra",
                        "descricao": f"{descricao} ({aba})",
                        "unidade": unidade,
                        "preco": float(preco_mg),
                        "tipo": "mao_de_obra"
                    }
                    if item["descricao"]:
                        all_data.append(item)
        except Exception as e:
            print(f"Erro ao ler '{aba}' de {file_mao_de_obra}: {e}")

    return all_data

if __name__ == "__main__":
    sinapi_file = "SINAPI_familias_e_coeficientes_2025_02.xlsx" # Ajuste o nome do arquivo principal
    all_sinapi_data = extract_data_from_excel(sinapi_file)

    with open("dados_sinapi.json", "w", encoding="utf-8") as f:
        json.dump(all_sinapi_data, f, ensure_ascii=False, indent=4)

    print("Dados extraídos e salvos em dados_sinapi.json")