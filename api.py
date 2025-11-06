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
        # --- TESTE: Retornando os dados de entrada para verificar se o endpoint funciona ---
        return {
            "message": "Teste bem-sucedido! O endpoint foi alcançado.",
            "dados_recebidos": pessoa.dict()
        }
    except Exception as e:
        return {"erro": str(e)}