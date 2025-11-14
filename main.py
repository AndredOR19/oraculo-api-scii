"""
Este arquivo existe apenas para compatibilidade com o cache do Vercel.
Os endpoints reais estão em /api/
"""

def handler(event, context):
    return {
        'statusCode': 200,
        'body': 'Use /api/chat ou /api/calcular_mapa'
    }
