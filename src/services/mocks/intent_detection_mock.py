from src.services.intent_detection import Intent
from src.utils.validators import detect_identifier_type

class IntentDetectorMock:
    """
    Versão mock do detector de intenções para desenvolvimento.
    """
    
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
        if "atendente" in message or "humano" in message or "pessoa" in message:
            return Intent(
                type="request_human",
                value=message,
                confidence=0.9
            )
        
        # Verificar se é pergunta sobre status
        if "status" in message or "andamento" in message or "situação" in message:
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
