import streamlit as st
import requests
import json
import time
import re
import openai
import base64
from pathlib import Path

# Função para carregar imagens locais como base64
@st.cache_data
def get_image_base64(image_path):
    """Carrega e converte uma imagem para base64 com cache"""
    if not Path(image_path).exists():
        return None
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Carrega a imagem da atendente uma única vez
atendente_img_path = "assets/atendente-carglass.jpg"
atendente_img_b64 = get_image_base64(atendente_img_path)
atendente_img_url = f"data:image/jpeg;base64,{atendente_img_b64}" if atendente_img_b64 else "https://api.dicebear.com/7.x/bottts/svg?seed=CarGlass"

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
        {"role": "assistant", "content": "Olá! Sou o assistente virtual da CarGlass. Estou aqui para ajudar com informações sobre seu atendimento, status do serviço e esclarecer qualquer dúvida que você tenha! 😊 Por favor, digite seu CPF, telefone, placa do veículo, número da ordem ou chassi para começarmos."}
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
    """Função para buscar dados do cliente através da API real"""
    
    # URL base do serviço
    base_url = "http://fusion-hml.carglass.hml.local:3000/api/status"
    
    # Montar URL específica com base no tipo de identificador
    api_url = f"{base_url}/{tipo}/{valor}"
    
    # Headers da requisição
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        # Fazer a requisição GET para a API
        response = requests.get(api_url, headers=headers, timeout=30)
        
        # Verificar se a resposta foi bem-sucedida
        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError:
                st.error("Erro ao processar resposta do servidor.")
                return None
        else:
            st.warning(f"Servidor retornou status {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Erro ao consultar API: {str(e)}")
        return None
            
   
    else:
        # Usar a API real
        try:
            # URL base do serviço
            base_url = "http://fusion-hml.carglass.hml.local:3000/api/status"
            
            # Montar URL específica com base no tipo de identificador
            api_url = f"{base_url}/{tipo}/{valor}"
            
            # Headers da requisição
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Fazer a requisição GET para a API
            response = requests.get(api_url, headers=headers, timeout=30)
            
            # Verificar se a resposta foi bem-sucedida
            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    st.error("Erro ao processar resposta do servidor.")
                    return None
            else:
                st.warning(f"Servidor retornou status {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Erro ao consultar API: {str(e)}")
            return None

