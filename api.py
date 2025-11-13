import os
import sys

# Configurar ambiente
os.environ['HOME'] = '/tmp'

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from kerykeion import AstrologicalSubject

# Carregar variáveis
load_dotenv() 
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

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
        # Dicionário de tradução de signos (abreviação → nome completo em português)
        signos_map = {
            "Ari": "Áries", "Tau": "Touro", "Gem": "Gêmeos",
            "Can": "Câncer", "Leo": "Leão", "Vir": "Virgem",
            "Lib": "Libra", "Sco": "Escorpião", "Sag": "Sagitário",
            "Cap": "Capricórnio", "Aqu": "Aquário", "Pis": "Peixes"
        }
        
        # Dicionário de tradução de casas
        casas_map = {
            "First_House": "1", "Second_House": "2", "Third_House": "3",
            "Fourth_House": "4", "Fifth_House": "5", "Sixth_House": "6",
            "Seventh_House": "7", "Eighth_House": "8", "Ninth_House": "9",
            "Tenth_House": "10", "Eleventh_House": "11", "Twelfth_House": "12"
        }
        
        subject = AstrologicalSubject(
            pessoa.nome,
            pessoa.ano,
            pessoa.mes,
            pessoa.dia,
            pessoa.hora,
            pessoa.minuto,
            lat=-28.51,
            lng=-50.93,
            tz_str="America/Sao_Paulo",
            city=pessoa.cidade,
            nation=pessoa.pais
        )
        
        # Extrair e traduzir os signos
        signo_sol = signos_map.get(subject.sun["sign"], subject.sun["sign"])
        signo_lua = signos_map.get(subject.moon["sign"], subject.moon["sign"])
        signo_asc = signos_map.get(subject.first_house["sign"], subject.first_house["sign"])
        signo_mercurio = signos_map.get(subject.mercury["sign"], subject.mercury["sign"])
        signo_venus = signos_map.get(subject.venus["sign"], subject.venus["sign"])
        signo_marte = signos_map.get(subject.mars["sign"], subject.mars["sign"])
        signo_jupiter = signos_map.get(subject.jupiter["sign"], subject.jupiter["sign"])
        signo_saturno = signos_map.get(subject.saturn["sign"], subject.saturn["sign"])
        signo_urano = signos_map.get(subject.uranus["sign"], subject.uranus["sign"])
        signo_netuno = signos_map.get(subject.neptune["sign"], subject.neptune["sign"])
        signo_plutao = signos_map.get(subject.pluto["sign"], subject.pluto["sign"])
        
        # Extrair e traduzir as casas
        casa_sol = casas_map.get(subject.sun["house"], subject.sun["house"])
        casa_lua = casas_map.get(subject.moon["house"], subject.moon["house"])
        casa_mercurio = casas_map.get(subject.mercury["house"], subject.mercury["house"])
        casa_venus = casas_map.get(subject.venus["house"], subject.venus["house"])
        casa_marte = casas_map.get(subject.mars["house"], subject.mars["house"])
        casa_jupiter = casas_map.get(subject.jupiter["house"], subject.jupiter["house"])
        casa_saturno = casas_map.get(subject.saturn["house"], subject.saturn["house"])
        casa_urano = casas_map.get(subject.uranus["house"], subject.uranus["house"])
        casa_netuno = casas_map.get(subject.neptune["house"], subject.neptune["house"])
        casa_plutao = casas_map.get(subject.pluto["house"], subject.pluto["house"])
        
        return {
            "nome": pessoa.nome,
            "diagnostico_astrologico": {
                "sol": f"{signo_sol} em Casa {casa_sol}",
                "lua": f"{signo_lua} em Casa {casa_lua}",
                "ascendente": signo_asc,
                "mercurio": f"{signo_mercurio} em Casa {casa_mercurio}",
                "venus": f"{signo_venus} em Casa {casa_venus}",
                "marte": f"{signo_marte} em Casa {casa_marte}",
                "jupiter": f"{signo_jupiter} em Casa {casa_jupiter}",
                "saturno": f"{signo_saturno} em Casa {casa_saturno}",
                "urano": f"{signo_urano} em Casa {casa_urano}",
                "netuno": f"{signo_netuno} em Casa {casa_netuno}",
                "plutao": f"{signo_plutao} em Casa {casa_plutao}"
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
