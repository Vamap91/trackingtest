import uuid
from datetime import datetime

class EscalationServiceMock:
    """
    Versão mock do serviço de escalonamento para desenvolvimento.
    """
    
    def __init__(self):
        # Armazenamento temporário para desenvolvimento
        self.escalations = {}
    
    def escalate(self, user_id, channel, conversation_history, reason):
        """Escala a conversa para um atendente humano (simulado)"""
        # Gerar ID único para o escalonamento
        escalation_id = str(uuid.uuid4())[:8].upper()
        
        # Registrar escalonamento para acompanhamento
        self.escalations[escalation_id] = {
            "user_id": user_id,
            "channel": channel,
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "status": "pending"
        }
        
        print(f"[MOCK] Conversa escalonada: {escalation_id} - Usuário: {user_id} - Motivo: {reason}")
        
        return escalation_id
    
    def get_escalation_status(self, escalation_id):
        """Consulta status de um escalonamento"""
        if escalation_id in self.escalations:
            return self.escalations[escalation_id]["status"]
        return "not_found"
    
    def update_escalation_status(self, escalation_id, status):
        """Atualiza status de um escalonamento"""
        if escalation_id in self.escalations:
            self.escalations[escalation_id]["status"] = status
            self.escalations[escalation_id]["updated_at"] = datetime.now().isoformat()
