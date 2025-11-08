import os
import sys 

# --- FIX 1: CONFIGURAÇÃO DE CACHE (Para flatlib - O Comando Explícito) ---
try:
    # Importa o 'swe' (o motor suíço) diretamente
    from flatlib.ephem import swe 
except ImportError as e:
    print(f"Erro ao importar 'swe' do flatlib: {e}", file=sys.stderr)
    sys.exit(1)

FLATLIB_CACHE_PATH = '/tmp/flatlib_cache'

# Cria o diretório (se não existir)
if not os.path.exists(FLATLIB_CACHE_PATH):
    try:
        os.makedirs(FLATLIB_CACHE_PATH, exist_ok=True)
    except OSError as e:
        if e.errno != 17: # 17 = File exists
            print(f"Erro ao criar diretório de cache: {e}", file=sys.stderr)
            
# --- O COMANDO EXPLÍCITO (A Solução Definitiva 4.0) ---
# Nós comandamos a biblioteca DIRETAMENTE, usando o comando do log de erro.
# O 'os.environ' falhou; isto não vai falhar.
swe.swe_set_ephe_path(FLATLIB_CACHE_PATH)
# --- FIM DO FIX 1 ---


# --- AGORA O RESTO DAS IMPORTAÇÕES (são seguras) ---
from fastapi import FastAPI
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib.objects import Sun, Moon, Ascendant

# --- CARREGAR CHAVES ---
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- APP ---
app = FastAPI()

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

# --- ENDPOINTS ---
@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao Cérebro da Kabbalah das Águas Primordiais. O Mestre está consciente e íntegro."}

# Endpoint Mapa de Alma (O Motor Astrológico + A Fusão SCII)
@app.post("/gerar-mapa-alma")
def gerar_mapa_alma(pessoa: PessoaInput):
    try:
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

        # Nomes dos arquétipos que vamos procurar no Supabase
        signo_sol = sol_obj.sign
        signo_lua = lua_obj.sign
        signo_asc = asc_obj.sign

        # === PASSO 2: A TRADUÇÃO SCII (A Nova Magia) ===
        
        # Função auxiliar para "traduzir" um arquétipo (ex: "Capricórnio") na Gnose (Letra)
        def traduzir_arquetipo(nome_arquetipo):
            try:
                # 1. Encontra o arquétipo no Supabase
                arquetipo_resp = supabase.table('arquetipos').select('id').eq('nome_arquetipo', nome_arquetipo).execute()
                if not arquetipo_resp.data:
                    return {"erro": f"Arquétipo '{nome_arquetipo}' não encontrado no SCII."}
                
                arquetipo_id = arquetipo_resp.data[0]['id']

                # 2. Encontra a correspondência na malha SCII
                correspondencia_resp = supabase.table('scii_correspondencias').select('letra_id').eq('arquetipo_id', arquetipo_id).execute()
                if not correspondencia_resp.data:
                    return {"erro": f"Correspondência SCII para '{nome_arquetipo}' não encontrada."}
                
                letra_id = correspondencia_resp.data[0]['letra_id']

                # 3. Busca a Gnose da Letra
                letra_resp = supabase.table('letras').select('nome_letra, pictografia, acao_espiritual').eq('id', letra_id).execute()
                if not letra_resp.data:
                    return {"erro": f"Letra ID '{letra_id}' não encontrada."}
                    
                return letra_resp.data[0] # Retorna a Gnose (ex: {"nome_letra": "Ayin", ...})
            
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