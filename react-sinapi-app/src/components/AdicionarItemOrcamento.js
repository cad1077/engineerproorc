// src/components/AdicionarItemOrcamento.js
import React, { useState, useEffect } from 'react';

function AdicionarItemOrcamento({ onAdicionarItem }) {
  const [descricao, setDescricao] = useState('');
  const [quantidade, setQuantidade] = useState(1);
  const [sugestoes, setSugestoes] = useState([]);
  const [todosItensSinapi, setTodosItensSinapi] = useState([]);
  const apiUrl = 'http://localhost:8000';
  const [itemSelecionado, setItemSelected] = useState(null); // Para armazenar o item SINAPI selecionado

  useEffect(() => {
    const fetchTodosItens = async () => {
      try {
        const response = await fetch(`${apiUrl}/items`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setTodosItensSinapi(data);
      } catch (error) {
        console.error("Erro ao buscar itens do SINAPI:", error);
      }
    };

    fetchTodosItens();
  }, []);

  const handleDescricaoChange = (event) => {
    console.log("handleDescricaoChange foi chamada!"); // Adicione esta linha
    const value = event.target.value;
    setDescricao(value);
    setItemSelecionado(null); // Limpa o item selecionado ao digitar

    if (value.length >= 3) {
      const filteredSugestoes = todosItensSinapi.filter(
        item => item.descricao.toLowerCase().includes(value.toLowerCase())
      );
      setSugestoes(filteredSugestoes.slice(0, 50)); // Mostrar no máximo 50 sugestões
    } else {
      setSugestoes([]);
    }
  };

  const handleQuantidadeChange = (event) => {
    setQuantidade(parseInt(event.target.value, 10) || 1);
  };

  const handleAdicionarClick = () => {
    if (itemSelecionado) {
      if (onAdicionarItem) {
        const newItem = { quantidade };
        if (itemSelecionado.tipo === 'mao_de_obra' && itemSelecionado.codigo_da_composicao) {
          newItem.codigo_da_composicao = itemSelecionado.codigo_da_composicao;
          newItem.descricao = itemSelecionado.descricao;
          newItem.unidade = itemSelecionado.unidade;
        } else {
          newItem.id = itemSelecionado.id;
        }
        console.log("Item selecionado ao adicionar:", itemSelecionado);
        console.log("Novo item a ser adicionado:", newItem);
        onAdicionarItem(newItem);
        setDescricao('');
        setQuantidade(1);
        setSugestoes([]);
        setItemSelecionado(null);
      }
    } else {
      alert("Por favor, selecione um item da lista de sugestões.");
    }
  };

  const selecionarSugestao = (item) => {
    setDescricao(item.descricao);
    setSugestoes([]);
    setItemSelecionado(item); // Armazena o item SINAPI selecionado
    console.log("Item selecionado:", item);
  };

  return (
    <div>
      <h3>Adicionar Item ao Orçamento</h3>
      <div>
        <label htmlFor="descricao">Descrição:</label>
        <input
          type="text"
          id="descricao"
          value={descricao}
          onChange={handleDescricaoChange}
        />
        {sugestoes.length > 0 && (
          <ul>
            {sugestoes.map(item => (
              <li key={item.id} onClick={() => selecionarSugestao(item)}>
                {item.descricao} ({item.unidade})
              </li>
            ))}
          </ul>
        )}
      </div>
      <div>
        <label htmlFor="quantidade">Quantidade:</label>
        <input
          type="number"
          id="quantidade"
          value={quantidade}
          onChange={handleQuantidadeChange}
        />
      </div>
      <button onClick={handleAdicionarClick}>Adicionar</button>
    </div>
  );
}

export default AdicionarItemOrcamento;