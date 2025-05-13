class Action:
    """Representa uma ação a ser tomada pelo sistema"""
    
    def __init__(self, type, params=None):
        self.type = type
        self.params = params or {}


class DecisionEngine:
    """
    Motor de regras para tomada de decisão com base na intenção e contexto.
    Implementa toda a lógica condicional.
    """
    
    def __init__(self, rule_configs=None):
        self.rules = rule_configs or self._load_default_rules()
    
    def determine_action(self, intent, session):
        """
        Determina a próxima ação com base na intenção e estado da sessão
        
        Args:
            intent: Intenção detectada
            session: Sessão atual com estado e histórico
            
        Returns:
            Action: Objeto com tipo de ação e parâmetros
        """
        # Verificar estado atual da sessão
        current_state = session.get_state()
        
        # Regras para estado inicial/identificação
        if current_state == "awaiting_identifier":
            if intent.type == "provide_identifier":
                return Action(
                    type="query_status",
                    params={
                        "identifier": intent.value,
                        "id_type": intent.entity_type
                    }
                )
            else:
                return Action(
                    type="ask_for_identifier",
                    params={}
                )
        
        # Regras para clientes já identificados
        elif current_state == "awaiting_followup":
            # Cliente já identificado, processando perguntas ou comandos
            
            # Caso: cliente pede para falar com atendente
            if intent.type == "request_human":
                return Action(
                    type="escalate",
                    params={
                        "reason": "customer_request"
                    }
                )
            
            # Caso: cliente pergunta sobre status
            elif intent.type == "ask_status":
                return Action(
                    type="answer_question",
                    params={
                        "question": intent.value
                    }
                )
            
            # Caso: cliente fornece novo identificador
            elif intent.type == "provide_identifier":
                return Action(
                    type="query_status",
                    params={
                        "identifier": intent.value,
                        "id_type": intent.entity_type
                    }
                )
            
            # Caso: pergunta genérica sobre serviço
            elif intent.type == "ask_question":
                # Verificar se conseguimos responder ou precisamos escalar
                if self._can_answer_question(intent.value, session):
                    return Action(
                        type="answer_question",
                        params={
                            "question": intent.value
                        }
                    )
                else:
                    return Action(
                        type="escalate",
                        params={
                            "reason": "complex_question"
                        }
                    )
            
            # Caso padrão: tentar responder como pergunta
            else:
                return Action(
                    type="answer_question",
                    params={
                        "question": intent.value
                    }
                )
        
        # Estado de escalonamento
        elif current_state == "escalated":
            # Se já escalonado, qualquer mensagem vai para o atendente
            return Action(
                type="forward_to_agent",
                params={
                    "message": intent.value,
                    "escalation_id": session.get_escalation_id()
                }
            )
        
        # Estado desconhecido (erro)
        else:
            return Action(
                type="reset_session",
                params={}
            )
    
    def _can_answer_question(self, question, session):
        """
        Determina se o bot pode responder a pergunta ou precisa escalar
        
        Args:
            question: Texto da pergunta
            session: Sessão atual
            
        Returns:
            bool: True se o bot pode responder, False se precisa escalar
        """
        # Implementar lógica para determinar se a pergunta está no escopo do bot
        # Isso pode usar NLP, keywords, ou outras técnicas
        
        # Exemplo simples baseado em palavras-chave
        answerable_topics = [
            "status", "prazo", "previsão", "peças", "valor", 
            "pagamento", "garantia", "tempo", "finalizado", "loja"
        ]
        
        # Verificar se a pergunta contém palavras-chave respondíveis
        question_lower = question.lower()
        for topic in answerable_topics:
            if topic in question_lower:
                return True
        
        # Verificar complexidade da pergunta
        words = question_lower.split()
        if len(words) > 20:  # Perguntas muito longas podem ser complexas
            return False
            
        # Por padrão, tentar responder
        return True
        
    def _load_default_rules(self):
        """Carrega regras padrão de negócio"""
        # Implementar carregamento de regras (pode ser de arquivo JSON/YAML)
        return {}
