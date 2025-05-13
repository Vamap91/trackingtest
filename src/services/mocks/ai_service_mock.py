class AIServiceMock:
    """
    Versão mock do serviço de IA para desenvolvimento.
    """
    
    def generate_response(self, question, client_data, channel="web"):
        """
        Gera resposta simulada para perguntas do cliente
        
        Args:
            question (str): Pergunta do cliente
            client_data (dict): Dados do cliente e atendimento
            channel (str): Canal de comunicação
            
        Returns:
            str: Resposta gerada
        """
        dados = client_data.get("dados", {})
        nome = dados.get("nome", "Cliente")
        status = dados.get("status", "Em processamento")
        ordem = dados.get("ordem", "N/A")
        tipo_servico = dados.get("tipo_servico", "")
        
        # Respostas pré-definidas para perguntas comuns
        question_lower = question.lower()
        
        if any(word in question_lower for word in ["prazo", "previsão", "quando", "tempo", "demora"]):
            if status == "Em andamento":
                return f"Seu serviço de {tipo_servico} está em andamento e a previsão de conclusão é para hoje até o final do dia. Assim que for finalizado, você receberá uma notificação."
            elif status == "Agendado":
                return f"Seu serviço está agendado e será realizado conforme data e horário combinados. Para confirmar o horário exato, recomendo entrar em contato com nossa central pelo 0800-727-2327."
            else:
                return f"Seu serviço já foi concluído! O veículo foi entregue conforme solicitado."
                
        elif any(word in question_lower for word in ["peça", "material", "vidro"]):
            return f"Para o serviço de {tipo_servico}, estamos utilizando peças originais com garantia de fábrica. Todos os materiais já estão em estoque e são de primeira linha para garantir a qualidade do serviço."
            
        elif any(word in question_lower for word in ["loja", "unidade", "próxima", "endereço"]):
            return "Temos várias unidades disponíveis. As mais próximas e com disponibilidade para atendimento são:\n\n- CarGlass Morumbi: Av. Dr. Guilherme Dumont Vilares, 1163\n- CarGlass Santana: R. Voluntários da Pátria, 2191\n\nDeseja que eu informe mais detalhes sobre alguma delas?"
            
        elif any(word in question_lower for word in ["garantia", "seguro"]):
            return f"Todos os serviços da CarGlass possuem garantia. Para o serviço de {tipo_servico}, a garantia é de 12 meses para defeitos de instalação. Em caso de trincas ou quebras por impacto, não é coberto pela garantia."
            
        elif any(word in question_lower for word in ["preço", "valor", "custo", "pagamento"]):
            return f"O valor do serviço de {tipo_servico} já foi definido e está registrado em nossa ordem de serviço. Para informações detalhadas sobre valores e formas de pagamento, por favor entre em contato com nossa central pelo 0800-727-2327."
            
        elif any(word in question_lower for word in ["status", "andamento", "situação"]):
            return f"O status atual do seu atendimento é: {status}. A ordem de serviço {ordem} está sendo acompanhada por nossa equipe para garantir a qualidade do serviço."
            
        else:
            # Resposta genérica para outras perguntas
            return (
                f"Olá {nome}, obrigado por sua pergunta.\n\n"
                f"Baseado nas informações que temos, seu serviço de {tipo_servico} está com status: {status}.\n\n"
                f"Para obter informações mais detalhadas sobre sua pergunta específica, "
                f"recomendo entrar em contato com nossa central de atendimento pelo 0800-727-2327."
            )
