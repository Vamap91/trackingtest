import logging
import requests
import streamlit as st
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class AIService:
    """
    Serviço para integração com API de IA (OpenAI ou similar).
    Responsável por gerar respostas personalizadas usando IA.
    """
    
    def __init__(self):
        # Tentar obter configurações do secrets
        try:
            self.api_key = st.secrets.get("openai", {}).get("api_key", "")
            self.model = st.secrets.get("openai", {}).get("model", "gpt-3.5-turbo")
            self.api_endpoint = st.secrets.get("openai", {}).get("api_endpoint", "https://api.openai.com/v1/chat/completions")
        except Exception as e:
            logger.warning(f"Não foi possível carregar configurações OpenAI: {str(e)}")
            self.api_key = ""
            self.model = "gpt-3.5-turbo"
            self.api_endpoint = "https://api.openai.com/v1/chat/completions"
    
    def generate_response(self, question, client_data, channel="web"):
        """
        Gera resposta personalizada para a pergunta do cliente usando IA
        
        Args:
            question (str): Pergunta do cliente
            client_data (dict): Dados do cliente e atendimento
            channel (str): Canal de comunicação
            
        Returns:
            str: Resposta gerada
        """
        # Se não tem API key ou estamos em desenvolvimento, usar resposta mock
        if not self.api_key or self._is_dev_mode():
            return self._generate_mock_response(question, client_data, channel)
        
        try:
            # Preparar contexto para a IA
            context = self._prepare_context(client_data)
            
            # Montar prompt para a IA
            prompt = self._create_prompt(question, context)
            
            # Chamar API de IA
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": question}
                ],
                "max_tokens": 300,
                "temperature": 0.7
            }
            
            response = requests.post(
                self.api_endpoint,
                headers=headers,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                answer = result["choices"][0]["message"]["content"].strip()
                return answer
            else:
                logger.error(f"Erro na API de IA: {response.status_code} - {response.text}")
                return self._generate_fallback_response()
                
        except Exception as e:
            logger.error(f"Erro ao gerar resposta com IA: {str(e)}")
            return self._generate_fallback_response()
    
    def _prepare_context(self, client_data):
        """Prepara contexto do cliente para a IA"""
        dados = client_data.get("dados", {})
        nome = dados.get("nome", "Cliente")
        status = dados.get("status", "Em processamento")
        ordem = dados.get("ordem", "N/A")
        tipo_servico = dados.get("tipo_servico", "")
        veiculo = dados.get("veiculo", {})
        
        return {
            "nome": nome,
            "status": status,
            "ordem": ordem,
            "tipo_servico": tipo_servico,
            "veiculo": veiculo
        }
    
    def _create_prompt(self, question, context):
        """Cria prompt para a IA com contexto do cliente"""
        return (
            f"Você é o assistente virtual da CarGlass, uma empresa especializada em reparo e troca de vidros automotivos.\n"
            f"Você está conversando com {context['nome']}, que tem um atendimento com as seguintes informações:\n\n"
            f"- Status do atendimento: {context['status']}\n"
            f"- Ordem de serviço: {context['ordem']}\n"
            f"- Tipo de serviço: {context['tipo_servico']}\n"
            f"- Veículo: {context['veiculo'].get('modelo', '')} - {context['veiculo'].get('ano', '')}\n"
            f"- Placa: {context['veiculo'].get('placa', '')}\n\n"
            f"Responda de forma educada, clara e concisa. Se não tiver certeza sobre alguma informação específica, "
            f"sugira que o cliente entre em contato com a central de atendimento pelo 0800-727-2327.\n\n"
            f"O cliente está perguntando: {question}\n"
            f"Forneça uma resposta personalizada considerando o contexto do atendimento."
        )
    
    def _is_dev_mode(self):
        """Verifica se estamos em modo de desenvolvimento"""
        try:
            return st.secrets.get("api", {}).get("environment", "dev") == "dev"
        except:
            return True
    
    def _generate_mock_response(self, question, client_data, channel):
        """Gera resposta simulada para desenvolvimento e testes"""
        dados = client_data.get("dados", {})
        nome = dados.get("nome", "Cliente")
        status = dados.get("status", "Em processamento")
        ordem = dados.get("ordem", "N/A")
        
        # Respostas pré-definidas para perguntas comuns
        question_lower = question.lower()
        
        if "prazo" in question_lower or "previsão" in question_lower or "quando" in question_lower:
            if status == "Em andamento":
                return f"Seu serviço de {dados.get('tipo_servico', '')} está em andamento e a previsão de conclusão é para hoje até o final do dia."
            elif status == "Agendado":
                return f"Seu serviço está agendado e será realizado conforme data e horário combinados. Para confirmar o horário exato, recomendo entrar em contato com nossa central."
            else:
                return f"Seu serviço já foi concluído! O veículo foi entregue conforme solicitado."
                
        elif "peça" in question_lower or "material" in question_lower:
            return f"Para o serviço de {dados.get('tipo_servico', '')}, estamos utilizando peças originais com garantia de fábrica. Todos os materiais já estão em estoque."
            
        elif "loja" in question_lower or "unidade" in question_lower or "próxima" in question_lower:
            return "Temos várias unidades disponíveis. As mais próximas e com disponibilidade para atendimento são:\n\n- CarGlass Morumbi: Av. Dr. Guilherme Dumont Vilares, 1163\n- CarGlass Santana: R. Voluntários da Pátria, 2191\n\nDeseja que eu informe mais detalhes sobre alguma delas?"
            
        elif "garantia" in question_lower:
            return f"Todos os serviços da CarGlass possuem garantia. Para o serviço de {dados.get('tipo_servico', '')}, a garantia é de 12 meses para defeitos de instalação. Em caso de trincas ou quebras por impacto, não é coberto pela garantia."
            
        else:
            # Resposta genérica para outras perguntas
            return (
                f"Baseado nas informações do seu atendimento, posso informar que seu serviço de "
                f"{dados.get('tipo_servico', 'vidros automotivos')} está com status: {status}.\n\n"
                f"Para {nome}, em relação à sua pergunta sobre '{question}', recomendo entrar em contato "
                f"com nossa central de atendimento pelo 0800-727-2327 para informações mais detalhadas."
            )
    
    def _generate_fallback_response(self):
        """Gera resposta padrão em caso de erro na IA"""
        return (
            "Desculpe, não consegui processar sua pergunta neste momento. "
            "Por favor, tente novamente ou entre em contato com nossa central de atendimento "
            "pelo telefone 0800-727-2327 para obter assistência."
        )
