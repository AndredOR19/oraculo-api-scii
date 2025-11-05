import os
from fastapi import FastAPI
from supabase import create_client, Client
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from kerykeion import KrInstance, MakeSvg

# --- FIX DE CACHE PARA KERYKEION ---
# Tentativa de forçar o cache para /tmp, um diretório gravável no Vercel
CACHE_DIR = "/tmp/kerykeion_cache"
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR, exist_ok=True)

os.environ['KERYKEION_CACHE_DIR'] = CACHE_DIR
os.environ['KERYKEION_DB_PATH'] = os.path.join(CACHE_DIR, 'kerykeion.db')

# Carrega as variáveis de ambiente
load_dotenv()
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Inicializa o Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Inicializa o FastAPI
app = FastAPI()

# Adiciona o middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo de entrada
class PessoaInput(BaseModel):
    nome: str
    ano: int
    mes: int
    dia: int
    hora: int
    minuto: int
    cidade: str
    pais: str

# Endpoints
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

@app.post("/gerar-mapa-alma")
def gerar_mapa_alma(pessoa: PessoaInput):
    try:
        # Instancia o KrInstance com os dados da pessoa
        cliente = KrInstance(
            pessoa.nome,
            pessoa.ano,
            pessoa.mes,
            pessoa.dia,
            pessoa.hora,
            pessoa.minuto,
            pessoa.cidade,
            pessoa.pais,
            db_path=os.environ['KERYKEION_DB_PATH'] # Força o uso do db_path
        )
        
        # Gera o mapa (exemplo, você pode querer outros dados)
        sol = cliente.sun
        lua = cliente.moon
        asc = cliente.ascendant

        return {
            "nome": cliente.name,
            "diagnostico_basico": {
                "sol": f"{sol['sign']} em {sol['house_name']}",
                "lua": f"{lua['sign']} em {lua['house_name']}",
                "ascendente": asc['sign']
            }
        }
    except Exception as e:
        # Retorna o erro específico para depuração
        return {"erro": str(e)}