# Função para processar consultas do usuário com IA
def process_user_query(user_input, client_data):
    """Processa consultas do usuário usando GPT-4 Turbo após identificação"""
    
    # Configurar API key da OpenAI - buscando do secrets do Streamlit
    try:
        # Tentativa de acessar a chave da API das secrets do Streamlit
        openai.api_key = st.secrets["openai"]["api_key"]
        has_api_key = True
    except (KeyError, TypeError):
        has_api_key = False
    
    if not has_api_key:
        st.warning("⚠️ AMBIENTE DE TESTE - API OpenAI não configurada. Usando respostas simuladas.")
        # Retornar resposta simulada
        return f"""
        Claro! Baseado nos dados do seu atendimento, posso informar que:
        
        {user_input}
        
        Para mais detalhes específicos sobre essa questão, recomendo entrar em contato com nossa central pelo 0800-727-2327.
        
        Posso ajudar com mais alguma informação? 😊
        """
    
    try:
        # Extrair dados do cliente
        dados = client_data.get("dados", {})
        nome = dados.get("nome", "Cliente")
        status = dados.get("status", "Em processamento")
        ordem = dados.get("ordem", "N/A")
        
        # Construir prompt para o GPT-4 Turbo com personalidade mais amigável
        system_message = f"""
        Você é o assistente virtual da CarGlass, amigável, prestativo e especializado em atendimento ao cliente.
        
        Personalidade: Use um tom amigável, caloroso e empático. Seja conversacional e natural como um atendente humano que se importa.
        Refira-se ao cliente pelo nome quando possível. Use linguagem simples e direta, evitando termos técnicos desnecessários.
        Ocasionalmente use emojis adequados (😊, 👍, etc.) para tornar a conversa mais amigável, mas sem exagerar.
        
        Você está conversando com {nome}, que tem um atendimento com as seguintes informações:
        - Status: {status}
        - Ordem: {ordem}
        - Serviço: {dados.get('tipo_servico', 'N/A')}
        - Veículo: {dados.get('veiculo', {}).get('modelo', 'N/A')} - {dados.get('veiculo', {}).get('ano', 'N/A')}
        - Placa: {dados.get('veiculo', {}).get('placa', 'N/A')}
        
        Forneça respostas úteis, empáticas e precisas com base no contexto do atendimento.
        Limite suas respostas a no máximo 3 parágrafos. Seja conciso e direto.
        Não invente informações que não estão no contexto.
        Se não souber a resposta, sugira contatar a central de atendimento de forma amigável.
        
        Quando apropriado, mostre entusiasmo com pequenas expressões como "Claro!", "Com prazer!" ou "Sem problema!" no início das respostas.
        """
        
        # Chamada para o modelo GPT-4 Turbo da OpenAI
        # Usando o client da versão mais recente da OpenAI
        response = openai.chat.completions.create(
            model="gpt-4-turbo-preview",  # Usar GPT-4 Turbo
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_input}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        # Extrair e retornar a resposta
        return response.choices[0].message.content
        
    except Exception as e:
        st.error(f"Erro ao processar com IA: {str(e)}")
        return "Desculpe, não foi possível processar sua pergunta. Por favor, tente novamente ou entre em contato com nossa central de atendimento pelo 0800-727-2327."

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
                    Olá {nome}! 😊 Encontrei suas informações.
                    
                    Seu atendimento está com status: {status_tag}
                    
                    Ordem de serviço: {ordem}
                    
                    Como posso ajudar você hoje? Você pode perguntar sobre:
                    - Detalhes do seu atendimento
                    - Previsão de conclusão
                    - Peças utilizadas
                    - Lojas mais próximas
                    
                    Estou à disposição para esclarecer qualquer dúvida!
                    """
                
                st.session_state.messages.append({"role": "assistant", "content": response_message})
            else:
                # Não encontrou o cliente
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"""
                    Não consegui encontrar informações com o {tipo} fornecido. 😕
                    
                    Por favor, verifique se digitou corretamente ou tente outro tipo de identificação.
                    
                    Você pode informar:
                    - CPF (11 dígitos)
                    - Telefone (com DDD)
                    - Placa do veículo
                    - Número da ordem de serviço
                    - Chassi do veículo
                    
                    Estou aqui para ajudar quando estiver pronto! 👍
                    """
                })
        else:
            # Não conseguiu identificar o tipo
            st.session_state.messages.append({
                "role": "assistant", 
                "content": """
                Não consegui identificar o formato da informação fornecida. 😕
                
                Por favor, digite um dos seguintes:
                - CPF (11 dígitos)
                - Telefone (com DDD)
                - Placa do veículo (AAA0000 ou AAA0A00)
                - Número da ordem de serviço
                - Chassi do veículo (17 caracteres)
                
                Vamos tentar novamente? Estou aqui para ajudar! 😊
                """
            })
    # Se já identificou o cliente, processar perguntas adicionais
    else:
        # Aqui processamos as perguntas usando a IA com contexto do cliente
        client_data = st.session_state.cliente_info
        
        # Processar com a OpenAI ou resposta simulada
        with st.spinner("Processando sua pergunta..."):
            resposta = process_user_query(user_input, client_data)
            
        st.session_state.messages.append({"role": "assistant", "content": resposta})

# Função para reiniciar a conversa
def reset_conversation():
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou o assistente virtual da CarGlass. Estou aqui para ajudar com informações sobre seu atendimento, status do serviço e esclarecer qualquer dúvida que você tenha! 😊 Por favor, digite seu CPF, telefone, placa do veículo, número da ordem ou chassi para começarmos."}
    ]
    st.session_state.awaiting_identifier = True
    st.session_state.cliente_info = None

# Exibir mensagens na interface de chat
for msg in st.session_state.messages:
    # Aqui está a mudança principal: usar a imagem da atendente para o assistente
    avatar_url = atendente_img_url if msg["role"] == "assistant" else "https://api.dicebear.com/7.x/personas/svg?seed=Client"
    
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
