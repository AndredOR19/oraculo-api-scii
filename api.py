import os
import sys

# CRITICAL: Monkey-patch do pathlib ANTES de qualquer import
# Isso força TODOS os paths do Kerykeion para /tmp
import pathlib
_original_path_init = pathlib.Path.__init__

def _patched_path_init(self, *args, **kwargs):
    _original_path_init(self, *args, **kwargs)
    # Se o path contém 'cache' e aponta para /var/task, redireciona para /tmp
    if hasattr(self, '_str'):
        path_str = str(self)
        if 'cache' in path_str and path_str.startswith('/var/task'):
            object.__setattr__(self, '_str', path_str.replace('/var/task', '/tmp'))

pathlib.Path.__init__ = _patched_path_init

# Configurar variáveis de ambiente
os.environ['HOME'] = '/tmp'
os.environ['KERYKEION_CACHE_DIR'] = '/tmp/kerykeion_cache'
os.environ['KERYKEION_GEONAMES_USERNAME'] = 'demo'

# Criar diretório de cache
cache_dir = '/tmp/kerykeion_cache'
try:
    os.makedirs(cache_dir, exist_ok=True)
except:
    pass

# AGORA importar as bibliotecas
import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Importar Kerykeion COM o patch aplicado
from kerykeion import AstrologicalSubject

# Carregar variáveis de ambiente
load_dotenv() 
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# Criar app FastAPI
app = FastAPI()

# Configurar CORS
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

# Função para traduzir arquétipos
def traduzir_arquetipo_requests(nome_arquetipo):
    try:
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
        return {"erro": f"Erro na tradução SCII: {str(e)}"}

# Endpoints
@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao Cérebro da Kabbalah das Águas Primordiais. O Mestre está consciente e íntegro."}

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

@app.post("/gerar-mapa-alma")
def gerar_mapa_alma(pessoa: PessoaInput):
    try:
        # Criar o sujeito astrológico
        subject = AstrologicalSubject(
            pessoa.nome,
            pessoa.ano,
            pessoa.mes,
            pessoa.dia,
            pessoa.hora,
            pessoa.minuto,
            pessoa.cidade,
            pessoa.pais
        )
        
        # Extrair os signos
        signo_sol = subject.sun["sign"]
        signo_lua = subject.moon["sign"]
        signo_asc = subject.first_house["sign"]
        signo_mercurio = subject.mercury["sign"]
        signo_venus = subject.venus["sign"]
        signo_marte = subject.mars["sign"]
        signo_jupiter = subject.jupiter["sign"]
        signo_saturno = subject.saturn["sign"]
        signo_urano = subject.uranus["sign"]
        signo_netuno = subject.neptune["sign"]
        signo_plutao = subject.pluto["sign"]
        
        return {
            "nome": pessoa.nome,
            "diagnostico_astrologico": {
                "sol": f"{signo_sol} em Casa {subject.sun['house']}",
                "lua": f"{signo_lua} em Casa {subject.moon['house']}",
                "ascendente": signo_asc,
                "mercurio": f"{signo_mercurio} em Casa {subject.mercury['house']}",
                "venus": f"{signo_venus} em Casa {subject.venus['house']}",
                "marte": f"{signo_marte} em Casa {subject.mars['house']}",
                "jupiter": f"{signo_jupiter} em Casa {subject.jupiter['house']}",
                "saturno": f"{signo_saturno} em Casa {subject.saturn['house']}",
                "urano": f"{signo_urano} em Casa {subject.uranus['house']}",
                "netuno": f"{signo_netuno} em Casa {subject.neptune['house']}",
                "plutao": f"{signo_plutao} em Casa {subject.pluto['house']}"
            },
            "diagnostico_scii_gnose": {
                "sol_letra": traduzir_arquetipo_requests(signo_sol),
                "lua_letra": traduzir_arquetipo_requests(signo_lua),
                "ascendente_letra": traduzir_arquetipo_requests(signo_asc),
                "mercurio_letra": traduzir_arquetipo_requests(signo_mercurio),
                "venus_letra": traduzir_arquetipo_requests(signo_venus),
                "marte_letra": traduzir_arquetipo_requests(signo_marte),
                "jupiter_letra": traduzir_arquetipo_requests(signo_jupiter),
                "saturno_letra": traduzir_arquetipo_requests(signo_saturno),
                "urano_letra": traduzir_arquetipo_requests(signo_urano),
                "netuno_letra": traduzir_arquetipo_requests(signo_netuno),
                "plutao_letra": traduzir_arquetipo_requests(signo_plutao)
            }
        }
    
    except Exception as e:
        return {"erro": str(e)}