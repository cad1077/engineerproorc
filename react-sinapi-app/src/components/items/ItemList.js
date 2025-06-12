// src/components/items/ItemList.js
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function ItemList() {
  const [items, setItems] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState(''); // Novo estado para a categoria selecionada
  const apiUrl = 'http://localhost:8000';

  const categories = ["", "Serviço", "Insumo"]; // Adicione aqui as categorias que você quer exibir

  const handleCategoryChange = (event) => {
    setSelectedCategory(event.target.value);
  };

  useEffect(() => {
    const fetchItems = async () => {
      let url = `${apiUrl}/items`;
      if (selectedCategory) {
        url = `${apiUrl}/items/categoria/${selectedCategory}`;
      }

      try {
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setItems(data);
        // Log dos IDs dos primeiros itens recebidos
        if (data && data.length > 0) {
          console.log("IDs dos primeiros itens recebidos:", data.slice(0, 5).map(item => item.id));
        }
      } catch (error) {
        console.error("Erro ao buscar itens:", error);
      }
    };

    fetchItems();
  }, [selectedCategory]); // O efeito roda novamente quando 'selectedCategory' muda

  return (
    <div>
      <h2>Lista de Serviços e Insumos</h2>
      <div>
        <label htmlFor="category">Filtrar por Categoria: </label>
        <select id="category" value={selectedCategory} onChange={handleCategoryChange}>
          {categories.map(category => (
            <option key={category} value={category}>{category === "" ? "Todas" : category}</option>
          ))}
        </select>
      </div>
      {items.length > 0 ? (
        <ul>
          {items.map(item => (
            <li key={item.id}>
              <Link to={`/items/${item.id}`}>{item.descricao} - {item.unidade} - R$ {item.preco.toFixed(2)}</Link>
            </li>
          ))}
        </ul>
      ) : (
        <p>Carregando itens...</p>
      )}
    </div>
  );
}

export default ItemList;