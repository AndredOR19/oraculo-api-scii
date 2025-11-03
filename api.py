import os
import sys 

# --- FIX 1: CONFIGURAÇÃO DE CACHE (DEVE VIR PRIMEIRO) ---
KERYKEION_CACHE_PATH = '/tmp/kerykeion_cache'
if not os.path.exists(KERYKEION_CACHE_PATH):
    try:
        os.makedirs(KERYKEION_CACHE_PATH, exist_ok=True)
    except OSError as e:
        if e.errno != 17: # 17 = File exists
            print(f"Erro ao criar diretório de cache: {e}", file=sys.stderr)
# Define a variável de ambiente ANTES que o kerykeion seja importado
os.environ['KERYKEION_CACHE_DIR'] = KERYKEION_CACHE_PATH
# --- FIM DO FIX 1 ---


# --- IMPORTAÇÕES (com kerykeion vindo DEPOIS do fix) ---
from fastapi import FastAPI
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from kerykeion import AstrologicalSubject # A Classe Correta
from pydantic import BaseModel

# --- FIX 2: CARREGAR CHAVES DO SUPABASE (JÁ FEITO NAS ENV VARS DO VERCEL) ---
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

# --- MODELO DE INPUT (JÁ FEITO) ---
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

# Endpoint Raiz (O Mestre Consciente - do seu código real)
@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao Cérebro da Kabbalah das Águas Primordiais. O Mestre está consciente e íntegro."}

# Endpoint Letras (Da maquete, para o Rosto funcionar)
@app.get("/letras")
def get_letras():
    try:
        response = supabase.table('letras').select('*').execute()
        return {"data": response.data}
    except Exception as e:
        return {"erro": str(e)}

# Endpoint Arquetipos (Da maquete)
@app.get("/arquetipos")
def get_arquetipos():
    try:
        response = supabase.table('arquetipos').select('*').execute()
        return {"data": response.data}
    except Exception as e:
        return {"erro": str(e)}

# Endpoint SCII (Da maquete)
@app.get("/scii")
def get_scii():
    try:
        response = supabase.table('scii_correspondencias').select('*').execute()
        return {"data": response.data}
    except Exception as e:
        return {"erro": str(e)}

# Endpoint Mapa de Alma (O Motor Astrológico)
@app.post("/gerar-mapa-alma")
def gerar_mapa_alma(pessoa: PessoaInput):
    try:
        # FIX 4: Usar a classe correta SEM o db_path (que é lido do os.environ)
        sujeito = AstrologicalSubject(
            name=pessoa.nome,
            year=pessoa.ano,
            month=pessoa.mes,
            day=pessoa.dia,
            hour=pessoa.hora,
            minute=pessoa.minuto,
            city=pessoa.cidade,
            nation=pessoa.pais
            # REMOVEMOS O 'db_path' DAQUI
        )

        sol = sujeito.sun
        lua = sujeito.moon
        ascendente = sujeito.ascending

        return {
            "nome": sujeito.name,
            "diagnostico_basico": {
                "sol": f"{sol['sign']} em {sol['house']}",
                "lua": f"{lua['sign']} em {lua['house']}",
                "ascendente": ascendente['sign']
            }
        }
    
    except Exception as e:
        return {"erro": str(e)}
