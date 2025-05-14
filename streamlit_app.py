import streamlit as st
import requests
import json
import time
import re
import uuid

# Configuração da página
st.set_page_config(
    page_title="CarGlass - Assistente Virtual",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        font-weight: 600;
        color: #1e3a8a;
    }
    
    .main-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-message {
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 10px;
        display: flex;
        align-items: flex-start;
    }
    
    .chat-message.user {
        background-color: #e6f3ff;
    }
    
    .chat-message.assistant {
        background-color: #f0f7ff;
        border-left: 5px solid #0066cc;
    }
    
    .chat-message .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
        margin-right: 1rem;
    }
    
    .chat-message .message {
        flex-grow: 1;
    }
    
    .status-tag {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 50px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .status-tag.complete {
        background-color: #d1fae5;
        color: #047857;
    }
    
    .status-tag.progress {
        background-color: #ffedd5;
        color: #c2410c;
    }
    
    .status-tag.scheduled {
        background-color: #dbeafe;
        color: #1e40af;
    }
    
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
        color: #666;
    }
    
    /* Remove o Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="main-header"><img src="https://www.carglass.com.br/wp-content/uploads/2023/02/logoCarglass.png" width="200"></div>', unsafe_allow_html=True)

# Inicializar variáveis de sessão
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou o assistente virtual da CarGlass. Posso ajudar com informações sobre seu atendimento, status do serviço e mais. Digite seu CPF, telefone, placa do veículo, número da ordem ou chassi para começarmos."}
    ]

if "awaiting_identifier" not in st.session_state:
    st.session_state.awaiting_identifier = True

if "cliente_info" not in st.session_state:
    st.session_state.cliente_info = None

# Função para detectar o tipo de identificador
def detect_identifier_type(text):
    # Remove caracteres não alfanuméricos
    clean_text = re.sub(r'[^a-zA-Z0-9]', '', text)
    
    # Verifica CPF (11 dígitos numéricos)
    if re.match(r'^\d{11}$', clean_text):
        return "cpf", clean_text
    
    # Verifica telefone (10-11 dígitos numéricos)
    elif re.match(r'^\d{10,11}$', clean_text):
        return "telefone", clean_text
    
    # Verifica placa (3 letras + 4 números ou 3 letras + 1 número + 1 letra + 2 números)
    elif re.match(r'^[A-Za-z]{3}\d{4}$', clean_text) or re.match(r'^[A-Za-z]{3}\d[A-Za-z]\d{2}$', clean_text):
        return "placa", clean_text.upper()
    
    # Verifica chassi (17 caracteres alfanuméricos)
    elif re.match(r'^[A-HJ-NPR-Z0-9]{17}$', clean_text.upper()):
        return "chassi", clean_text.upper()
    
    # Verifica ordem (começa com "ORD" ou números)
    elif clean_text.upper().startswith("ORD") or re.match(r'^\d{5,8}$', clean_text):
        return "ordem", clean_text.upper()
    
    # Não foi possível identificar
    return None, clean_text

# Função para buscar dados do cliente
def get_client_data(tipo, valor):
    """Versão com dados simulados para teste de interface"""
    
    # Mostrar banner de ambiente de teste
    st.warning("⚠️ AMBIENTE DE TESTE - Usando dados simulados para demonstração")
    
    # Simular um pequeno atraso como em chamada real
    time.sleep(1)
    
    # Dados simulados baseados no tipo de identificador
    mock_data = {
        "sucesso": True,
        "tipo": tipo,
        "valor": valor,
        "dados": {
            "nome": "Cliente Teste",
            "cpf": "123.456.789-00" if tipo == "cpf" else "N/A",
            "telefone": "(11) 98765-4321" if tipo == "telefone" else "N/A",
            "ordem": f"ORD{12345}" if tipo == "ordem" else f"ORD{65432}",
            "status": ["Em andamento", "Concluído", "Agendado"][hash(valor) % 3],
            "tipo_servico": "Troca de Parabrisa",
            "veiculo": {
                "modelo": "Honda Civic",
                "placa": valor.upper() if tipo == "placa" else "ABC1D23",
                "ano": "2023"
            }
        }
    }
    
    # Para testes, falhar ocasionalmente para simular erro de servidor
    if hash(valor) % 10 == 0:
        return None
        
    return mock_data

# Função para processar a entrada do usuário
def process_user_input():
    user_input = st.session_state.user_input
    
    if not user_input:
        return
        
    # Adicionar mensagem do usuário ao histórico
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Resetar o input para limpar o campo
    st.session_state.user_input = ""
    
    # Se estiver aguardando identificador
    if st.session_state.awaiting_identifier:
        # Tentar detectar o tipo de identificador
        tipo, valor = detect_identifier_type(user_input)
        
        if tipo:
            # Mostrar mensagem de processamento temporária
            temp_message = "Estou consultando suas informações..."
            st.session_state.messages.append({"role": "assistant", "content": temp_message})
            
            # Processar a solicitação
            with st.spinner("Consultando..."):
                client_data = get_client_data(tipo, valor)
            
            # Remover a mensagem temporária
            st.session_state.messages.pop()
            
            if client_data and client_data.get("sucesso"):
                # Armazenar dados do cliente
                st.session_state.cliente_info = client_data
                st.session_state.awaiting_identifier = False
                
                # Extrair informações principais
                dados = client_data.get("dados", {})
                nome = dados.get("nome", "Cliente")
                status = dados.get("status", "Em processamento")
                ordem = dados.get("ordem", "N/A")
                
                # Exibir mensagem personalizada com os dados
                status_tag = ""
                if status.lower() == "concluído":
                    status_tag = '<span class="status-tag complete">Concluído</span>'
                elif status.lower() == "em andamento":
                    status_tag = '<span class="status-tag progress">Em andamento</span>'
                else:
                    status_tag = '<span class="status-tag scheduled">Agendado</span>'
                
                # Usar a mensagem da IA se disponível
                if "mensagem_ia" in client_data:
                    response_message = client_data["mensagem_ia"]
                else:
                    response_message = f"""
                    Olá {nome}! Encontrei suas informações.
                    
                    Seu atendimento está com status: {status_tag}
                    
                    Ordem de serviço: {ordem}
                    
                    Como posso ajudar você hoje? Você pode perguntar sobre:
                    - Detalhes do seu atendimento
                    - Previsão de conclusão
                    - Peças utilizadas
                    - Lojas mais próximas
                    """
                
                st.session_state.messages.append({"role": "assistant", "content": response_message})
            else:
                # Não encontrou o cliente
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"""
                    Não consegui encontrar informações com o {tipo} fornecido. 
                    
                    Por favor, verifique se digitou corretamente ou tente outro tipo de identificação.
                    
                    Você pode informar:
                    - CPF (11 dígitos)
                    - Telefone (com DDD)
                    - Placa do veículo
                    - Número da ordem de serviço
                    - Chassi do veículo
                    """
                })
        else:
            # Não conseguiu identificar o tipo
            st.session_state.messages.append({
                "role": "assistant", 
                "content": """
                Não consegui identificar o formato da informação fornecida.
                
                Por favor, digite um dos seguintes:
                - CPF (11 dígitos)
                - Telefone (com DDD)
                - Placa do veículo (AAA0000 ou AAA0A00)
                - Número da ordem de serviço
                - Chassi do veículo (17 caracteres)
                """
            })
    # Se já identificou o cliente, processar perguntas adicionais
    else:
        # Aqui processaria as perguntas usando a IA com contexto do cliente
        client_data = st.session_state.cliente_info
        dados = client_data.get("dados", {})
        
        # Simular o processamento da IA
        with st.spinner("Processando sua pergunta..."):
            time.sleep(1.5)  # Simular processamento
            
            # Resposta simulada - em uma implementação real, viria da API de IA
            resposta = f"""
            Baseado nos dados do seu atendimento, posso informar que:
            
            {user_input}
            
            Para mais detalhes específicos sobre essa questão, recomendo entrar em contato com nossa central pelo 0800-727-2327.
            
            Posso ajudar com mais alguma informação?
            """
            
            st.session_state.messages.append({"role": "assistant", "content": resposta})

# Função para reiniciar a conversa
def reset_conversation():
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou o assistente virtual da CarGlass. Posso ajudar com informações sobre seu atendimento, status do serviço e mais. Digite seu CPF, telefone, placa do veículo, número da ordem ou chassi para começarmos."}
    ]
    st.session_state.awaiting_identifier = True
    st.session_state.cliente_info = None

# Exibir mensagens na interface de chat
for msg in st.session_state.messages:
    avatar_url = "https://api.dicebear.com/7.x/bottts/svg?seed=CarGlass" if msg["role"] == "assistant" else "https://api.dicebear.com/7.x/personas/svg?seed=Client"
    
    with st.container():
        st.markdown(f"""
        <div class="chat-message {msg['role']}">
            <img src="{avatar_url}" class="avatar" alt="{msg['role']}">
            <div class="message">{msg['content']}</div>
        </div>
        """, unsafe_allow_html=True)

# Container para entrada do usuário
with st.container():
    # Campo de entrada do usuário
    st.text_input(
        "Digite aqui sua mensagem ou identificação", 
        key="user_input",
        on_change=process_user_input,
        placeholder="CPF, telefone, placa, chassi ou ordem de serviço..."
    )
    
    # Botões de ação
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        st.button("Nova Consulta", on_click=reset_conversation)

# Footer
st.markdown("""
<div class="footer">
    <p>© 2025 CarGlass Brasil - Assistente Virtual</p>
    <p>Central de Atendimento: 0800-727-2327 | WhatsApp: (11) 4003-8070</p>
</div>
""", unsafe_allow_html=True)
