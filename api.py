import os
import tempfile
from flask import Flask, request, jsonify

# SOLUÇÃO DEFINITIVA: Configurar AGressivamente o cache do Kerykeion
KERYKEION_CACHE_PATH = '/tmp/kerykeion_cache'
os.environ['KERYKEION_DB_PATH'] = KERYKEION_CACHE_PATH
os.environ['KERYKEION_CACHE_PATH'] = KERYKEION_CACHE_PATH

# Criar diretório de cache explicitamente
os.makedirs(KERYKEION_CACHE_PATH, exist_ok=True)

print(f"🎯 Cache configurado em: {KERYKEION_CACHE_PATH}")

from kerykeion import AstrologicalSubject

app = Flask(__name__)

@app.route('/gerar-mapa-alma', methods=['POST'])
def gerar_mapa_alma():
    data = request.get_json()
    try:
        # 1. Cria o "sujeito astrológico" com a CLASSE CORRETA
        #    E APLICA A "SOLUÇÃO DEFINITIVA" (db_path='/tmp/...')
        sujeito = AstrologicalSubject(
            name=data['nome'],
            year=int(data['ano']),
            month=int(data['mes']),
            day=int(data['dia']),
            hour=int(data['hora']),
            minute=int(data['minuto']),
            city=data['cidade'],
            nation=data['pais'],
            db_path=KERYKEION_CACHE_PATH
        )

        # 2. Obtém os dados principais (Sol, Lua, Ascendente)
        sol = sujeito.sun
        lua = sujeito.moon
        ascendente = sujeito.ascending

        # 3. Retorna o diagnóstico astrológico básico
        return jsonify({
            "nome": sujeito.name,
            "diagnostico_basico": {
                "sol": f"{sol['sign']} em {sol['house']}",
                "lua": f"{lua['sign']} em {lua['house']}",
                "ascendente": ascendente['sign']
            }
        })

    except Exception as e:
        print(f"🔥 ERRO: {str(e)}")
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)