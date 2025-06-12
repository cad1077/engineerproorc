// src/components/OrcamentoFinal.js
import React, { useState, useEffect, useRef } from 'react';
import { usePDF } from 'react-to-pdf';
import generatePDF from 'react-to-pdf'; // Import generatePDF
import AdicionarItemOrcamento from './AdicionarItemOrcamento';

function OrcamentoFinal() {
  const [orcamentoInsumos, setOrcamentoInsumos] = useState([]);
  const [totalInsumos, setTotalInsumos] = useState(0);
  const [orcamentoMaoDeObra, setOrcamentoMaoDeObra] = useState([]);
  const [totalMaoDeObra, setTotalMaoDeObra] = useState(0);
  const [totalOrcamento, setTotalOrcamento] = useState(0);
  const apiUrl = 'http://localhost:8000';
  const pdfRef = useRef(); // Use pdfRef here
  const [itensOrcamento, setItensOrcamento] = useState([]);
  const [ufSelecionada, setUfSelecionada] = useState(''); // Estado para a UF selecionada

  const handleAdicionarItem = (newItem) => {
    setItensOrcamento([...itensOrcamento, newItem]);
  };

  useEffect(() => {
    const carregarItensOrcamento = async () => {
      let totalGeral = 0;
      let totalInsumosCalculado = 0;
      let totalMaoDeObraCalculado = 0;
      const insumosDetalhados = [];
      const maoDeObraDetalhados = [];

      for (const itemSelecionado of itensOrcamento) {
        console.log("ID do item no OrcamentoFinal:", itemSelecionado.id); // Adicione esta linha
        try {
          const response = await fetch(`${apiUrl}/items/${itemSelecionado.id}?uf=${ufSelecionada}`);
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }
          const data = await response.json();
          const precoTotalItem = data.preco * itemSelecionado.quantidade;

          if (data.tipo === 'insumo') {
            totalInsumosCalculado += precoTotalItem;
            insumosDetalhados.push({ ...data, quantidade: itemSelecionado.quantidade, precoTotal: precoTotalItem });
          } else if (data.tipo === 'mao_de_obra') {
            totalMaoDeObraCalculado += precoTotalItem;
            maoDeObraDetalhados.push({ ...data, quantidade: itemSelecionado.quantidade, precoTotal: precoTotalItem });
          }
          totalGeral += precoTotalItem;
        } catch (error) {
          console.error("Erro ao buscar detalhes do item:", error);
        }
      }
      setOrcamentoInsumos(insumosDetalhados);
      setTotalInsumos(totalInsumosCalculado);
      setOrcamentoMaoDeObra(maoDeObraDetalhados);
      setTotalMaoDeObra(totalMaoDeObraCalculado);
      setTotalOrcamento(totalGeral);
    };

    if (itensOrcamento.length > 0) {
      carregarItensOrcamento();
    } else {
      setOrcamentoInsumos([]);
      setTotalInsumos(0);
      setOrcamentoMaoDeObra([]);
      setTotalMaoDeObra(0);
      setTotalOrcamento(0);
    }
  }, [itensOrcamento, ufSelecionada]);

  const handleGeneratePdf = () => {
    generatePDF(pdfRef.current, {
      filename: 'orcamento_sinapi.pdf',
      html2canvasOptions: { scale: 2 }, // Opcional: aumenta a qualidade do PDF
      jsPDFOptions: { unit: 'in', format: 'letter', orientation: 'portrait' }, // Opcional: configura o formato do PDF
    });
  };

  return (
    <div ref={pdfRef}> {/* Attach the ref here */}
      <h2>Orçamento Final</h2>
      <div>
        <label htmlFor="uf">Estado (UF): </label>
        <select id="uf" value={ufSelecionada} onChange={(e) => setUfSelecionada(e.target.value)}>
          <option value="">Selecione o Estado</option>
          <option value="AC">Acre</option>
          <option value="AL">Alagoas</option>
          <option value="AM">Amazonas</option>
          <option value="AP">Amapá</option>
          <option value="BA">Bahia</option>
          <option value="CE">Ceará</option>
          <option value="DF">Distrito Federal</option>
          <option value="ES">Espírito Santo</option>
          <option value="GO">Goiás</option>
          <option value="MA">Maranhão</option>
          <option value="MT">Mato Grosso</option>
          <option value="MS">Mato Grosso do Sul</option>
          <option value="MG">Minas Gerais</option>
          <option value="PA">Pará</option>
          <option value="PB">Paraíba</option>
          <option value="PR">Paraná</option>
          <option value="PE">Pernambuco</option>
          <option value="PI">Piauí</option>
          <option value="RJ">Rio de Janeiro</option>
          <option value="RN">Rio Grande do Norte</option>
          <option value="RS">Rio Grande do Sul</option>
          <option value="RO">Rondônia</option>
          <option value="RR">Roraima</option>
          <option value="SC">Santa Catarina</option>
          <option value="SP">São Paulo</option>
          <option value="SE">Sergipe</option>
          <option value="TO">Tocantins</option>
        </select>
      </div>
      <AdicionarItemOrcamento onAdicionarItem={handleAdicionarItem} />

      <h3>Insumos</h3>
      {orcamentoInsumos.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Descrição</th>
              <th>Unidade</th>
              <th>Preço Unitário</th>
              <th>Quantidade</th>
              <th>Preço Total</th>
            </tr>
          </thead>
          <tbody>
            {orcamentoInsumos.map(item => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>{item.descricao}</td>
                <td>{item.unidade}</td>
                <td>R$ {item.preco.toFixed(2)}</td>
                <td>{item.quantidade}</td>
                <td>R$ {item.precoTotal.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>Nenhum insumo adicionado.</p>
      )}
      <h4>Subtotal Insumos: R$ {totalInsumos.toFixed(2)}</h4>

      <h3>Mão de Obra</h3>
      {orcamentoMaoDeObra.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Descrição</th>
              <th>Unidade</th>
              <th>Preço Unitário</th>
              <th>Quantidade</th>
              <th>Preço Total</th>
            </tr>
          </thead>
          <tbody>
            {orcamentoMaoDeObra.map(item => (
              <tr key={item.id}>
                <td>{item.id}</td>
                <td>{item.descricao}</td>
                <td>{item.unidade}</td>
                <td>R$ {item.preco.toFixed(2)}</td>
                <td>{item.quantidade}</td>
                <td>R$ {item.precoTotal.toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>Nenhum serviço de mão de obra adicionado.</p>
      )}
      <h4>Subtotal Mão de Obra: R$ {totalMaoDeObra.toFixed(2)}</h4>

      <h3>Total do Orçamento: R$ {totalOrcamento.toFixed(2)}</h3>
      <button onClick={handleGeneratePdf}>Gerar PDF do Orçamento</button>
    </div>
  );
}

export default OrcamentoFinal;