import os
import sys 

# --- FIX 1: CONFIGURAÇÃO DE CACHE (DEVE VIR PRIMEIRO) ---
from flatlib.ephem import swe 
KERYKEION_CACHE_PATH = '/tmp/flatlib_cache'
if not os.path.exists(KERYKEION_CACHE_PATH):
    try:
        os.makedirs(KERYKEION_CACHE_PATH, exist_ok=True)
    except OSError as e:
        if e.errno != 17:
            print(f"Erro ao criar diretório de cache: {e}", file=sys.stderr)
swe.swe_set_ephe_path(KERYKEION_CACHE_PATH)
# --- FIM DO FIX 1 ---

# --- AGORA O RESTO DAS IMPORTAÇÕES (são seguras) ---
from fastapi import FastAPI
from supabase import create_client, Client # Importamos a Classe, mas não a usamos ainda
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
# --- REMOVEMOS A CRIAÇÃO DO CLIENTE GLOBAL DAQUI ---

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
@app.get("/")
def read_root():
    # Este endpoint não precisa de conexão, então não a criamos.
    return {"message": "Bem-vindo ao Cérebro da Kabbalah das Águas Primordiais. O Mestre está consciente e íntegro."}

# Endpoint Letras (Cria sua própria conexão)
@app.get("/letras")
def get_letras():
    try:
        # --- FIX 4 (SERVERLESS): Cria a conexão DENTRO da função ---
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.from_('letras').select('*').execute()
        return {"data": response.data}
    except Exception as e:
        return {"erro": str(e)}

# Endpoint Arquetipos (Cria sua própria conexão)
@app.get("/arquetipos")
def get_arquetipos():
    try:
        # --- FIX 4 (SERVERLESS): Cria a conexão DENTRO da função ---
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.from_('arquetipos').select('*').execute()
        return {"data": response.data}
    except Exception as e:
        return {"erro": str(e)}

# Endpoint SCII (Cria sua própria conexão)
@app.get("/scii")
def get_scii():
    try:
        # --- FIX 4 (SERVERLESS): Cria a conexão DENTRO da função ---
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = supabase.from_('scii_correspondencias').select('*').execute()
        return {"data": response.data}
    except Exception as e:
        return {"erro": str(e)}


# Endpoint Mapa de Alma (Cria sua própria conexão)
@app.post("/gerar-mapa-alma")
def gerar_mapa_alma(pessoa: PessoaInput):
    try:
        # --- FIX 4 (SERVERLESS): Cria a conexão DENTRO da função ---
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        # === PASSO 1: CÁLCULO ASTROLÓGICO (Como antes) ===
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

        # === PASSO 2: A TRADUÇÃO SCII (A Nova Magia) ===
        
        # Função auxiliar (ela usará o 'supabase' que acabamos de criar)
        def traduzir_arquetipo(nome_arquetipo):
            try:
                arquetipo_resp = supabase.from_('arquetipos').select('id').eq('nome_arquetipo', nome_arquetipo).execute()
                if not arquetipo_resp.data:
                    return {"erro": f"Arquétipo '{nome_arquetipo}' não encontrado no SCII."}
                
                arquetipo_id = arquetipo_resp.data[0]['id']

                correspondencia_resp = supabase.from_('scii_correspondencias').select('letra_id').eq('arquetipo_id', arquetipo_id).execute()
                if not correspondencia_resp.data:
                    return {"erro": f"Correspondência SCII para '{nome_arquetipo}' não encontrada."}
                
                letra_id = correspondencia_resp.data[0]['letra_id']

                letra_resp = supabase.from_('letras').select('nome_letra, pictografia, acao_espiritual').eq('id', letra_id).execute()
                if not letra_resp.data:
                    return {"erro": f"Letra ID '{letra_id}' não encontrada."}
                    
                return letra_resp.data[0] 
            
            except Exception as e:
                return {"erro": f"Erro na tradução SCII: {str(e)}"}

        # === PASSO 3: RETORNAR O MAPA DE ALMA COMPLETO ===
        return {
            "nome": pessoa.nome,
            "diagnostico_astrologico": {
                "sol": f"{signo_sol} em Casa {sol_obj.house}",
                "lua": f"{signo_lua} em Casa {lua_obj.house}",
                "ascendente": signo_asc
            },
            "diagnostico_scii_gnose": {
                "sol_letra": traduzir_arquetipo(signo_sol),
                "lua_letra": traduzir_arquetipo(signo_lua),
                "ascendente_letra": traduzir_arquetipo(signo_asc)
            }
        }
    
    except Exception as e:
        return {"erro": str(e)}
