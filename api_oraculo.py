import os
from google import genai

AIzaSyDc07nAn0ajBRc0IgZyj3TzRZkpiwQDvCw
client = genai.Client(AIzaSyDc07nAn0ajBRc0IgZyj3TzRZkpiwQDvCw)

def consultar_oraculo(pergunta_do_usuario):
    # 1. Definição do Cérebro (Instrução do Sistema)
    # Aqui, a instrução completa do SCII (V2.0) será carregada.
    # Por enquanto, usamos um placeholder, mas na vida real o modelo já tem a instrução salva.
    system_instruction = "SUA_INSTRUÇÃO_COMPLETA_DO_SCII_V2_0_VAI_AQUI"
    
    # 2. Configurações e Chamada ao Modelo
    response = client.models.generate_content(
        model='gemini-2.5-pro',
        contents=[
            {"role": "user", "parts": [{"text": pergunta_do_usuario}]},
        ],
        config={
            "system_instruction": system_instruction,
            "temperature": 0.5,
            # Se você usou Grounding (arquivos/links), isso também está configurado no modelo.
        }
    )
    
    # 3. Retorno da Resposta
    return response.text

# --- TESTE SIMPLES (NÃO FAZ PARTE DA API, APENAS PARA TESTAR) ---
# resultado = consultar_oraculo("Qual é o meu desafio neste momento?")
# print(resultado)
