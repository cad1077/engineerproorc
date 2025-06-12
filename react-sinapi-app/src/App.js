// src/App.js
import React, { useEffect, useState, useRef } from "react";
import { fetchComposicoes } from "./api/composicoes";
import ItemList from './components/items/ItemList';
import ItemDetail from './components/items/ItemDetail';
import OrcamentoFinal from './components/OrcamentoFinal'; // Importe o componente OrcamentoFinal
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

const App = () => {
  const [composicoes, setComposicoes] = useState({});

  useEffect(() => {
    const loadData = async () => {
      const data = await fetchComposicoes();
      setComposicoes(data);
    };
    loadData();
  }, []);

  return (
    <Router>
      <div style={{ padding: "1rem" }}>
        <header>
          <h1>Orçamento SINAPI</h1>
          <nav>
            <ul>
              <li>
                <Link to="/items">Lista de Itens</Link>
              </li>
              <li>
                <Link to="/composicoes">Composições SINAPI</Link>
              </li>
              <li>
                <Link to="/orcamento">Orçamento Final</Link> {/* Novo link para o Orçamento Final */}
              </li>
            </ul>
          </nav>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<ItemList />} /> {/* Adicionada a rota para a página inicial */}
            <Route path="/items" element={<ItemList />} />
            <Route path="/items/:id" element={<ItemDetail />} />
            <Route path="/orcamento" element={<OrcamentoFinal />} />
            <Route path="/composicoes" element={
              <>
                <h2>Composições SINAPI</h2>
                <ul>
                  {Object.entries(composicoes).map(([codigo, comp]) => (
                    <li key={codigo}>
                      <strong>Família {codigo}</strong>
                      <ul>
                        {comp.itens.map((item, idx) => (
                          <li key={idx}>
                            {item.descricao_insumo} ({item.unidade}) - SP: {item.coeficientes?.SP || 'N/A'}
                          </li>
                        ))}
                      </ul>
                    </li>
                  ))}
                </ul>
              </>
            } />
          </Routes>
        </main>
      </div>
    </Router>
  );
};

export default App;