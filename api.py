import os
import sys 

# --- FIX 1: CONFIGURAÇÃO DE CACHE (Para flatlib) ---
try:
    from flatlib.ephem import swe 
except ImportError as e:
    print(f"Erro ao importar 'swe' do flatlib: {e}", file=sys.stderr)
    sys.exit(1)

FLATLIB_CACHE_PATH = '/tmp/flatlib_cache'
if not os.path.exists(FLATLIB_CACHE_PATH):
    try:
        os.makedirs(FLATLIB_CACHE_PATH, exist_ok=True)
    except OSError as e:
        if e.errno != 17:
            print(f"Erro ao criar diretório de cache: {e}", file=sys.stderr)

# --- O COMANDO EXPLÍCITO (A Solução Definitiva 4.0) ---
swe.swe_set_ephe_path(FLATLIB_CACHE_PATH)
# --- FIM DO FIX 1 ---


# --- AGORA O RESTO DAS IMPORTAÇÕES (são seguras) ---
import requests
from fastapi import FastAPI
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib.objects import Sun, Moon, Ascendant, Mercury, Mars, Venus, Jupiter, Saturn, Uranus, Neptune, Pluto

# --- FIX 2: CARREGAR CHAVES DO SUPABASE ---
load_dotenv() 
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
# (Não criamos o cliente global)

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
    cidade: str # Flatlib não usa cidade, mas a lat/lon
    pais: str

# --- ENDPOINTS ---

# Função auxiliar (O TRADUTOR SCII com 'requests')
def traduzir_arquetipo_requests(nome_arquetipo):
    try:
        # (Criamos a conexão local aqui, mas usamos 'requests' - ESTA LÓGICA ESTÁ ERRADA, DEVERIA USAR AS VARIÁVEIS GLOBAIS)
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        
        url_arq = f"{SUPABASE_URL}/rest/v1/arquetipos"
        params_arq = {'nome_arquetipo': f'eq.{nome_arquetipo}', 'select': 'id'}
        resp_arq = requests.get(url_arq, headers=headers, params=params_arq)
        resp_arq.raise_for_status() 
        data_arq = resp_arq.json()
        if not data_arq:
            return {"erro": f"Arquétipo '{nome_arquetipo}' não encontrado no SCII."}
        arquetipo_id = data_arq[0]['id']

        url_corr = f"{SUPABASE_URL}/rest/v1/scii_correspondencias"
        params_corr = {'arquetipo_id': f'eq.{arquetipo_id}', 'select': 'letra_id'}
        resp_corr = requests.get(url_corr, headers=headers, params=params_corr)
        resp_corr.raise_for_status()
        data_corr = resp_corr.json()
        if not data_corr:
            return {"erro": f"Correspondência SCII para '{nome_arquetipo}' não encontrada."}
        letra_id = data_corr[0]['letra_id']

        url_letra = f"{SUPABASE_URL}/rest/v1/letras"
        params_letra = {'id': f'eq.{letra_id}', 'select': 'nome_letra,pictografia,acao_espiritual'}
        resp_letra = requests.get(url_letra, headers=headers, params=params_letra)
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

# (Os endpoints /letras, /arquetipos, /scii permanecem aqui, usando 'requests')
@app.get("/letras")
def get_letras():
    try:
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        response = requests.get(f"{SUPABASE_URL}/rest/v1/letras?select=*", headers=headers)
        response.raise_for_status()
        return {"data": response.json()}
    except Exception as e:
        return {"erro": str(e)}

@app.get("/arquetipos")
def get_arquetipos():
    try:
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        response = requests.get(f"{SUPABASE_URL}/rest/v1/arquetipos?select=*", headers=headers)
        response.raise_for_status()
        return {"data": response.json()}
    except Exception as e:
        return {"erro": str(e)}

