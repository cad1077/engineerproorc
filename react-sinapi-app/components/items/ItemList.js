import React, { useState, useEffect } from 'react';

function ItemList() {
  const [items, setItems] = useState([]);
  const apiUrl = 'http://localhost:8000'; // Certifique-se de que a porta corresponde à sua API FastAPI

  useEffect(() => {
    fetch(`${apiUrl}/items`)
      .then(response => response.json())
      .then(data => setItems(data))
      .catch(error => console.error("Erro ao buscar itens:", error));
  }, []);

  return (
    <div>
      <h2>Lista de Serviços e Insumos</h2>
      {items.length > 0 ? (
        <ul>
          {items.map(item => (
            <li key={item.id}>{item.descricao} - {item.unidade} - R$ {item.preco.toFixed(2)}</li>
          ))}
        </ul>
      ) : (
        <p>Carregando itens...</p>
      )}
    </div>
  );
}

export default ItemList;