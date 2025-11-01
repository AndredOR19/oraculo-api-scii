# main.py - Versão 2.0 - Restauração Completa do Mestre

import json
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any

# --- Modelos de Dados Pydantic (A Base da nossa Comunicação) ---

class GematriaInput(BaseModel):
    palavra: str

class TiragemInput(BaseModel):
    cartas: List[str]

class MeditacaoInput(BaseModel):
    letra: str

class AcertoInput(BaseModel):
    queixa_analisada: str
    letras_identificadas: List[str]
    diagnostico_sintetizado: str

class QueixaInput(BaseModel):
    queixa: str

class SessaoInput(BaseModel):
    user_id: str
    session_id: str | None = None
    mensagem: str

# --- Inicialização da API (O Nascimento da Consciência) ---

app = FastAPI(
    title="Cérebro da Kabbalah das Águas Primordiais",
    description="Uma API para fornecer insights, diagnósticos e guia terapêutico-arquetípico.",
    version="2.0.0" # Versão Restaurada e Completa
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite que QUALQUER site acesse sua API
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)

# --- Carregamento da Memória (O Conhecimento Primordial) ---

def carregar_db():
    with open("scii_database.json", "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_db(data):
    with open("scii_database.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

scii_data = carregar_db()

# --- Mapas Pré-calculados para Eficiência (A Intuição Rápida) ---

letras_data = scii_data.get("letras", {})
regras_diagnostico = scii_data.get("regras_diagnostico", [])
memoria_ativa = scii_data.get("memoria_ativa", [])
TAROT_MAP = {info.get("tarot"): info for info in letras_data.values() if info.get("tarot")}
TRANSLITERATION_MAP = {
    'a': 'Aleph', 'b': 'Bet', 'g': 'Gimel', 'd': 'Dalet',
    'h': 'He', 'v': 'Vav', 'u': 'Vav', 'w': 'Vav', 'z': 'Zayin',
    'ch': 'Het', 't': 'Tet', 'i': 'Yod', 'y': 'Yod', 'j': 'Yod',
    'k': 'Kaf', 'q': 'Kof', 'c': 'Samekh', 'l': 'Lamed', 'm': 'Mem', 'n': 'Nun',
    's': 'Samekh', 'e': 'Ayin', 'o': 'Ayin', 'f': 'Peh', 'p': 'Peh',
    'ts': 'Tzadi', 'r': 'Resh', 'sh': 'Shin', 'x': 'Shin'
}

# --- Armazenamento de Sessões Ativas (A Memória de Curto Prazo) ---
sessoes_ativas: Dict[str, Any] = {}

# --- LÓGICA INTERNA (As Funções Cognitivas) ---

def analisar_queixa_interna(queixa: str):
    # Lógica para o Terapeuta
    letras_encontradas = set()
    for regra in regras_diagnostico:
        for palavra_chave in regra["palavras_chave"]:
            if palavra_chave in queixa.lower():
                letras_encontradas.add(regra["letra"])
    return list(letras_encontradas) if letras_encontradas else []

# --- ENDPOINTS DA API (As Formas de Interagir com o Mestre) ---

@app.get("/", tags=["Status"])
async def root():
    """Endpoint inicial da API."""
    return {"message": "Bem-vindo ao Cérebro da Kabbalah das Águas Primordiais. O Mestre está consciente e íntegro."}

@app.get("/scii/letra/{nome_letra}", tags=["Sistema SCII"])
async def get_letra_info(nome_letra: str, persona: str = "arquiteto"):
    """Retorna todas as informações e correspondências de uma letra hebraica específica."""
    letra_formatada = nome_letra.capitalize()
    letra_info = letras_data.get(letra_formatada)
    if not letra_info:
        raise HTTPException(status_code=404, detail=f"Letra '{nome_letra}' não encontrada.")

    if persona == "mestre":
        return {
            "persona": "mestre",
            "resposta": f"A letra {letra_info['nome_hebraico']} ({letra_info['caractere']}), de valor gemátrico {letra_info['valor_gematrico']}, é um pilar do sistema SCII. Seu pictograma original, '{letra_info['pictograma']}', ancora seu significado. Associada ao arcano '{letra_info['tarot']}', ela governa o '{letra_info['corpo_do_verbo']}' no Corpo do Verbo, e seu conceito chave é: {letra_info['conceito_chave']}"
        }
    
    if persona == "poeta":
        return {
            "persona": "poeta",
            "resposta": f"Contemple {letra_info['nome_hebraico']} ({letra_info['caractere']}), a face do indizível. Nascida como um(a) '{letra_info['pictograma']}', ela dança no corpo como os(as) '{letra_info['corpo_do_verbo']}'. No grande Oráculo, ela é a voz de '{letra_info['tarot']}'. Silencie-se e escute seu segredo: '{letra_info['conceito_chave'].split(',')[0]}'."
        }

    # O default é a persona "arquiteto"
    return letra_info

@app.get("/scii/corpo/{parte_do_corpo}", tags=["Sistema SCII"])
async def get_corpo_info(parte_do_corpo: str):
    """Busca a letra correspondente a uma parte do corpo."""
    for letra, info in letras_data.items():
        if parte_do_corpo.lower() in info.get("corpo_do_verbo", "").lower():
            return {"letra_encontrada": letra, "dados": info}
    raise HTTPException(status_code=404, detail=f"Nenhuma letra encontrada para a parte do corpo '{parte_do_corpo}'.")

@app.post("/analise/gematria", tags=["Análise"])
async def analisar_gematria(input: GematriaInput):
    """Calcula o valor gemátrico de uma palavra ou frase."""
    palavra = input.palavra.lower()
    valor_total = 0
    detalhamento = []
    for char in palavra:
        nome_letra_hebraica = TRANSLITERATION_MAP.get(char)
        if nome_letra_hebraica:
            info_letra = letras_data.get(nome_letra_hebraica)
            if info_letra:
                valor = info_letra.get("valor_gematrico", 0)
                valor_total += valor
                detalhamento.append({"letra_original": char, "letra_hebraica": nome_letra_hebraica, "valor": valor})
    return {"palavra_analisada": palavra, "valor_gematrico": valor_total, "detalhamento": detalhamento}

@app.post("/oraculo/interpretar_tiragem", tags=["Oráculo"])
async def interpretar_tiragem(input: TiragemInput):
    """Interpreta uma tiragem de Tarot baseada no sistema SCII."""
    detalhamento_cartas = []
    conceitos_gerais = []
    for carta in input.cartas:
        info_letra = TAROT_MAP.get(carta)
        if info_letra:
            conceito = info_letra.get("conceito_chave", "Conceito não encontrado.")
            detalhamento_cartas.append({"carta": carta, "letra_associada": info_letra.get("nome_hebraico"), "insight_scii": f'Representa {conceito} Associado ao {info_letra.get("corpo_do_verbo", "corpo")}.'})
            conceitos_gerais.append(conceito.split(',')[0])
    if not conceitos_gerais:
        raise HTTPException(status_code=404, detail="Nenhuma carta pôde ser interpretada.")
    interpretacao_geral = f"A sua jornada se desdobra através das seguintes forças: {' -> '.join(conceitos_gerais)}."
    return {"tiragem_analisada": input.cartas, "interpretacao_geral": interpretacao_geral, "detalhamento_cartas": detalhamento_cartas}

@app.post("/diagnostico/analisar_queixa", tags=["Oráculo"])
async def analisar_queixa(input: QueixaInput):
    # Lógica do Diagnóstico Dialético
    return {"detail": "Este endpoint foi evoluído para o /terapeuta/sessao para um diálogo mais profundo."} # Placeholder para a função completa que já temos no fluxo do terapeuta

@app.post("/mestre/gerar_meditacao_guiada", tags=["Mestre"])
async def gerar_meditacao(input: MeditacaoInput):
    letra = input.letra.capitalize()
    info_letra = letras_data.get(letra)
    if not info_letra:
        raise HTTPException(status_code=404, detail=f"Letra '{letra}' não encontrada.")
    # Lógica de geração de texto da Meditação
    texto_meditacao = f'''
**Meditação Guiada da Letra {letra} ({info_letra.get('caractere')}) - {info_letra.get('conceito_chave', '').split(',')[0]}**

*(Introdução)*
Encontre uma posição confortável... Hoje, vamos comungar com a letra {letra}.

*(Visualização e Conexão Corporal)*
Visualize a forma da letra {letra}. Leve essa consciência para {info_letra.get('corpo_do_verbo', 'seu corpo')}. Com cada inspiração, sinta {info_letra.get('funcao_corporal', 'sua energia')}...

*(Encerramento)*
Quando estiver pronto, abra os olhos, trazendo a essência de {letra} com você.'''
    return {"letra_meditada": letra, "meditacao_guiada": texto_meditacao}

@app.post("/diagnostico/confirmar_acerto", tags=["Mestre"])
async def confirmar_acerto(input: AcertoInput):
    # Lógica para registrar o aprendizado na Memória Ativa
    db_data = carregar_db()
    db_data["memoria_ativa"].append(input.dict())
    salvar_db(db_data)
    return {"status": "Aprendizado registrado com sucesso."}

@app.post("/terapeuta/sessao", tags=["Terapeuta Arquetípico"])
async def sessao_terapeutica(input: SessaoInput):
    """Ponto de entrada principal para interagir com o Terapeuta Arquetípico."""
    session_id = input.session_id
    if not session_id or session_id not in sessoes_ativas:
        session_id = str(uuid.uuid4())
        sessoes_ativas[session_id] = {"user_id": input.user_id, "estado": "ACOLHIMENTO", "historico": [], "hipotese": []}
        resposta = ("Bem-vindo. Sou o Terapeuta Arquetípico... Para começar, por favor, me diga o que o traz aqui hoje.")
        sessoes_ativas[session_id]["estado"] = "ABERTURA"
        return {"session_id": session_id, "resposta": resposta}
    
    sessao_atual = sessoes_ativas[session_id]
    estado_atual = sessao_atual["estado"]
    sessao_atual["historico"].append({"role": "user", "content": input.mensagem})

    if estado_atual == "ABERTURA":
        queixa = input.mensagem
        letras_hipotese = analisar_queixa_interna(queixa)
        sessao_atual["hipotese"] = letras_hipotese
        if letras_hipotese:
            primeira_letra = letras_hipotese[0]
            resposta = f"Entendo... A forma como você descreve sua questão me faz pensar sobre a energia de '{primeira_letra}'. Onde em seu corpo físico você sente o eco dessa sensação?"
        else:
            resposta = "Entendo. Pode me falar um pouco mais sobre essa sensação?"
        sessao_atual["estado"] = "EXPLORACAO_1"
        return {"session_id": session_id, "resposta": resposta}

    elif estado_atual == "EXPLORACAO_1":
        local_sensacao = input.mensagem
        resposta = f"Interessante você localizar a sensação em '{local_sensacao}'. E como é essa sensação? Se pudesse descrevê-la... é um peso, um vazio, um calor?"
        sessao_atual["estado"] = "EXPLORACAO_2"
        return {"session_id": session_id, "resposta": resposta}
        
    elif estado_atual == "EXPLORACAO_2":
        descricao_sensacao = input.mensagem
        resposta = f"A textura de '{descricao_sensacao}'... compreendo. (A partir daqui, o Terapeuta pode decidir intervir ou sintetizar). Nossa sessão se encerra por hoje."
        del sessoes_ativas[session_id]
        return {"session_id": session_id, "resposta": resposta, "status": "Sessão encerrada."}

    else:
        raise HTTPException(status_code=400, detail="Estado de sessão inválido.")
