import os
import tempfile
from flask import Flask, request, jsonify

# SOLUÇÃO DEFINITIVA: Configurar AGressivamente o cache do Kerykeion
os.environ['KERYKEION_DB_PATH'] = '/tmp/kerykeion_cache'
os.environ['KERYKEION_CACHE_PATH'] = '/tmp/kerykeion_cache'

# Criar diretório de cache explicitamente
cache_dir = '/tmp/kerykeion_cache'
os.makedirs(cache_dir, exist_ok=True)

print(f"🎯 Cache configurado em: {cache_dir}")

from kerykeion import Report

app = Flask(__name__)

@app.route('/gerar-mapa-alma', methods=['POST'])
def gerar_mapa_alma():
    data = request.get_json()
    try:
        nome = data['nome']
        ano = int(data['ano'])
        mes = int(data['mes'])
        dia = int(data['dia'])
        hora = int(data['hora'])
        minuto = int(data['minuto'])
        cidade = data['cidade']
        pais = data['pais']

        # Forçar o uso do cache directory explicitamente
        report = Report(
            nome, ano, mes, dia, hora, minuto, cidade, pais,
            db_path='/tmp/kerykeion_cache'  # SOLUÇÃO EXPLÍCITA
        )

        return jsonify({
            "nome": report.subject.name,
            "data_nascimento": report.subject.birthdate.isoformat(),
            "cidade_nascimento": report.subject.birthplace,
            "signo_solar": report.subject.sun_sign,
            "ascendente": report.subject.ascendant,
            "casa_lunar": report.subject.moon_house,
            "planetas": [
                {
                    "nome": planet.name,
                    "signo": planet.sign,
                    "casa": planet.house,
                    "grau": planet.position
                }
                for planet in report.planets_list
            ]
        })
    except Exception as e:
        print(f"🔥 ERRO: {str(e)}")
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)