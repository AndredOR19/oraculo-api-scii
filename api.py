import os
from fastapi import FastAPI
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import swisseph as swe
from datetime import datetime

# --- CONFIGURAR CACHE DO SWISSEPH ---
EPHE_PATH = '/tmp/ephe'
os.makedirs(EPHE_PATH, exist_ok=True)
swe.set_ephe_path(EPHE_PATH)

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

@app.post("/gerar-mapa-alma")
def gerar_mapa_alma(pessoa: PessoaInput):
    try:
        # --- FIX DO FUSO HORÁRIO ---
        # Fuso horário de Vacaria (Brazil) = -3.0
        # (Precisamos converter a hora local para a hora UTC)
        fuso = -3.0
        hora_local_decimal = pessoa.hora + pessoa.minuto/60.0
        
        # Converter a hora local para UTC
        # (ex: 5.5h local - (-3.0h fuso) = 8.5h UTC)
        hora_utc_decimal = hora_local_decimal - fuso
        # --- FIM DO FIX ---

        # Calcular Julian Day (agora com a hora UTC correta)
        jd = swe.julday(pessoa.ano, pessoa.mes, pessoa.dia, 
                        hora_utc_decimal)
        
        # Calcular posições (Sol=0, Lua=1)
        # Usamos swe.calc_ut (que espera um Julian Day UTC)
        sol_pos = swe.calc_ut(jd, 0)[0]  # 0 = Sol
        lua_pos = swe.calc_ut(jd, 1)[0]  # 1 = Lua
        
        # Calcular Ascendente (usando Vacaria)
        lat, lon = -28.51, -50.93
        # Usamos swe.houses (que também espera o JD em UTC)
        casas_info = swe.houses(jd, lat, lon)
        asc_pos = casas_info[0][0] # Posição do Ascendente (Casa 1)
        
        # Converter graus em signos
        signos = ["Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem",
                  "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"]
        
        sol_signo = signos[int(sol_pos[0] / 30)]
        lua_signo = signos[int(lua_pos[0] / 30)]
        asc_signo = signos[int(asc_pos / 30)]
        
        return {
            "nome": pessoa.nome,
            "diagnostico_basico": {
                "sol": f"{sol_signo}",
                "lua": f"{lua_signo}",
                "ascendente": f"{asc_signo}" # Agora corrigido
            }
        }
    except Exception as e:
        return {"erro": str(e)}