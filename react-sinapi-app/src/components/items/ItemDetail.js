// src/components/items/ItemDetail.js
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

function ItemDetail() {
  // useState para armazenar os detalhes do item específico
  const [item, setItem] = useState(null);
  // useParams é um hook do react-router-dom que permite acessar os parâmetros da URL
  const { id } = useParams(); // 'id' corresponde ao parâmetro definido na rota em App.js ('/items/:id')
  // URL base da sua API FastAPI
  const apiUrl = 'http://localhost:8000';

  // useEffect para buscar os detalhes do item assim que o componente ItemDetail é montado ou quando o 'id' na URL muda
  useEffect(() => {
    // Função assíncrona para buscar os detalhes do item da API
    const fetchItem = async () => {
      try {
        // Fazendo uma requisição GET para o endpoint /items/{id} da API, usando o ID da URL
        const response = await fetch(`${apiUrl}/items/${id}`);
        // Verificando se a resposta foi bem-sucedida
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        // Convertendo a resposta para JSON
        const data = await response.json();
        // Atualizando o estado 'item' com os dados recebidos
        setItem(data);
      } catch (error) {
        // Imprimindo qualquer erro no console
        console.error("Erro ao buscar item:", error);
      }
    };

    // Chamando a função para buscar o item
    fetchItem();
  }, [id]); // Dependência no 'id': este efeito rodará novamente se o valor de 'id' mudar na URL

  // Renderiza uma mensagem de carregamento enquanto o item está sendo buscado
  if (!item) {
    return <p>Carregando detalhes do item...</p>;
  }

  // Renderiza os detalhes do item quando ele é carregado
  return (
    <div>
      <h2>Detalhes do Item</h2>
      <p><strong>ID:</strong> {item.id}</p>
      <p><strong>Categoria:</strong> {item.categoria}</p>
      <p><strong>Descrição:</strong> {item.descricao}</p>
      <p><strong>Unidade:</strong> {item.unidade}</p>
      <p><strong>Preço:</strong> R$ {item.preco.toFixed(2)}</p>
      {/* Aqui você pode adicionar mais detalhes do item se necessário */}
    </div>
  );
}

export default ItemDetail;