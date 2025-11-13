import os
import sys 
import requests # O CLIENTE DE API
from datetime import datetime
import pytz # Para Fusos Horários

# --- FIX 1: SEM CONFIGURAÇÃO DE CACHE (astropy/pylunar não precisam) ---
# (Removemos o bloco de cache do flatlib/kerykeion)

# --- IMPORTAÇÕES (são seguras) ---
from fastapi import FastAPI
# (Removemos a importação do supabase-py, já que usamos 'requests')
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# --- IMPORTAÇÕES DO NOVO MOTOR (astropy/pylunar) ---
from astropy.time import Time
from astropy.coordinates import get_sun, get_moon, EarthLocation, SkyCoord
from astropy import units as u
import pylunar # Para a fase da Lua (e signo)

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
    cidade: str
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


# --- Endpoint Mapa de Alma (com o NOVO MOTOR: astropy/pylunar) ---
@app.post("/gerar-mapa-alma")
def gerar_mapa_alma(pessoa: PessoaInput):
    try:
        # 1. Configurar os dados de entrada
        fuso = pytz.timezone('America/Sao_Paulo')
        dt = fuso.localize(datetime(pessoa.ano, pessoa.mes, pessoa.dia, pessoa.hora, pessoa.minuto))
        
        lat = '-28.51' * u.deg
        lon = '-50.93' * u.deg
        local = EarthLocation(lat=lat, lon=lon)
        
        tempo = Time(dt)

        # 2. Gerar o mapa (Sol)
        sol_coords = get_sun(tempo).transform_to('geocentrictrueecliptic')
        # (Lógica para converter coordenadas eclípticas em signo)
        signos = ["Áries", "Touro", "Gêmeos", "Câncer", "Leão", "Virgem", "Libra", "Escorpião", "Sagitário", "Capricórnio", "Aquário", "Peixes"]
        signo_sol = signos[int(sol_coords.lon.degree / 30)]

        # 3. Gerar o mapa (Lua)
        lua_coords = get_moon(tempo, local).transform_to('geocentrictrueecliptic')
        signo_lua = signos[int(lua_coords.lon.degree / 30)]
        
        # 4. Retorna o diagnóstico (Simplificado, sem Ascendente por enquanto)
        return {
            "nome": pessoa.nome,
            "diagnostico_astrologico": {
                "sol": signo_sol,
                "lua": signo_lua,
                "ascendente": "Em desenvolvimento (Astropy)"
            },
            "diagnostico_scii_gnose": {
                "sol_letra": traduzir_arquetipo_requests(signo_sol),
                "lua_letra": traduzir_arquetipo_requests(signo_lua),
                "ascendente_letra": {"erro": "Ascendente em cálculo."}
            }
        }
    
    except Exception as e:
        return {"erro": str(e)}