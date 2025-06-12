import pandas as pd
import json

# Carregar planilha
arquivo = "SINAPI_familias_e_coeficientes_2025_02.xlsx"

# Carregar a planilha correta com as composições, especificando a linha do cabeçalho
df = pd.read_excel(arquivo, sheet_name=0, header=4)

# Renomear colunas se necessário (adaptar conforme sua planilha)
# Você pode comentar ou remover esta linha se os nomes das colunas na planilha estiverem corretos
# df.columns = [col.strip() for col in df.columns]

# Filtrar e organizar as composições
composicoes = {}
for _, row in df.iterrows():
    # Tente novamente com "Código da Composição"
    cod_composicao_col = "Código da Composição"
    if cod_composicao_col not in df.columns:
        cod_composicao_col = "Código Composição" # Tenta a versão sem o "da"

    try:
        cod_composicao = str(row[cod_composicao_col]).strip()
        if cod_composicao not in composicoes:
            composicoes[cod_composicao] = {
                "descricao": row["Descrição Composição"],
                "unidade": row["Unidade"],
                "itens": []
            }
        composicoes[cod_composicao]["itens"].append({
            "codigo_insumo": row["Código Insumo"],
            "descricao_insumo": row["Descrição do Insumo"],
            "unidade": row["Unidade Insumo"],
            "coeficiente": row["Coeficientes" if "Coeficientes" in df.columns else "Coeficiente"]
        })
    except KeyError as e:
        print(f"Erro ao acessar coluna: {e}")
        print(f"Linha com problema: {row}")
        break # Para a execução ao encontrar o primeiro erro grave

# Salvar em JSON
with open("composicoes.json", "w", encoding="utf-8") as f:
    json.dump(composicoes, f, ensure_ascii=False, indent=2)

print("Arquivo composicoes.json gerado com sucesso!")