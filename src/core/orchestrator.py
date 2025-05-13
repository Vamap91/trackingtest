from src.core.service_registry import ServiceRegistry

class ActionOrchestrator:
    """
    Orquestrador central de ações do sistema.
    Determina qual ação executar com base na entrada do usuário e contexto.
    """
    
    def __init__(self, session_manager, service_registry):
        self.session_manager = session_manager
        self.services = service_registry
    
    def process_input(self, user_input, channel, user_id):
        """
        Processa entrada do usuário e determina próximas ações
        
        Args:
            user_input (str): Texto enviado pelo usuário
            channel (str): Canal de origem ('web' ou 'whatsapp')
            user_id (str): Identificador do usuário
            
        Returns:
            str: Resposta formatada para o usuário
        """
        # Recuperar sessão/estado atual
        session = self.session_manager.get_session(channel, user_id)
        
        # Determinar intenção do usuário
        intent = self.services.intent_detector.detect(user_input, session)
        
        # Aplicar regras de negócio para determinar ação
        action = self.services.decision_engine.determine_action(intent, session)
        
        # Executar ação apropriada
        if action.type == "query_status":
            return self._handle_status_query(action, session)
        elif action.type == "answer_question":
            return self._handle_question(action, session)
        elif action.type == "escalate":
            return self._handle_escalation(action, session)
        elif action.type == "ask_for_identifier":
            return self._handle_ask_for_identifier(session)
        elif action.type == "custom_action":
            return self._handle_custom_action(action, session)
        else:
            return self._handle_unknown(action, session)
    
    def _handle_status_query(self, action, session):
        """Processa consulta de status"""
        identifier = action.params.get("identifier")
        id_type = action.params.get("id_type")
        
        # Consultar API Fusion baseado no tipo de identificador
        client_data = self.services.fusion_api.get_client_data(id_type, identifier)
        
        if client_data and client_data.get("sucesso"):
            # Atualizar sessão com dados do cliente
            session.update_client_info(client_data)
            
            # Gerar resposta personalizada
            response = self.services.response_generator.generate_status_response(
                client_data, 
                channel=session.channel
            )
            
            # Atualizar estado da sessão
            session.set_state("awaiting_followup")
            return response
        else:
            # Tratar falha na consulta
            session.set_state("awaiting_identifier")
            return self.services.response_generator.generate_not_found_response(
                id_type, 
                channel=session.channel
            )
    
    def _handle_question(self, action, session):
        """Processa pergunta sobre atendimento"""
        # Verificar se temos dados do cliente
        if not session.has_client_info():
            return self.services.response_generator.generate_need_identification_response(
                channel=session.channel
            )
        
        # Gerar resposta baseada no contexto e pergunta
        question = action.params.get("question")
        client_data = session.get_client_info()
        
        return self.services.ai_service.generate_response(
            question, 
            client_data,
            channel=session.channel
        )
    
    def _handle_escalation(self, action, session):
        """Escala para atendente humano"""
        reason = action.params.get("reason")
        
        # Registrar motivo do escalonamento
        session.set_escalation_reason(reason)
        
        # Iniciar processo de escalonamento
        escalation_id = self.services.escalation_service.escalate(
            session.user_id,
            session.channel,
            session.get_conversation_history(),
            reason
        )
        
        # Retornar mensagem informando sobre escalonamento
        return self.services.response_generator.generate_escalation_response(
            escalation_id,
            channel=session.channel
        )
    
    def _handle_ask_for_identifier(self, session):
        """Solicita identificador ao usuário"""
        return self.services.response_generator.generate_ask_for_identifier_response(
            channel=session.channel
        )
    
    def _handle_custom_action(self, action, session):
        """Executa ação personalizada com base em regras de negócio"""
        action_name = action.params.get("name")
        
        # Buscar handler para ação personalizada
        custom_actions = self.services.get("custom_actions")
        if action_name in custom_actions:
            handler = custom_actions[action_name]
            return handler(action.params, session)
        else:
            return self.services.response_generator.generate_not_implemented_response(
                action_name,
                channel=session.channel
            )
    
    def _handle_unknown(self, action, session):
        """Trata ações desconhecidas"""
        return self.services.response_generator.generate_fallback_response(
            channel=session.channel
        )
