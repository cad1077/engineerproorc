import pandas as pd
import json
import os

# Função para extrair dados de mão de obra
def extrair_mao_de_obra(path):
    print(f"🔍 Lendo mão de obra: {path}")
    df = pd.read_excel(path, sheet_name=0)
    df.columns = df.columns.str.strip()

    registros = []

    for _, row in df.iterrows():
        try:
            codigo = str(row['Código']).strip()
            descricao = str(row['Descrição']).strip()
            unidade = str(row['Unidade']).strip()
            uf = str(row['UF']).strip()
            preco = float(row['Preço Hora R$'])

            registros.append({
                "codigo": codigo,
                "descricao": descricao,
                "unidade": unidade,
                "tipo": "mao_de_obra",
                "uf": uf,
                "preco": preco
            })
        except Exception as e:
            continue  # Ignorar linhas com erro

    return registros

# Função para extrair dados de insumos e serviços
def extrair_referencia(path):
    print(f"🔍 Lendo referência: {path}")
    df = pd.read_excel(path, sheet_name=0)
    df.columns = df.columns.str.strip()

    registros = []

    for _, row in df.iterrows():
        try:
            codigo = str(row['Código']).strip()
            descricao = str(row['Descrição']).strip()
            unidade = str(row['Unidade']).strip()
            uf = str(row['UF']).strip()
            preco = float(row['Preço Médio R$'])

            registros.append({
                "codigo": codigo,
                "descricao": descricao,
                "unidade": unidade,
                "tipo": "insumo",
                "uf": uf,
                "preco": preco
            })
        except Exception as e:
            continue  # Ignorar linhas com erro

    return registros

# Função para consolidar registros no formato desejado
def consolidar(registros):
    print(f"🔄 Consolidando {len(registros)} registros...")
    base = {}

    for item in registros:
        cod = item['codigo']
        if cod not in base:
            base[cod] = {
                "codigo": item['codigo'],
                "descricao": item['descricao'],
                "unidade": item['unidade'],
                "tipo": item['tipo'],
                "valores_por_uf": {}
            }
        base[cod]["valores_por_uf"][item['uf']] = item['preco']

    return list(base.values())

# Função principal
def main():
    # Caminhos dos arquivos (podem ser ajustados conforme necessário)
    ref_path = "SINAPI_Referência_2025_02.xlsx"
    mao_path = "SINAPI_mao_de_obra_2025_02.xlsx"
    output_path = "dados_sinapi.json"

    # Verificar se os arquivos existem
    if not os.path.exists(ref_path):
        print(f"❌ Arquivo não encontrado: {ref_path}")
        return
    if not os.path.exists(mao_path):
        print(f"❌ Arquivo não encontrado: {mao_path}")
        return

    # Extração
    mao = extrair_mao_de_obra(mao_path)
    insumos = extrair_referencia(ref_path)

    # Consolidação
    todos = mao + insumos
    consolidados = consolidar(todos)

    # Exportação para JSON
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(consolidados, f, ensure_ascii=False, indent=2)

    print(f"✅ Base de dados consolidada criada: {output_path}")

if __name__ == "__main__":
    main()
