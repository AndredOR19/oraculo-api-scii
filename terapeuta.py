from enum import Enum, auto
import requests
import re

# Enum para controlar o fluxo da conversa
class EstagioSessao(Enum):
    ACOLHIMENTO = auto()
    QUEIXA = auto()
    INVESTIGACAO = auto()
    INTERVENCAO = auto()
    ENCERRAMENTO = auto()

class SessaoTerapeutica:
    """
    Orquestra uma sessão terapêutica completa, gerenciando o estado, 
    o fluxo e a interação com os endpoints da API.
    """
    def __init__(self, user_id: str, base_url: str = "http://127.0.0.1:8000"):
        self.user_id = user_id
        self.estagio = EstagioSessao.ACOLHIMENTO
        self.historico = []
        self.diagnostico_silencioso = None
        self.base_url = base_url

    def processar_entrada(self, texto_usuario: str = ""):
        """
        Processa a entrada do usuário com base no estágio atual da sessão.
        Este é o método principal que impulsiona a conversa.
        """
        self.historico.append(f"Usuário: {texto_usuario}")

        if self.estagio == EstagioSessao.ACOLHIMENTO:
            return self._processar_acolhimento()
        
        elif self.estagio == EstagioSessao.QUEIXA:
            return self._processar_queixa(texto_usuario)

        elif self.estagio == EstagioSessao.INVESTIGACAO:
            # Em uma implementação real, as respostas do usuário aqui levariam a mais perguntas
            # ou à transição para a intervenção.
            return self._propor_intervencao()

        elif self.estagio == EstagioSessao.INTERVENCAO:
            # Aqui, o sistema reagiria à confirmação do usuário para a intervenção.
            if "sim" in texto_usuario.lower() or "gostaria" in texto_usuario.lower():
                return self._executar_intervencao()
            else:
                self.estagio = EstagioSessao.ENCERRAMENTO
                return self._processar_encerramento()
        
        elif self.estagio == EstagioSessao.ENCERRAMENTO:
            # Qualquer mensagem do usuário no estágio de encerramento pode finalizar a sessão.
            return "A sessão foi encerrada. Que a paz e a clareza o acompanhem."


    def _processar_acolhimento(self):
        """Gera a mensagem de boas-vindas e avança para o estágio de queixa."""
        self.estagio = EstagioSessao.QUEIXA
        resposta = (
            "Bem-vindo. Eu sou o Terapeuta Arquetípico. "
            "Minha função é servir como um espelho para a sua alma, usando a sabedoria antiga das Letras Sagradas. "
            "Lembre-se, sou uma ferramenta para autoconhecimento, não um substituto para terapia profissional. "
            "Nossa conversa é confidencial. Sinta-se à vontade para compartilhar o que está em sua mente e em seu coração."
        )
        self.historico.append(f"Terapeuta: {resposta}")
        return resposta

    def _processar_queixa(self, texto_queixa: str):
        """Recebe a queixa, chama o diagnóstico e avança para a investigação."""
        try:
            # Chama o endpoint de análise da API principal
            response = requests.post(f"{self.base_url}/diagnostico/analisar_queixa", json={"queixa": texto_queixa})
            response.raise_for_status()
            self.diagnostico_silencioso = response.json()
            
            self.estagio = EstagioSessao.INVESTIGACAO
            resposta = self._gerar_pergunta_socratica()
            self.historico.append(f"Terapeuta: {resposta}")
            return resposta

        except requests.exceptions.RequestException as e:
            return f"Erro ao processar a queixa: {e}"
        except Exception as e:
            return f"Ocorreu um erro inesperado: {e}"

    def _gerar_pergunta_socratica(self):
        """Gera a primeira pergunta de aprofundamento com base no diagnóstico."""
        if not self.diagnostico_silencioso:
            return "Não foi possível analisar sua queixa. Poderia reformular?"

        # Extrai a síntese para a pergunta
        sintese = self.diagnostico_silencioso.get("diagnostico_sintetizado", "")
        
        # Lógica simples para extrair o tema principal da síntese
        tema = "suas palavras"
        if "conflito" in sintese:
            tema = "a energia do 'conflito'"
        elif "bloqueio" in sintese:
            tema = "a sensação de 'bloqueio'"
        
        return f"Entendo. Sinto em {tema}. Onde em seu corpo você localiza essa sensação com mais intensidade?"

    def _propor_intervencao(self):
        """Com base na conversa, propõe uma meditação ou outra ferramenta."""
        # Lógica para decidir qual letra usar (aqui, usamos a primeira do diagnóstico)
        try:
            primeira_pratica = self.diagnostico_silencioso['praticas_recomendadas'][0]['letra_chave']
            letra_nome = re.match(r'(\w+)', primeira_pratica).group(1)
        except (TypeError, IndexError, AttributeError):
            letra_nome = "Aleph" # Fallback

        self.estagio = EstagioSessao.INTERVENCAO
        resposta = f"Parece que estamos tocando na energia de {letra_nome}. Gostaria que eu gerasse uma meditação guiada para explorarmos isso juntos agora?"
        self.historico.append(f"Terapeuta: {resposta}")
        return resposta

    def _executar_intervencao(self):
        """Chama o endpoint para gerar a meditação e avança para o encerramento."""
        try:
            primeira_pratica = self.diagnostico_silencioso['praticas_recomendadas'][0]['letra_chave']
            letra_nome = re.match(r'(\w+)', primeira_pratica).group(1)
        except (TypeError, IndexError, AttributeError):
            letra_nome = "Aleph" # Fallback

        try:
            response = requests.post(f"{self.base_url}/mestre/gerar_meditacao_guiada", json={"letra": letra_nome})
            response.raise_for_status()
            meditacao = response.json()['meditacao_guiada']
            
            self.estagio = EstagioSessao.ENCERRAMENTO
            resposta = f"Aqui está a sua meditação:\n\n{meditacao}\n\nApós concluí-la, podemos encerrar nossa sessão."
            self.historico.append(f"Terapeuta: {resposta}")
            return resposta

        except requests.exceptions.RequestException as e:
            return f"Erro ao gerar a meditação: {e}"

    def _processar_encerramento(self):
        """Gera a mensagem de resumo e a 'lição de casa' antes de finalizar."""
        # Em uma implementação futura, salvaria o resumo na Memória Ativa.
        self.estagio = EstagioSessao.ENCERRAMENTO # Mantém no estágio final
        resposta = "Nesta sessão, exploramos as energias que se manifestaram em sua queixa. Como prática para a semana, sugiro que observe os momentos em que essa sensação surge, sem julgamento. Apenas observe."
        self.historico.append(f"Terapeuta: {resposta}")
        return resposta