from src.utils.formatters import format_status_tag

class ResponseGenerator:
    """
    Responsável por gerar respostas formatadas para o usuário.
    Adapta a saída conforme o canal (web, WhatsApp) e tipo de informação.
    """
    
    def generate_status_response(self, client_data, channel="web"):
        """
        Gera resposta formatada para consulta de status
        
        Args:
            client_data (dict): Dados do cliente e atendimento
            channel (str): Canal de comunicação ('web' ou 'whatsapp')
            
        Returns:
            str: Mensagem formatada
        """
        # Se já tem uma mensagem da IA, usá-la
        if "mensagem_ia" in client_data and client_data["mensagem_ia"]:
            return client_data["mensagem_ia"]
        
        # Extrair informações principais
        dados = client_data.get("dados", {})
        nome = dados.get("nome", "Cliente")
        status = dados.get("status", "Em processamento")
        ordem = dados.get("ordem", "N/A")
        tipo_servico = dados.get("tipo_servico", "")
        veiculo = dados.get("veiculo", {})
        modelo = veiculo.get("modelo", "")
        placa = veiculo.get("placa", "")
        
        # Formatar conforme o canal
        if channel == "whatsapp":
            # Formato mais simples para WhatsApp (sem HTML)
            return (
                f"Olá {nome}! Encontrei suas informações.\n\n"
                f"Seu atendimento está com status: {status}\n"
                f"Ordem de serviço: {ordem}\n"
                f"Serviço: {tipo_servico}\n"
                f"Veículo: {modelo} - Placa: {placa}\n\n"
                f"Como posso ajudar você hoje? Você pode perguntar sobre:\n"
                f"- Detalhes do seu atendimento\n"
                f"- Previsão de conclusão\n"
                f"- Peças utilizadas\n"
                f"- Lojas mais próximas"
            )
        else:
            # Formato mais rico para web (com HTML)
            status_tag = format_status_tag(status)
            
            return (
                f"Olá {nome}! Encontrei suas informações.\n\n"
                f"Seu atendimento está com status: {status_tag}\n\n"
                f"Ordem de serviço: {ordem}\n"
                f"Serviço: {tipo_servico}\n"
                f"Veículo: {modelo} - Placa: {placa}\n\n"
                f"Como posso ajudar você hoje? Você pode perguntar sobre:\n"
                f"- Detalhes do seu atendimento\n"
                f"- Previsão de conclusão\n"
                f"- Peças utilizadas\n"
                f"- Lojas mais próximas"
            )
    
    def generate_not_found_response(self, id_type, channel="web"):
        """Gera resposta para quando não encontra informações do cliente"""
        return (
            f"Não consegui encontrar informações com o {id_type} fornecido.\n\n"
            f"Por favor, verifique se digitou corretamente ou tente outro tipo de identificação.\n\n"
            f"Você pode informar:\n"
            f"- CPF (11 dígitos)\n"
            f"- Telefone (com DDD)\n"
            f"- Placa do veículo\n"
            f"- Número da ordem de serviço\n"
            f"- Chassi do veículo"
        )
    
    def generate_ask_for_identifier_response(self, channel="web"):
        """Gera resposta solicitando identificador ao usuário"""
        return (
            f"Por favor, me informe um dos seguintes dados para que eu possa consultar seu atendimento:\n\n"
            f"- CPF (11 dígitos)\n"
            f"- Telefone (com DDD)\n"
            f"- Placa do veículo\n"
            f"- Número da ordem de serviço\n"
            f"- Chassi do veículo"
        )
    
    def generate_need_identification_response(self, channel="web"):
        """Gera resposta quando precisa identificar o cliente primeiro"""
        return (
            f"Para que eu possa te ajudar com isso, preciso primeiro identificar seu atendimento.\n\n"
            f"Por favor, me informe seu CPF, telefone, placa do veículo, número da ordem de serviço ou chassi."
        )
    
    def generate_escalation_response(self, escalation_id, channel="web"):
        """Gera resposta quando a conversa é escalonada para um atendente humano"""
        return (
            f"Entendo que você precisa de uma assistência mais específica. Vou transferir você para um de nossos atendentes.\n\n"
            f"Um atendente entrará em contato em breve. Seu número de protocolo é {escalation_id}.\n\n"
            f"Obrigado por utilizar o assistente virtual da CarGlass!"
        )
    
    def generate_not_implemented_response(self, action_name, channel="web"):
        """Gera resposta quando uma funcionalidade não está implementada"""
        return (
            f"Desculpe, a funcionalidade '{action_name}' ainda não está disponível.\n\n"
            f"Estamos trabalhando para implementá-la em breve. Por enquanto, posso ajudar com consultas de status e informações sobre seu atendimento."
        )
    
    def generate_fallback_response(self, channel="web"):
        """Gera resposta padrão quando não entende a solicitação"""
        return (
            f"Desculpe, não consegui entender completamente sua solicitação.\n\n"
            f"Posso ajudar com informações sobre seu atendimento, status do serviço, previsão de conclusão e informações gerais sobre os serviços da CarGlass.\n\n"
            f"Como posso te ajudar hoje?"
        )
