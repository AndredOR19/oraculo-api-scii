# main.py - v3 - O Oráculo

from fastapi import FastAPI
from pydantic import BaseModel

# =============================================================================
# PARTE 1: NOSSO NOVO BANCO DE DADOS DE CONHECIMENTO
# Esta estrutura (um dicionário) guarda todo o conhecimento do Oráculo.
# Colocamos fora de qualquer função para que seja uma constante no nosso programa.
# Para adicionar conhecimento, basta adicionar novas entradas aqui.
# =============================================================================
BASE_DE_CONHECIMENTO_SCII = {
    "א": { "letra": "א", "nome": "Aleph", "correspondencias": { "elemento": "Ar", "corpo_somatico": "Peito / Pulmões", "conceito": "Vontade, Sopro Vital, Paradoxo" }},
    "ב": { "letra": "ב", "nome": "Bet", "correspondencias": { "planeta": "Mercúrio", "corpo_somatico": "Boca", "conceito": "Casa, Interioridade, Dualidade, Receptáculo" }},
    "ג": { "letra": "ג", "nome": "Gimel", "correspondencias": { "planeta": "Lua", "corpo_somatico": "Olho Direito", "conceito": "Movimento, Fluxo, Recompensa, Camelo" }},
    "ד": { "letra": "ד", "nome": "Dalet", "correspondencias": { "planeta": "Vênus", "corpo_somatico": "Olho Esquerdo", "conceito": "Porta, Abertura, Estrutura, Passagem" }},
    "ה": { "letra": "ה", "nome": "He", "correspondencias": { "signo": "Áries", "corpo_somatico": "Pé Direito", "conceito": "Sopro, Expressão, Janela, Revelação Divina" }},
    "ו": { "letra": "ו", "nome": "Vav", "correspondencias": { "signo": "Touro", "corpo_somatico": "Rim Direito", "conceito": "Conexão, Elo, Gancho, Continuidade" }},
    "ז": { "letra": "ז", "nome": "Zayin", "correspondencias": { "signo": "Gêmeos", "corpo_somatico": "Pé Esquerdo", "conceito": "Arma, Espada, Escolha, Discernimento" }},
    "ח": { "letra": "ח", "nome": "Chet", "correspondencias": { "signo": "Câncer", "corpo_somatico": "Mão Direita", "conceito": "Cerca, Barreira, Vida, Transcendência" }},
    "ט": { "letra": "ט", "nome": "Tet", "correspondencias": { "signo": "Leão", "corpo_somatico": "Rim Esquerdo", "conceito": "Serpente, Bem Oculto, Potencial, Introspecção" }},
    "י": { "letra": "י", "nome": "Yod", "correspondencias": { "signo": "Virgem", "corpo_somatico": "Mão Esquerda", "conceito": "Ponto, Semente, Mão, Potência Criadora" }},
    "כ": { "letra": "כ", "nome": "Kaf", "correspondencias": { "planeta": "Júpiter", "corpo_somatico": "Narina Direita", "conceito": "Palma da Mão, Realização, Submissão, Força" }},
    "ל": { "letra": "ל", "nome": "Lamed", "correspondencias": { "signo": "Libra", "corpo_somatico": "Vesícula Biliar", "conceito": "Aguilhão, Ensinar, Propósito, Coração" }},
    "מ": { "letra": "מ", "nome": "Mem", "correspondencias": { "elemento": "Água", "corpo_somatico": "Ventre / Abdômen", "conceito": "Intuição, Inconsciente, Oculto, Fonte" }},
    "נ": { "letra": "נ", "nome": "Nun", "correspondencias": { "signo": "Escorpião", "corpo_somatico": "Intestinos", "conceito": "Peixe, Movimento, Alma, Lealdade" }},
    "ס": { "letra": "ס", "nome": "Samekh", "correspondencias": { "signo": "Sagitário", "corpo_somatico": "Estômago", "conceito": "Apoio, Escora, Confiança, Círculo" }},
    "ע": { "letra": "ע", "nome": "Ayin", "correspondencias": { "signo": "Capricórnio", "corpo_somatico": "Fígado", "conceito": "Olho, Visão Interior, Percepção, Fonte" }},
    "פ": { "letra": "פ", "nome": "Pe", "correspondencias": { "planeta": "Marte", "corpo_somatico": "Narina Esquerda", "conceito": "Boca, Palavra, Comunicação, Expressão" }},
    "צ": { "letra": "צ", "nome": "Tsade", "correspondencias": { "signo": "Aquário", "corpo_somatico": "Esôfago", "conceito": "Anzol, Justiça, Retidão, Caça" }},
    "ק": { "letra": "ק", "nome": "Qof", "correspondencias": { "signo": "Peixes", "corpo_somatico": "Baço", "conceito": "Nuca, Fundo da Agulha, Santidade, Contato" }},
    "ר": { "letra": "ר", "nome": "Resh", "correspondencias": { "planeta": "Saturno", "corpo_somatico": "Ouvido Direito", "conceito": "Cabeça, Início, Pobreza, Escolha" }},
    "ש": { "letra": "ש", "nome": "Shin", "correspondencias": { "elemento": "Fogo", "corpo_somatico": "Cabeça / Cérebro", "conceito": "Poder, Ação Espiritual, Dente, Transformação" }},
    "ת": { "letra": "ת", "nome": "Tav", "correspondencias": { "planeta": "Sol", "corpo_somatico": "Ouvido Esquerdo", "conceito": "Marca, Selo, Verdade, Aliança, Conclusão" }}
}
# =============================================================================

class TextoParaAnalise(BaseModel):
    texto: str

app = FastAPI(
    title="API do Oráculo SCII",
    description="Uma API para processar textos e retornar análises oraculares baseadas na Kabbalah das Águas Primordiais.",
    version="0.1.0",
)

@app.get("/")
def ler_raiz():
    return {"mensagem": "Bem-vindo ao Oráculo SCII. Use o endpoint /docs para interagir."}


# =============================================================================
# PARTE 2: A FUNÇÃO DE ANÁLISE EVOLUÍDA
# Esta função agora usa o Banco de Dados para retornar significados.
# =============================================================================
@app.post("/analisar")
def analisar_texto(item: TextoParaAnalise):
    
    texto_recebido = item.texto
    
    # 1. Prepara uma lista vazia para guardar os resultados completos.
    letras_encontradas = []
    
    # 2. Faz um LOOP, não numa lista simples, mas nas chaves do nosso banco de dados.
    for letra, dados_da_letra in BASE_DE_CONHECIMENTO_SCII.items():
        # ...se a letra (a "chave", ex: "א") estiver no texto...
        if letra in texto_recebido:
            # ...adiciona todos os "dados_da_letra" (o dicionário completo) à nossa lista de resultados.
            letras_encontradas.append(dados_da_letra)

    # 3. Cria uma mensagem final dinâmica.
    if letras_encontradas:
        # Pega o nome de cada letra encontrada para criar uma lista de nomes.
        nomes_letras = [info['nome'] for info in letras_encontradas]
        mensagem = f"Análise concluída. Energias encontradas: {', '.join(nomes_letras)}."
    else:
        mensagem = "Análise concluída. Nenhuma das energias primordiais (א, מ, ש) foi detectada."

    # 4. Monta a resposta final no novo formato.
    analise_scii = {
        "letras_presentes": letras_encontradas, # A nossa lista de resultados
        "mensagem": mensagem
    }
    
    return {
        "status": "sucesso",
        "texto_original": texto_recebido,
        "analise_scii": analise_scii
    }