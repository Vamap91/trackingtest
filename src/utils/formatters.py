def format_status_tag(status):
    """
    Formata o status do atendimento como uma tag colorida HTML.
    
    Args:
        status (str): Status do atendimento
        
    Returns:
        str: HTML da tag formatada
    """
    status_lower = status.lower()
    
    if "concluído" in status_lower or "finalizado" in status_lower:
        return '<span class="status-tag complete">Concluído</span>'
    
    elif "andamento" in status_lower or "execução" in status_lower or "processamento" in status_lower:
        return '<span class="status-tag progress">Em andamento</span>'
    
    elif "agendado" in status_lower or "programado" in status_lower:
        return '<span class="status-tag scheduled">Agendado</span>'
    
    # Status desconhecido
    return f'<span class="status-tag">{status}</span>'

def format_cpf_display(cpf):
    """
    Formata CPF para exibição com máscara.
    
    Args:
        cpf (str): CPF sem formatação
        
    Returns:
        str: CPF formatado (ex: 123.456.789-00)
    """
    # Remove caracteres não numéricos
    cpf = ''.join(filter(str.isdigit, cpf))
    
    # Se não tiver 11 dígitos, retorna como está
    if len(cpf) != 11:
        return cpf
    
    # Formata com pontos e traço
    return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

def format_telefone_display(telefone):
    """
    Formata telefone para exibição com máscara.
    
    Args:
        telefone (str): Telefone sem formatação
        
    Returns:
        str: Telefone formatado (ex: (11) 98765-4321)
    """
    # Remove caracteres não numéricos
    telefone = ''.join(filter(str.isdigit, telefone))
    
    # Formata conforme o comprimento
    if len(telefone) == 11:
        # Celular com 9
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
    elif len(telefone) == 10:
        # Telefone fixo
        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
    else:
        # Formato desconhecido, retorna como está
        return telefone

def format_placa_display(placa):
    """
    Formata placa para exibição.
    
    Args:
        placa (str): Placa sem formatação
        
    Returns:
        str: Placa formatada (ex: ABC-1234 ou ABC-1D23)
    """
    # Remove caracteres não alfanuméricos
    placa = ''.join(filter(lambda c: c.isalnum(), placa)).upper()
    
    # Formato antigo (ABC1234)
    if len(placa) == 7 and placa[:3].isalpha() and placa[3:].isdigit():
        return f"{placa[:3]}-{placa[3:]}"
    
    # Formato Mercosul (ABC1D23)
    elif len(placa) == 7 and placa[:3].isalpha() and placa[3].isdigit() and placa[4].isalpha() and placa[5:].isdigit():
        return f"{placa[:3]}-{placa[3:]}"
    
    # Formato desconhecido, retorna como está
    return placa

def format_money(value, currency="R$"):
    """
    Formata valor monetário.
    
    Args:
        value (float): Valor a ser formatado
        currency (str): Símbolo da moeda
        
    Returns:
        str: Valor formatado (ex: R$ 1.234,56)
    """
    try:
        # Converte para float se for string
        if isinstance(value, str):
            value = float(value.replace('.', '').replace(',', '.'))
        
        # Formata com duas casas decimais, separador de milhar e vírgula decimal
        formatted = f"{value:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        
        return f"{currency} {formatted}"
    except (ValueError, TypeError):
        # Se não conseguir formatar, retorna como está
        return f"{currency} {value}"
