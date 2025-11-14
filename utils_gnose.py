import os
import requests
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos

# Chaves do Supabase (lidas dos segredos do Vercel)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # Use a chave service_role

def traduzir_arquetipo_para_letra(nome_arquetipo, headers):
    """Busca a letra hebraica correspondente a um arquétipo no Supabase."""
    try:
        # 1. Encontrar o ID do arquétipo pelo nome
        params_arq = {'nome_arquetipo': f'eq.{nome_arquetipo}', 'select': 'id'}
        resp_arq = requests.get(f"{SUPABASE_URL}/rest/v1/arquetipos", headers=headers, params=params_arq)
        resp_arq.raise_for_status()
        data_arq = resp_arq.json()
        if not data_arq:
            return {"erro": f"Arquétipo '{nome_arquetipo}' não encontrado."}
        arquetipo_id = data_arq[0]['id']

        # 2. Encontrar o ID da letra pela correspondência
        params_corr = {'arquetipo_id': f'eq.{arquetipo_id}', 'select': 'letra_id'}
        resp_corr = requests.get(f"{SUPABASE_URL}/rest/v1/scii_correspondencias", headers=headers, params=params_corr)
        resp_corr.raise_for_status()
        data_corr = resp_corr.json()
        if not data_corr:
            return {"erro": f"Correspondência para '{nome_arquetipo}' não encontrada."}
        letra_id = data_corr[0]['letra_id']

        # 3. Buscar os dados da letra
        params_letra = {'id': f'eq.{letra_id}', 'select': 'nome_letra,pictografia,acao_espiritual'}
        resp_letra = requests.get(f"{SUPABASE_URL}/rest/v1/letras", headers=headers, params=params_letra)
        resp_letra.raise_for_status()
        data_letra = resp_letra.json()
        if not data_letra:
            return {"erro": f"Letra com ID '{letra_id}' não encontrada."}
        
        return data_letra[0]
    except Exception as e:
        print(f"Erro ao traduzir arquétipo '{nome_arquetipo}': {e}")
        return {"erro": str(e)}

def calcular_mapa_e_buscar_dados(nome, data_nasc, hora_nasc, local_nasc):
    """
    Função central que executa toda a Gnose:
    1. Calcula o mapa astrológico com flatlib.
    2. Busca os dados de arquétipos/letras no Supabase.
    3. Retorna um dicionário (JSON) completo.
    """
    print(f"Iniciando cálculo para: {nome}")

    try:
        # ================================================================
        # == INÍCIO: LÓGICA ADAPTADA DE API.PY ===========================
        # ================================================================
        
        # 1. Lógica do Flatlib
        # TODO: Implementar geocodificação para 'local_nasc'
        lat = -28.51  # Exemplo: Vacaria
        lon = -50.93  # Exemplo: Vacaria
        
        # O formato da data deve ser 'YYYY/MM/DD' e hora 'HH:MM'
        data_formatada = data_nasc.replace('-', '/')
        data = Datetime(data_formatada, hora_nasc, "-03:00") # Fuso de São Paulo
        pos = GeoPos(lat, lon)
        chart = Chart(data, pos)
        
        # Extração dos planetas e ascendente
        sol = chart.getObject("Sun")
        lua = chart.getObject("Moon")
        mercurio = chart.getObject("Mercury")
        venus = chart.getObject("Venus")
        marte = chart.getObject("Mars")
        jupiter = chart.getObject("Jupiter")
        saturno = chart.getObject("Saturn")
        urano = chart.getObject("Uranus")
        netuno = chart.getObject("Neptune")
        plutao = chart.getObject("Pluto")
        asc = chart.get(0)

        mapa_astrologico = {
            "sol": {"signo": sol.sign, "casa": sol.house()},
            "lua": {"signo": lua.sign, "casa": lua.house()},
            "ascendente": {"signo": asc.sign, "casa": asc.house()},
            "mercurio": {"signo": mercurio.sign, "casa": mercurio.house()},
            "venus": {"signo": venus.sign, "casa": venus.house()},
            "marte": {"signo": marte.sign, "casa": marte.house()},
            "jupiter": {"signo": jupiter.sign, "casa": jupiter.house()},
            "saturno": {"signo": saturno.sign, "casa": saturno.house()},
            "urano": {"signo": urano.sign, "casa": urano.house()},
            "netuno": {"signo": netuno.sign, "casa": netuno.house()},
            "plutao": {"signo": plutao.sign, "casa": plutao.house()},
        }

        # 2. Lógica do Supabase (com Requests)
        headers = {
            "apikey": SUPABASE_KEY,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json"
        }
        
        dados_scii = {}
        for astro, dados in mapa_astrologico.items():
            signo = dados['signo']
            # O nome do campo no JSON de resposta será 'sol_letra', 'lua_letra', etc.
            dados_scii[f"{astro}_letra"] = traduzir_arquetipo_para_letra(signo, headers)

        # ================================================================
        # == FIM: LÓGICA ADAPTADA ========================================
        # ================================================================

        # 3. Montar o Dicionário/JSON de resposta
        resultado_final = {
            "nome": nome,
            "dados_nascimento": {
                "data": data_nasc,
                "hora": hora_nasc,
                "local": local_nasc
            },
            "diagnostico_astrologico": mapa_astrologico,
            "diagnostico_scii_gnose": dados_scii
        }

        print(f"Cálculo concluído com sucesso para {nome}.")
        return resultado_final

    except Exception as e:
        print(f"ERRO CRÍTICO em utils_gnose: {e}")
        return {"erro": str(e), "status": 500}