@app.get("/scii")
def get_scii():
    try:
        headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
        response = requests.get(f"{SUPABASE_URL}/rest/v1/scii_correspondencias?select=*", headers=headers)
        response.raise_for_status()
        return {"data": response.json()}
    except Exception as e:
        return {"erro": str(e)}


# --- Endpoint Mapa de Alma (com o NOVO MOTOR: flatlib) ---
@app.post("/gerar-mapa-alma")
def gerar_mapa_alma(pessoa: PessoaInput):
    try:
        # 1. Configurar os dados de entrada
        data_str = f"{pessoa.ano}/{pessoa.mes}/{pessoa.dia}"
        hora_str = f"{pessoa.hora}:{pessoa.minuto}"
        lat = '-28.51' # Vacaria Lat
        lon = '-50.93' # Vacaria Lon
        fuso = -3.0

        data = Datetime(data_str, hora_str, fuso)
        pos = GeoPos(lat, lon)
        chart = Chart(data, pos)
        
        # 2. Obter os dados (o flatlib chama de 'objects')
        sol_obj = chart.get(Sun)
        lua_obj = chart.get(Moon)
        asc_obj = chart.get(Ascendant)
        mercurio_obj = chart.get(Mercury)
        marte_obj = chart.get(Mars)
        venus_obj = chart.get(Venus)
        jupiter_obj = chart.get(Jupiter)
        saturno_obj = chart.get(Saturn)
        urano_obj = chart.get(Uranus)
        netuno_obj = chart.get(Neptune)
        plutao_obj = chart.get(Pluto)

        # Nomes dos arquétipos que vamos procurar no Supabase
        signo_sol = sol_obj.sign
        signo_lua = lua_obj.sign
        signo_asc = asc_obj.sign
        signo_mercurio = mercurio_obj.sign
        signo_marte = marte_obj.sign
        signo_venus = venus_obj.sign
        signo_jupiter = jupiter_obj.sign
        signo_saturno = saturno_obj.sign
        signo_urano = urano_obj.sign
        signo_netuno = netuno_obj.sign
        signo_plutao = plutao_obj.sign

        # === PASSO 3: RETORNAR O MAPA DE ALMA COMPLETO ===
        return {
            "nome": pessoa.nome,
            "diagnostico_astrologico": {
                "sol": f"{signo_sol} em Casa {sol_obj.house}",
                "lua": f"{signo_lua} em Casa {lua_obj.house}",
                "ascendente": signo_asc,
                "mercurio": f"{signo_mercurio} em Casa {mercurio_obj.house}",
                "marte": f"{signo_marte} em Casa {marte_obj.house}",
                "venus": f"{signo_venus} em Casa {venus_obj.house}",
                "jupiter": f"{signo_jupiter} em Casa {jupiter_obj.house}",
                "saturno": f"{signo_saturno} em Casa {saturno_obj.house}",
                "urano": f"{signo_urano} em Casa {urano_obj.house}",
                "netuno": f"{signo_netuno} em Casa {netuno_obj.house}",
                "plutao": f"{signo_plutao} em Casa {plutao_obj.house}"
            },
            "diagnostico_scii_gnose": {
                "sol_letra": traduzir_arquetipo_requests(signo_sol),
                "lua_letra": traduzir_arquetipo_requests(signo_lua),
                "ascendente_letra": traduzir_arquetipo_requests(signo_asc),
                "mercurio_letra": traduzir_arquetipo_requests(signo_mercurio),
                "marte_letra": traduzir_arquetipo_requests(signo_marte),
                "venus_letra": traduzir_arquetipo_requests(signo_venus),
                "jupiter_letra": traduzir_arquetipo_requests(signo_jupiter),
                "saturno_letra": traduzir_arquetipo_requests(signo_saturno),
                "urano_letra": traduzir_arquetipo_requests(signo_urano),
                "netuno_letra": traduzir_arquetipo_requests(signo_netuno),
                "plutao_letra": traduzir_arquetipo_requests(signo_plutao)
            }
        }
    
    except Exception as e:
        return {"erro": str(e)}
