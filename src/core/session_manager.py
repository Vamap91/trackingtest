import json
import time
import uuid
from datetime import datetime, timedelta

class SessionManager:
    """
    Gerencia sessões de usuários através de múltiplos canais.
    Responsável por persistência e recuperação de estado.
    """
    
    def __init__(self, storage_client=None):
        """
        Inicializa gerenciador de sessões
        
        Args:
            storage_client: Cliente de armazenamento (Redis, MongoDB, etc.)
        """
        self.storage = storage_client
        self.session_ttl = 24 * 60 * 60  # 24 horas (em segundos)
        
        # Se não houver cliente de armazenamento, usar dicionário em memória (para desenvolvimento)
        if self.storage is None:
            self.memory_storage = {}
    
    def get_session(self, channel, user_id):
        """
        Recupera ou cria uma sessão para o usuário
        
        Args:
            channel: Canal de comunicação (web, whatsapp)
            user_id: ID do usuário nesse canal
            
        Returns:
            Session: Objeto de sessão
        """
        key = self._create_session_key(channel, user_id)
        
        if self.storage is None:
            # Usar armazenamento em memória para desenvolvimento
            session_data = self.memory_storage.get(key)
        else:
            # Usar cliente de armazenamento
            session_data = self.storage.get(key)
        
        if session_data:
            try:
                if isinstance(session_data, bytes):
                    session_data = session_data.decode('utf-8')
                session_dict = json.loads(session_data)
                return Session(channel, user_id, self, session_dict)
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Erro nos dados da sessão, criar nova
                return self._create_new_session(channel, user_id)
        else:
            # Sessão não existe, criar nova
            return self._create_new_session(channel, user_id)
    
    def save_session(self, session):
        """
        Persiste uma sessão
        
        Args:
            session: Objeto de sessão a ser salvo
        """
        key = self._create_session_key(session.channel, session.user_id)
        session_data = json.dumps(session.to_dict())
        
        if self.storage is None:
            # Usar armazenamento em memória para desenvolvimento
            self.memory_storage[key] = session_data
        else:
            # Usar cliente de armazenamento
            self.storage.setex(key, self.session_ttl, session_data)
    
    def delete_session(self, channel, user_id):
        """
        Remove uma sessão
        
        Args:
            channel: Canal de comunicação
            user_id: ID do usuário
        """
        key = self._create_session_key(channel, user_id)
        
        if self.storage is None:
            # Usar armazenamento em memória para desenvolvimento
            if key in self.memory_storage:
                del self.memory_storage[key]
        else:
            # Usar cliente de armazenamento
            self.storage.delete(key)
    
    def _create_session_key(self, channel, user_id):
        """Cria chave única para a sessão"""
        return f"session:{channel}:{user_id}"
    
    def _create_new_session(self, channel, user_id):
        """Cria nova sessão com valores padrão"""
        session = Session(
            channel=channel,
            user_id=user_id,
            manager=self,
            data={
                "session_id": str(uuid.uuid4()),
                "created_at": datetime.now().isoformat(),
                "state": "awaiting_identifier",
                "conversation_history": [
                    {
                        "role": "assistant",
                        "content": "Olá! Sou o assistente virtual da CarGlass. Por favor, informe seu CPF, telefone, placa, ordem de serviço ou chassi para que eu possa te ajudar.",
                        "timestamp": datetime.now().isoformat()
                    }
                ],
                "client_info": None,
                "escalation_info": None
            }
        )
        self.save_session(session)
        return session


class Session:
    """
    Representa uma sessão de usuário com todos os dados de estado e histórico.
    """
    
    def __init__(self, channel, user_id, manager, data):
        self.channel = channel
        self.user_id = user_id
        self.manager = manager
        self.data = data
    
    def get_state(self):
        """Retorna estado atual da sessão"""
        return self.data.get("state", "awaiting_identifier")
    
    def set_state(self, new_state):
        """Atualiza estado da sessão"""
        self.data["state"] = new_state
        self.manager.save_session(self)
    
    def add_message(self, role, content):
        """Adiciona mensagem ao histórico"""
        if "conversation_history" not in self.data:
            self.data["conversation_history"] = []
            
        self.data["conversation_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        self.manager.save_session(self)
    
    def get_conversation_history(self):
        """Retorna histórico de conversa"""
        return self.data.get("conversation_history", [])
    
    def update_client_info(self, client_data):
        """Atualiza informações do cliente"""
        self.data["client_info"] = client_data
        self.manager.save_session(self)
    
    def get_client_info(self):
        """Retorna informações do cliente"""
        return self.data.get("client_info")
    
    def has_client_info(self):
        """Verifica se tem informações do cliente"""
        return self.data.get("client_info") is not None
    
    def set_escalation_reason(self, reason):
        """Registra motivo de escalonamento"""
        if "escalation_info" not in self.data:
            self.data["escalation_info"] = {}
        
        self.data["escalation_info"]["reason"] = reason
        self.data["escalation_info"]["timestamp"] = datetime.now().isoformat()
        self.manager.save_session(self)
    
    def get_escalation_id(self):
        """Retorna ID de escalonamento para atendente"""
        if "escalation_info" in self.data:
            return self.data["escalation_info"].get("id")
        return None
    
    def to_dict(self):
        """Converte sessão para dicionário"""
        return self.data
    
    def reset(self):
        """Reinicia a sessão"""
        self.data["state"] = "awaiting_identifier"
        self.data["client_info"] = None
        self.data["escalation_info"] = None
        self.data["conversation_history"] = [
            {
                "role": "assistant",
                "content": "Olá! Sou o assistente virtual da CarGlass. Por favor, informe seu CPF, telefone, placa, ordem de serviço ou chassi para que eu possa te ajudar.",
                "timestamp": datetime.now().isoformat()
            }
        ]
        self.manager.save_session(self)
