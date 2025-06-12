const apiUrl = 'http://localhost:8000'; // Certifique-se de que a porta corresponde à sua API FastAPI

export const fetchComposicoes = async () => {
  try {
    const response = await fetch(`${apiUrl}/composicoes`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Erro ao buscar composições:", error);
    return {}; // Retorna um objeto vazio em caso de erro
  }
};