import streamlit as st
import requests
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO

st.title("Engineer.Pro Orçamentos")

api_url = "http://localhost:8000"

# Inicializa o histórico do chat no session state
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Inicializa a lista de itens no orçamento final no session state
if 'orcamento_final_itens' not in st.session_state:
    st.session_state['orcamento_final_itens'] = []

def fetch_sinapi_items():
    try:
        response = requests.get(f"{api_url}/items")
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar com a API: {e}")
        return None

def search_sinapi_semantic(query):
    try:
        response = requests.get(f"{api_url}/items/search_semantic/?query={query}")
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar com a API para busca semântica: {e}")
        return data

sinapi_items = fetch_sinapi_items()

st.subheader("Chatbot de Orçamentos SINAPI")

# Exibe o histórico do chat
for message in st.session_state['chat_history']:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

user_query = st.chat_input("Digite sua pergunta:")

if user_query:
    st.session_state['chat_history'].append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    intent = None
    query_lower = user_query.lower()

    if query_lower.startswith("remover") or query_lower.startswith("eliminar"):
        intent = "remover"
    elif query_lower.startswith("ver orçamento") or query_lower.startswith("mostrar orçamento"):
        intent = "ver_orcamento"
    elif query_lower.startswith("gerar pdf") or query_lower.startswith("baixar orçamento"):
        intent = "gerar_pdf"
    elif query_lower.startswith("adicionar") or query_lower.startswith("incluir"):
        intent = "adicionar"
    elif query_lower.startswith("ajuda") or query_lower.startswith("como usar"):
        intent = "ajuda"
    else:
        intent = "adicionar" # Se não identificar outra intenção, tenta adicionar

    if intent == "remover":
        term_to_remove = user_query.split(maxsplit=1)[1].strip()
        items_to_remove_indices = []
        for index, item in enumerate(st.session_state['orcamento_final_itens']):
            if term_to_remove in item['descricao'].lower():
                items_to_remove_indices.append(index)

        if items_to_remove_indices:
            with st.chat_message("bot"):
                st.markdown(f"Removendo {len(items_to_remove_indices)} itens correspondentes a '{term_to_remove}' do orçamento.")
            for index in sorted(items_to_remove_indices, reverse=True):
                del st.session_state['orcamento_final_itens'][index]
            st.rerun()
        else:
            with st.chat_message("bot"):
                st.markdown(f"Não encontrei nenhum item no orçamento com a descrição '{term_to_remove}'.")
        st.session_state['chat_history'].append({"role": "bot", "content": "Resposta do bot sobre a remoção de itens."})

    elif intent == "ver_orcamento":
        with st.chat_message("bot"):
            if st.session_state['orcamento_final_itens']:
                st.markdown("Itens atualmente no seu orçamento:")
                for item in st.session_state['orcamento_final_itens']:
                    st.markdown(f"- {item['quantidade']} unidades de {item['descricao']} ({item['unidade']})")
            else:
                st.markdown("Seu orçamento está vazio no momento.")
        st.session_state['chat_history'].append({"role": "bot", "content": "Exibindo o orçamento final no chat."})

    elif intent == "gerar_pdf":
        with st.chat_message("bot"):
            st.markdown("Gerando o PDF do orçamento.")
        st.session_state['chat_history'].append({"role": "bot", "content": "Gerando o PDF do orçamento."})
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        # Título do Orçamento
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 750, "Orçamento Final")
        p.setFont("Helvetica", 12)
        p.drawString(100, 730, "Engineer.Pro Orçamentos")
        p.line(100, 725, 500, 725)
        # Cabeçalho da tabela de itens
        y_position = 700
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, y_position, "Descrição")
        p.drawString(350, y_position, "Quantidade")
        p.drawString(420, y_position, "Preço Unitário")
        p.drawString(500, y_position, "Preço Total")
        p.line(100, y_position - 5, 550, y_position - 5)
        y_position -= 15
        # Adicionar os itens do orçamento
        p.setFont("Helvetica", 10)
        total_orcamento_pdf = 0
        for item in st.session_state['orcamento_final_itens']:
            if 'preco_unitario' in item and 'preco_total' in item and 'quantidade' in item:
                p.drawString(100, y_position, item['descricao'])
                p.drawString(350, y_position, str(item['quantidade']))
                p.drawString(420, y_position, f"R$ {item['preco_unitario']:.2f}")
                p.drawString(500, y_position, f"R$ {item['preco_total']:.2f}")
                y_position -= 15
                total_orcamento_pdf += item['preco_total']
                if y_position < 100:
                    p.showPage()
                    y_position = 750
                    p.setFont("Helvetica-Bold", 12)
                    p.drawString(100, y_position, "Descrição")
                    p.drawString(350, y_position, "Quantidade")
                    p.drawString(420, y_position, "Preço Unitário")
                    p.drawString(500, y_position, "Preço Total")
                    p.line(100, y_position - 5, 550, y_position - 5)
                    y_position -= 15
        # Total do Orçamento
        p.line(400, y_position - 5, 550, y_position - 5)
        y_position -= 15
        p.setFont("Helvetica-Bold", 12)
        p.drawString(420, y_position, "Total:")
        p.drawString(500, y_position, f"R$ {total_orcamento_pdf:.2f}")

        p.showPage()
        p.save()
        pdf_out = buffer.getvalue()
        st.download_button(
            label="Download Orçamento em PDF",
            data=pdf_out,
            file_name="orcamento_sinapi.pdf",
            mime="application/pdf"
        )
        with st.chat_message("bot"):
            st.markdown("O PDF do orçamento está pronto para download.")
        st.session_state['chat_history'].append({"role": "bot", "content": "O PDF do orçamento está pronto para download."})

    elif intent == "adicionar":
        quantities = {}
        item_query_parts = query_lower.split()
        temp_item_query = list(item_query_parts)

        for i, part in enumerate(item_query_parts):
            try:
                qty = int(part)
                if i > 0:
                    item_name_phrase = " ".join(item_query_parts[max(0, i - 2):i])
                    quantities[item_name_phrase] = qty
                    if part in temp_item_query:
                        temp_item_query.remove(part)
                elif i < len(item_query_parts) - 1:
                    item_name_phrase = " ".join(item_query_parts[i + 1:min(len(item_query_parts), i + 3)])
                    quantities[item_name_phrase] = qty
                    if part in temp_item_query:
                        temp_item_query.remove(part)
            except ValueError:
                pass

        item_query_str = " ".join(temp_item_query)
        semantic_results = search_sinapi_semantic(item_query_str)

        if semantic_results:
            added_items = False
            with st.chat_message("bot"):
                st.markdown(f"Analisando sua pergunta: **{user_query}**")
                for item in semantic_results[:3]:
                    suggested_item_name = item['descricao'].lower()
                    quantity_to_add = 1
                    for phrase, qty in quantities.items():
                        if phrase in suggested_item_name or suggested_item_name in phrase:
                            quantity_to_add = qty
                            break
                    item['quantidade'] = quantity_to_add
                    st.session_state['orcamento_final_itens'].append(item)
                    st.markdown(f"Adicionando {quantity_to_add} unidades de {item['descricao']} ao orçamento.")
                    added_items = True
                    break

            if not added_items:
                st.markdown("Não consegui identificar claramente o item e a quantidade. Por favor, tente novamente ou use a busca manual.")
            st.session_state['chat_history'].append({"role": "bot", "content": "Resposta do bot sobre a adição de itens."})
        else:
            bot_response = "Não encontrei nenhum item relacionado à sua pergunta."
            st.session_state['chat_history'].append({"role": "bot", "content": bot_response})
            with st.chat_message("bot"):
                st.markdown(bot_response)

    elif intent == "ajuda":
        with st.chat_message("bot"):
            st.markdown("Aqui estão alguns comandos que você pode usar:")
            st.markdown("- `Adicionar [item] [quantidade]` (ex: `Adicionar tijolo 10 unidades`)")
            st.markdown("- `Remover [item]` (ex: `Remover cimento`)")
            st.markdown("- `Ver orçamento` ou `Mostrar orçamento`")
            st.markdown("- `Gerar pdf` ou `Baixar orçamento`")
            st.markdown("Você também pode fazer perguntas gerais sobre itens.")
        st.session_state['chat_history'].append({"role": "bot", "content": "Exibindo a ajuda."})