import re

def detect_identifier_type(text):
    """
    Detecta automaticamente o tipo de identificador fornecido pelo usuário.
    
    Args:
        text (str): Texto fornecido pelo usuário
        
    Returns:
        tuple: (tipo, valor) onde tipo é uma string ('cpf', 'telefone', etc.) e valor é o identificador normalizado
    """
    # Remove caracteres não alfanuméricos para normalização
    clean_text = re.sub(r'[^a-zA-Z0-9]', '', text)
    
    # Verifica CPF (11 dígitos numéricos)
    if re.match(r'^\d{11}$', clean_text):
        return "cpf", clean_text
    
    # Verifica telefone (10-11 dígitos numéricos)
    elif re.match(r'^\d{10,11}$', clean_text):
        return "telefone", clean_text
    
    # Verifica placa (3 letras + 4 números ou 3 letras + 1 número + 1 letra + 2 números)
    # Formato antigo: ABC1234
    # Formato Mercosul: ABC1D23
    elif re.match(r'^[A-Za-z]{3}\d{4}$', clean_text) or re.match(r'^[A-Za-z]{3}\d[A-Za-z]\d{2}$', clean_text):
        return "placa", clean_text.upper()
    
    # Verifica chassi (17 caracteres alfanuméricos)
    # Exclui caracteres I, O e Q conforme padrão VIN
    elif re.match(r'^[A-HJ-NPR-Z0-9]{17}$', clean_text.upper()):
        return "chassi", clean_text.upper()
    
    # Verifica ordem (começa com "ORD" ou números)
    elif clean_text.upper().startswith("ORD") or re.match(r'^\d{5,8}$', clean_text):
        # Normaliza para incluir o prefixo ORD se for apenas números
        if re.match(r'^\d{5,8}$', clean_text):
            return "ordem", f"ORD{clean_text}"
        return "ordem", clean_text.upper()
    
    # Não foi possível identificar
    return None, clean_text

def validate_cpf(cpf):
    """
    Valida se um CPF é estruturalmente válido (não verifica se é real).
    
    Args:
        cpf (str): CPF a ser validado
        
    Returns:
        bool: True se o CPF é válido, False caso contrário
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'[^0-9]', '', cpf)
    
    # Verificar se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verificar se todos os dígitos são iguais (caso inválido)
    if len(set(cpf)) == 1:
        return False
    
    # Validação dos dígitos verificadores
    # Primeiro dígito verificador
    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cpf[9]) != digito1:
        return False
    
    # Segundo dígito verificador
    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    return int(cpf[10]) == digito2

def validate_telefone(telefone):
    """
    Valida se um número de telefone tem formato válido para o Brasil.
    
    Args:
        telefone (str): Número de telefone a ser validado
        
    Returns:
        bool: True se o telefone é válido, False caso contrário
    """
    # Remove caracteres não numéricos
    telefone = re.sub(r'[^0-9]', '', telefone)
    
    # Verificar se tem 10 ou 11 dígitos (com ou sem 9 no celular)
    if len(telefone) not in [10, 11]:
        return False
    
    # Verifica se o DDD é válido (entre 11 e 99)
    ddd = int(telefone[:2])
    if ddd < 11 or ddd > 99:
        return False
    
    # Se for celular (11 dígitos), o terceiro dígito deve ser 9
    if len(telefone) == 11 and telefone[2] != '9':
        return False
    
    return True

def validate_placa(placa):
    """
    Valida se uma placa de veículo tem formato válido (padrão antigo ou Mercosul).
    
    Args:
        placa (str): Placa a ser validada
        
    Returns:
        bool: True se a placa é válida, False caso contrário
    """
    # Remove caracteres não alfanuméricos
    placa = re.sub(r'[^a-zA-Z0-9]', '', placa).upper()
    
    # Verifica formato antigo (3 letras + 4 números)
    if re.match(r'^[A-Z]{3}\d{4}$', placa):
        return True
    
    # Verifica formato Mercosul (3 letras + 1 número + 1 letra + 2 números)
    if re.match(r'^[A-Z]{3}\d[A-Z]\d{2}$', placa):
        return True
    
    return False

def validate_chassi(chassi):
    """
    Valida se um chassi tem formato válido segundo o padrão VIN.
    
    Args:
        chassi (str): Chassi a ser validado
        
    Returns:
        bool: True se o chassi é válido, False caso contrário
    """
    # Remove caracteres não alfanuméricos
    chassi = re.sub(r'[^a-zA-Z0-9]', '', chassi).upper()
    
    # Verifica se tem 17 caracteres
    if len(chassi) != 17:
        return False
    
    # Verifica se não contém caracteres proibidos (I, O, Q)
    if re.search(r'[IOQ]', chassi):
        return False
    
    # Padrão básico do VIN/chassi
    if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', chassi):
        return False
    
    return True

def validate_ordem(ordem):
    """
    Valida se uma ordem de serviço tem formato válido.
    
    Args:
        ordem (str): Ordem de serviço a ser validada
        
    Returns:
        bool: True se a ordem é válida, False caso contrário
    """
    # Remove caracteres não alfanuméricos
    ordem = re.sub(r'[^a-zA-Z0-9]', '', ordem).upper()
    
    # Verifica se começa com "ORD" seguido de números
    if re.match(r'^ORD\d{5,8}$', ordem):
        return True
    
    # Ou se é apenas números (5 a 8 dígitos)
    if re.match(r'^\d{5,8}$', ordem):
        return True
    
    return False
