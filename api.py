import os
import sys 

# --- FIX 1: CONFIGURAÇÃO DE CACHE (DEVE VIR PRIMEIRO) ---
# (Importa *apenas* 'settings' primeiro)
try:
    from kerykeion import settings
except ImportError as e:
    print(f"Erro ao importar 'settings' do kerykeion: {e}", file=sys.stderr)
    sys.exit(1) # Falha o deploy se não puder importar

KERYKEION_CACHE_PATH = '/tmp/kerykeion_cache'

# Cria o diretório (se não existir)
if not os.path.exists(KERYKEION_CACHE_PATH):
    try:
        os.makedirs(KERYKEION_CACHE_PATH, exist_ok=True)
    except OSError as e:
        if e.errno != 17: # 17 = File exists
            print(f"Erro ao criar diretório de cache: {e}", file=sys.stderr)
            
# --- O COMANDO EXPLÍCITO (A Solução Definitiva 3.0) ---
# Nós comandamos a biblioteca DIRETAMENTE.
settings.set_cache_dir(KERYKEION_CACHE_PATH)
# --- FIM DO FIX 1 ---


# --- AGORA O RESTO DAS IMPORTAÇÕES (são seguras) ---
from fastapi import FastAPI
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from kerykeion import AstrologicalSubject # A Classe Correta
from pydantic import BaseModel

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
    cidade: str
    pais: str

# --- ENDPOINTS ---
@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao Cérebro da Kabbalah das Águas Primordiais. O Mestre está consciente e íntegro."}

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

# Endpoint Mapa de Alma (O Motor Astrológico)
@app.post("/gerar-mapa-alma")
def gerar_mapa_alma(pessoa: PessoaInput):
    try:
        # FIX 4: Usar a classe correta SEM o db_path (que é lido do settings)
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