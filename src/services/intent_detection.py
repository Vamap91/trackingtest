import re
from src.utils.validators import detect_identifier_type

class Intent:
    """Representa uma intenção detectada na mensagem do usuário"""
    
    def __init__(self, type, value=None, entity_type=None, confidence=1.0):
        self.type = type        # Tipo de intenção (ex: provide_identifier, ask_status)
        self.value = value      # Valor associado (ex: número do CPF, pergunta)
        self.entity_type = entity_type  # Tipo de entidade (ex: cpf, telefone, ordem)
        self.confidence = confidence    # Confiança na detecção (0.0 a 1.0)

class IntentDetector:
    """
    Responsável por detectar a intenção do usuário com base na mensagem.
    Em uma implementação completa, poderia usar NLU, mas começamos com regras simples.
    """
    
    def __init__(self):
        # Definir expressões regulares para tipos comuns de intenção
        self.request_human_patterns = [
            r'\b(falar|conversar|atendente|pessoa|humano|operador)\b',
            r'\b(não|ajud\w+ não|chatbot|bot)\b'
        ]
        
        self.ask_status_patterns = [
            r'\b(status|andamento|situação|etapa|fase|prazo|previsão)\b'
        ]
    
    def detect(self, message, session):
        """
        Detecta a intenção do usuário a partir da mensagem
        
        Args:
            message (str): Texto da mensagem do usuário
            session: Sessão atual com contexto
            
        Returns:
            Intent: Objeto representando a intenção detectada
        """
        # Limpeza básica da mensagem
        message = message.strip().lower()
        
        # Verificar se é um identificador (CPF, telefone, placa, etc.)
        id_type, id_value = detect_identifier_type(message)
        if id_type:
            return Intent(
                type="provide_identifier",
                value=id_value,
                entity_type=id_type,
                confidence=0.95
            )
        
        # Verificar se é pedido para falar com atendente humano
        if self._matches_patterns(message, self.request_human_patterns):
            return Intent(
                type="request_human",
                value=message,
                confidence=0.9
            )
        
        # Verificar se é pergunta sobre status
        if self._matches_patterns(message, self.ask_status_patterns):
            return Intent(
                type="ask_status",
                value=message,
                confidence=0.8
            )
        
        # Se não identificou nenhuma intenção específica, tratar como pergunta genérica
        return Intent(
            type="ask_question",
            value=message,
            confidence=0.6
        )
    
    def _matches_patterns(self, text, patterns):
        """Verifica se o texto corresponde a algum dos padrões"""
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
