import os
import sys 
import requests

# --- FIX 1: CONFIGURAÇÃO DE CACHE DO KERYKEION ---
# (Isso resolve o erro [Errno 30] Read-only file system)
KERYKEION_CACHE_PATH = '/tmp/kerykeion_cache'
if not os.path.exists(KERYKEION_CACHE_PATH):
    try:
        os.makedirs(KERYKEION_CACHE_PATH, exist_ok=True)
    except OSError as e:
        if e.errno != 17:
            print(f"Erro ao criar diretório de cache: {e}", file=sys.stderr)

# Define as variáveis ANTES de importar a biblioteca
os.environ['KERYKEION_CACHE_DIR'] = KERYKEION_CACHE_PATH
os.environ['KERYKEION_DB_PATH'] = KERYKEION_CACHE_PATH
# --- FIM DO FIX 1 ---

from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from kerykeion import AstrologicalSubject # O motor que funcionava

# --- FIX 2: CARREGAR CHAVES ---
load_dotenv() 
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

app = FastAPI()

# --- FIX 3: CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PessoaInput(BaseModel):
    nome: str
    ano: int
    mes: int
    dia: int
    hora: int
    minuto: int
    cidade: str
    pais: str

# Função auxiliar de Tradução (usando requests para evitar bugs de pool)
def traduzir_arquetipo_requests(nome_arquetipo):
    try:
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        
        # Busca o arquétipo
        url_arq = f"{SUPABASE_URL}/rest/v1/arquetipos"
        # Usamos 'params' para evitar erros de acento (Ex: Leão)
        params_arq = {'nome_arquetipo': f'eq.{nome_arquetipo}', 'select': 'id'}
        
        resp_arq = requests.get(url_arq, headers=headers, params=params_arq)
        resp_arq.raise_for_status()
        data_arq = resp_arq.json()
        
        if not data_arq:
            return {"erro": f"Arquétipo '{nome_arquetipo}' não encontrado no SCII."}
        arquetipo_id = data_arq[0]['id']

        # Busca a correspondência
        url_corr = f"{SUPABASE_URL}/rest/v1/scii_correspondencias"
        params_corr = {'arquetipo_id': f'eq.{arquetipo_id}', 'select': 'letra_id'}
        
        resp_corr = requests.get(url_corr, headers=headers, params=params_corr)
        resp_corr.raise_for_status()
        data_corr = resp_corr.json()
        
        if not data_corr:
            return {"erro": f"Correspondência SCII não encontrada."}
        letra_id = data_corr[0]['letra_id']

        # Busca a Letra
        url_letra = f"{SUPABASE_URL}/rest/v1/letras"
        params_letra = {'id': f'eq.{letra_id}', 'select': 'nome_letra,pictografia,acao_espiritual'}
        
        resp_letra = requests.get(url_letra, headers=headers, params=params_letra)
        resp_letra.raise_for_status()
        data_letra = resp_letra.json()
        
        if not data_letra:
            return {"erro": f"Letra ID '{letra_id}' não encontrada."}
            
        return data_letra[0] 
    
    except Exception as e:
        return {"erro": f"Erro na tradução SCII: {str(e)}"}

@app.get("/")
def read_root():
    return {"message": "O Mestre Kerykeion está online."}

@app.post("/gerar-mapa-alma")
def gerar_mapa_alma(pessoa: PessoaInput):
    try:
        # Motor Kerykeion (Simples e Funcional)
        sujeito = AstrologicalSubject(
            name=pessoa.nome,
            year=pessoa.ano,
            month=pessoa.mes,
            day=pessoa.dia,
            hour=pessoa.hora,
            minute=pessoa.minuto,
            city=pessoa.cidade,
            nation=pessoa.pais
        )

        # Pega os dados
        signo_sol = sujeito.sun['sign']
        signo_lua = sujeito.moon['sign']
        signo_asc = sujeito.first_house['sign']

        return {
            "nome": pessoa.nome,
            "diagnostico_astrologico": {
                "sol": f"{signo_sol} em Casa {sujeito.sun['house']}",
                "lua": f"{signo_lua} em Casa {sujeito.moon['house']}",
                "ascendente": signo_asc
            },
            "diagnostico_scii_gnose": {
                "sol_letra": traduzir_arquetipo_requests(signo_sol),
                "lua_letra": traduzir_arquetipo_requests(signo_lua),
                "ascendente_letra": traduzir_arquetipo_requests(signo_asc)
            }
        }
    
    except Exception as e:
        return {"erro": str(e)}