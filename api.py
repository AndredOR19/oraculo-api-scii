import os
import sys 

# --- FIX 1: CONFIGURAÇÃO DE CACHE (Para o NOVO motor: flatlib) ---
# O flatlib usa a variável 'FLATLIB_EPHEMERIS_DIR'
FLATLIB_CACHE_PATH = '/tmp/flatlib_cache'
if not os.path.exists(FLATLIB_CACHE_PATH):
    try:
        os.makedirs(FLATLIB_CACHE_PATH, exist_ok=True)
    except OSError as e:
        if e.errno != 17:
            print(f"Erro ao criar diretório de cache: {e}", file=sys.stderr)
            
# Define a variável de ambiente ANTES que o flatlib seja importado
os.environ['FLATLIB_EPHEMERIS_DIR'] = FLATLIB_CACHE_PATH
# --- FIM DO FIX 1 ---


# --- AGORA O RESTO DAS IMPORTAÇÕES (são seguras) ---
from fastapi import FastAPI
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- IMPORTAÇÕES DO NOVO MOTOR (flatlib) ---
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from flatlib.chart import Chart
from flatlib.objects import Sun, Moon, Ascendant

# --- FIX 2: CARREGAR CHAVES DO SUPABASE ---
load_dotenv() 
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
    cidade: str # Flatlib não usa cidade/país, mas sim lat/lon. Deixamos por enquanto.
    pais: str

# --- ENDPOINTS ---
@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao Cérebro da Kabbalah das Águas Primordiais. O Mestre está consciente e íntegro."}

# (Os endpoints /letras, /arquetipos, /scii permanecem aqui)
@app.get("/letras")
def get_letras():
    try:
        response = supabase.table('letras').select('*').execute()
        return {"data": response.data}
    except Exception as e:
        return {"erro": str(e)}

@app.get("/arquetipos")
def get_arquetipos():
    try:
        response = supabase.table('arquetipos').select('*').execute()
        return {"data": response.data}
    except Exception as e:
        return {"erro": str(e)}

@app.get("/scii")
def get_scii():
    try:
        response = supabase.table('scii_correspondencias').select('*').execute()
        return {"data": response.data}
    except Exception as e:
        return {"erro": str(e)}


# --- Endpoint Mapa de Alma (com o NOVO MOTOR: flatlib) ---
# NOTA: Flatlib requer Latitude/Longitude. Vacaria/Brazil = Aprox. -28.51, -50.93
# O Kerykeion fazia isso automaticamente (o aviso do 'Geonames').
# Vamos "chumbar" (hardcode) a lat/lon de Vacaria por enquanto para provar que funciona.
@app.post("/gerar-mapa-alma")
def gerar_mapa_alma(pessoa: PessoaInput):
    try:
        # 1. Configurar os dados de entrada para o flatlib
        # (Formato: 'YYYY/MM/DD', 'HH:MM')
        data_str = f"{pessoa.ano}/{pessoa.mes}/{pessoa.dia}"
        hora_str = f"{pessoa.hora}:{pessoa.minuto}"
        
        # TODO: Precisamos de um geolocalizador. Por agora, usamos Vacaria.
        lat = '-28.51' # Latitude de Vacaria
        lon = '-50.93' # Longitude de Vacaria
        # O Kerykeion calculava o fuso. Vamos assumir -3 (Brazil/Vacaria)
        fuso = -3.0

        data = Datetime(data_str, hora_str, fuso)
        pos = GeoPos(lat, lon)
        
        # 2. Gerar o mapa
        chart = Chart(data, pos)

        # 3. Obter os dados (o flatlib chama de 'objects')
        sol = chart.get(Sun)
        lua = chart.get(Moon)
        asc = chart.get(Ascendant)

        # 4. Retorna o diagnóstico
        return {
            "nome": pessoa.nome,
            "diagnostico_basico": {
                "sol": f"{sol.sign} em Casa {sol.house}",
                "lua": f"{lua.sign} em Casa {lua.house}",
                "ascendente": asc.sign
            }
        }
    
    except Exception as e:
        return {"erro": str(e)}