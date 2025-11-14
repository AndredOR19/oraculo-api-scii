from http.server import BaseHTTPRequestHandler
import json
from utils_gnose import calcular_mapa_e_buscar_dados # <-- Importa o Coração!

class handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            # 1. Obter os dados do corpo da requisição
            # Ajustado para o formato esperado pelo front-end/Postman
            nome = data.get('nome')
            # O front-end pode enviar 'ano', 'mes', 'dia' ou uma string 'data'
            if 'data' in data:
                data_nasc = data.get('data') # Formato 'AAAA-MM-DD'
            else:
                data_nasc = f"{data.get('ano')}-{str(data.get('mes')).zfill(2)}-{str(data.get('dia')).zfill(2)}"

            # O front-end pode enviar 'hora', 'minuto' ou uma string 'hora'
            if 'hora' in data and ':' in data['hora']:
                 hora_nasc = data.get('hora') # Formato 'HH:MM'
            else:
                 hora_nasc = f"{str(data.get('hora')).zfill(2)}:{str(data.get('minuto')).zfill(2)}"

            local_nasc = data.get('local', data.get('cidade', 'Não informado'))
            
            # 2. Chamar a função centralizada
            resultado_mapa = calcular_mapa_e_buscar_dados(
                nome=nome,
                data_nasc=data_nasc,
                hora_nasc=hora_nasc,
                local_nasc=local_nasc
            )
            
            # 3. Enviar a resposta (o JSON do mapa)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*') # CORS
            self.end_headers()
            self.wfile.write(json.dumps(resultado_mapa).encode('utf-8'))

        except Exception as e:
            print(f"ERRO no /api/calcular_mapa: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"erro": str(e)}).encode('utf-8'))
