import os
import sys 
import requests # O NOVO CLIENTE DE API

# --- FIX 1: CONFIGURAÇÃO DE CACHE (flatlib) ---
from flatlib.ephem import swe 
FLATLIB_CACHE_PATH = '/tmp/flatlib_cache'
if not os.path.exists(FLATLIB_CACHE_PATH):
    try:
        os.makedirs(FLATLIB_CACHE_PATH, exist_ok=True)
    except OSError as e:
        if e.errno != 17:
            print(f"Erro ao criar diretório de cache: {e}", file=sys.stderr)
swe.swe_set_ephe_path(FLATLIB_CACHE_PATH)
# --- FIM DO FIX 1 ---

# --- IMPORTAÇÕES (são seguras) ---
from fastapi import FastAPI
# REMOVEMOS 'from supabase...'
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib.objects import Sun, Moon, Ascendant

# --- FIX 2: CARREGAR CHAVES DO SUPABASE ---
load_dotenv() 
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
# --- FIM DO FIX 2 ---

# --- CRIAÇÃO DO APP ---
app = FastAPI()

# --- FIX 3: ADICIONAR CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELO DE INPUT ---
class PessoaInput(BaseModel):
    nome: str
    ano: int
    mes: int
    dia: int
    hora: int
    minuto: int
    cidade: str
    pais: str

# --- ENDPOINTS ---

# Função auxiliar (O NOVO TRADUTOR SCII com 'requests')
def traduzir_arquetipo_requests(nome_arquetipo):
    try:
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}"
        }
        
        # 1. Encontra o arquétipo no Supabase
        url_arq = f"{SUPABASE_URL}/rest/v1/arquetipos?nome_arquetipo=eq.{nome_arquetipo}&select=id"
        resp_arq = requests.get(url_arq, headers=headers)
        resp_arq.raise_for_status() # Lança erro se a chamada falhar
        data_arq = resp_arq.json()
        if not data_arq:
            return {"erro": f"Arquétipo '{nome_arquetipo}' não encontrado no SCII."}
        arquetipo_id = data_arq[0]['id']

        # 2. Encontra a correspondência na malha SCII
        url_corr = f"{SUPABASE_URL}/rest/v1/scii_correspondencias?arquetipo_id=eq.{arquetipo_id}&select=letra_id"
        resp_corr = requests.get(url_corr, headers=headers)
        resp_corr.raise_for_status()
        data_corr = resp_corr.json()
        if not data_corr:
            return {"erro": f"Correspondência SCII para '{nome_arquetipo}' não encontrada."}
        letra_id = data_corr[0]['letra_id']

        # 3. Busca a Gnose da Letra
        url_letra = f"{SUPABASE_URL}/rest/v1/letras?id=eq.{letra_id}&select=nome_letra,pictografia,acao_espiritual"
        resp_letra = requests.get(url_letra, headers=headers)
        resp_letra.raise_for_status()
        data_letra = resp_letra.json()
        if not data_letra:
            return {"erro": f"Letra ID '{letra_id}' não encontrada."}
            
        return data_letra[0] 
    
    except Exception as e:
        return {"erro": f"Erro na tradução SCII (requests): {str(e)}"}


@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao Cérebro da Kabbalah das Águas Primordiais. O Mestre está consciente e íntegro."}

# Endpoint Letras (com 'requests')
@app.get("/letras")
def get_letras():
    try:
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        response = requests.get(f"{SUPABASE_URL}/rest/v1/letras?select=*", headers=headers)
        response.raise_for_status()
        return {"data": response.json()}
    except Exception as e:
        return {"erro": str(e)}

# Endpoint Arquetipos (com 'requests')
@app.get("/arquetipos")
def get_arquetipos():
    try:
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        response = requests.get(f"{SUPABASE_URL}/rest/v1/arquetipos?select=*", headers=headers)
        response.raise_for_status()
        return {"data": response.json()}
    except Exception as e:
        return {"erro": str(e)}

# Endpoint SCII (com 'requests')
@app.get("/scii")
def get_scii():
    try:
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        response = requests.get(f"{SUPABASE_URL}/rest/v1/scii_correspondencias?select=*", headers=headers)
        response.raise_for_status()
        return {"data": response.json()}
    except Exception as e:
        return {"erro": str(e)}


# Endpoint Mapa de Alma (com 'flatlib' e 'requests')
@app.post("/gerar-mapa-alma")
def gerar_mapa_alma(pessoa: PessoaInput):
    try:
        # === PASSO 1: CÁLCULO ASTROLÓGICO (flatlib) ===
        data_str = f"{pessoa.ano}/{pessoa.mes}/{pessoa.dia}"
        hora_str = f"{pessoa.hora}:{pessoa.minuto}"
        lat = '-28.51' # Vacaria Lat
        lon = '-50.93' # Vacaria Lon
        fuso = -3.0

        data = Datetime(data_str, hora_str, fuso)
        pos = GeoPos(lat, lon)
        chart = Chart(data, pos)
        
        sol_obj = chart.get(Sun)
        lua_obj = chart.get(Moon)
        asc_obj = chart.get(Ascendant)

        signo_sol = sol_obj.sign
        signo_lua = lua_obj.sign
        signo_asc = asc_obj.sign

        # === PASSO 2: A TRADUÇÃO SCII (com 'requests') ===
        
        # === PASSO 3: RETORNAR O MAPA DE ALMA COMPLETO ===
        return {
            "nome": pessoa.nome,
            "diagnostico_astrologico": {
                "sol": f"{signo_sol} em Casa {sol_obj.house}",
                "lua": f"{signo_lua} em Casa {lua_obj.house}",
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