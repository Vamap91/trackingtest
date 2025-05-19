import streamlit as st
import requests
import json
import time
import re
import openai
import base64
from pathlib import Path

# Configuração da página - DEVE ser a primeira chamada Streamlit
st.set_page_config(
    page_title="CarGlass - Assistente Virtual",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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
        {"role": "assistant", "content": "Olá! Sou a Clara e estou aqui para ajudar com informações sobre seu atendimento, status do serviço e esclarecer qualquer dúvida que você tenha! 😊 Por favor, digite seu CPF, telefone, placa do veículo, número da ordem ou chassi para começarmos."}
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
    """Função para buscar dados do cliente através da API ou dados simulados"""
    
    # Configuração - modo de simulação para testes
    USAR_DADOS_SIMULADOS = True  # Alternar para False quando usar localmente com API real
    
    if USAR_DADOS_SIMULADOS:
        # Mostrar banner de ambiente de teste
        st.warning("⚠️ AMBIENTE DE TESTE - Usando dados simulados com base na estrutura real")
        
        # Simular um pequeno atraso como em chamada real
        time.sleep(1)
        
        # Definir mapeamentos com base nas informações do desenvolvedor
        status_mappings = {
            # OrderAffiliateSubStatusId -> SubStatus
            None: "Ordem de Serviço Aberta",
            1: "Negociar Carglass", 
            7: "Agendar cliente",
            10: "Confirmar Execução", 
            12: "Análise Auditoria",
            29: "Aguardar Vistoria",
            32: "Acompanhar Peça"
        }
        
        inspection_status = {
            "Aguardando Fotos": "Aguardando fotos para liberação",
            "Realizar Vistoria": "Fotos Recebidas",
            "Vistoria Realizada": "Peça Identificada",
            None: ""
        }
        
        # Dados simulados baseados em exemplos reais do Excel
        ordem_data = {
            "2653636": {"subStatusId": 7, "inspectionStatus": None, "veiculo": "S10 Pick-Up LS 2.8", "placa": "EUH6E61", "ano": "2022", "servico": "Parabrisa"},
            "2653624": {"subStatusId": 1, "inspectionStatus": None, "veiculo": "Strada Freedom 1.3", "placa": "CAR0009", "ano": "2024", "servico": "Farol Direito/Passageiro"},
            "2653623": {"subStatusId": 12, "inspectionStatus": None, "veiculo": "Fox Connect 1.6", "placa": "CAR0015", "ano": "2022", "servico": "Under Car"},
            "2653621": {"subStatusId": 1, "inspectionStatus": None, "veiculo": "Strada Freedom 1.3", "placa": "CAR0009", "ano": "2024", "servico": "Farol Esquerdo/Motorista"},
            "2653616": {"subStatusId": 1, "inspectionStatus": None, "veiculo": "CITY Sedan EX 1.5", "placa": "FVO1D28", "ano": "2014", "servico": "Parabrisa"}
        }
        
        # Mapear CPFs e telefones fictícios para ordens 
        cpf_ordem = {
            "12345678900": "2653636",
            "98765432100": "2653624", 
            "11122233344": "2653623"
        }
        
        telefone_ordem = {
            "11987654321": "2653636",
            "21987654321": "2653624",
            "31987654321": "2653623"
        }
        
        # Determinar a ordem com base no tipo de identificador
        ordem_id = None
        if tipo == "ordem":
            ordem_id = valor
        elif tipo == "cpf" and valor in cpf_ordem:
            ordem_id = cpf_ordem[valor]
        elif tipo == "telefone" and valor in telefone_ordem:
            ordem_id = telefone_ordem[valor]
        elif tipo == "placa":
            # Buscar por placa
            for oid, data in ordem_data.items():
                if data["placa"] == valor.upper():
                    ordem_id = oid
                    break
        
        # Se encontrou uma ordem válida
        if ordem_id and ordem_id in ordem_data:
            ordem_info = ordem_data[ordem_id]
            
            # Determinar o status com base na lógica fornecida pelo desenvolvedor
            sub_status_id = ordem_info["subStatusId"]
            inspection_status_name = ordem_info["inspectionStatus"]
            
            # Aplicar lógica para determinar o status baseado nas regras fornecidas
            status_description = status_mappings.get(sub_status_id, "Status não identificado")
            
            # Adicionar informação do inspection status quando relevante
            if inspection_status_name:
                inspection_info = inspection_status.get(inspection_status_name, "")
                if inspection_info:
                    status_description = inspection_info
            
            # Determinar status principal com base no SubStatus
            if sub_status_id == 10:  # ConfirmarExecução
                main_status = "Concluído"
            elif sub_status_id in [7, 32]:  # Agendarcliente, AcompanharPeça
                main_status = "Em andamento"
            else:
                main_status = "Agendado"
                
            # Criar mock com dados simulados
            mock_data = {
                "sucesso": True,
                "tipo": tipo,
                "valor": valor,
                "dados": {
                    "nome": "Cliente Teste",
                    "cpf": "123.456.789-00" if tipo == "cpf" else "N/A",
                    "telefone": "(11) 98765-4321" if tipo == "telefone" else "N/A",
                    "ordem": ordem_id,
                    "status": main_status,
                    "subStatus": status_description,
                    "tipo_servico": ordem_info["servico"],
                    "veiculo": {
                        "modelo": ordem_info["veiculo"],
                        "placa": ordem_info["placa"],
                        "ano": ordem_info["ano"]
                    }
                }
            }
            
            return mock_data
        else:
            # Não encontrou a ordem ou o identificador não está mapeado
            return None
    
    else:
        # Usar a API real (para ambiente interno com acesso VPN)
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
        api_key = st.secrets["openai"]["api_key"]
        client = openai.OpenAI(api_key=api_key)
        has_api_key = True
    except (KeyError, TypeError):
        has_api_key = False
    
    if not has_api_key:
        st.warning("⚠️ AMBIENTE DE TESTE - API OpenAI não configurada. Usando respostas simuladas.")
        
        # Extrair dados do cliente para resposta simulada
        dados = client_data.get("dados", {})
        nome = dados.get("nome", "Cliente")
        sub_status = dados.get("subStatus", "")
        
        # Verificar se o input contém palavras-chave sobre mudança de prestador
        mudanca_patterns = ["mudar", "trocar", "outra oficina", "outro prestador", "mudança", "prestador", "preferencial", "cidade"]
        has_mudanca_intent = any(pattern in user_input.lower() for pattern in mudanca_patterns)
        
        if has_mudanca_intent:
            # Resposta simulada para mudança de prestador
            cidade_patterns = ["cidade", "local", "localidade", "município", "outra cidade"]
            if any(pattern in user_input.lower() for pattern in cidade_patterns):
                # Mudança de cidade
                return f"""
                Entendo que você deseja mudar o local de atendimento para outra cidade.
                
                A troca de cidade será realizada. Temos um prazo de 48 horas para encaminhar, via link, as informações do agendamento.
                
                Nossa equipe realizará a troca no sistema e entrará em contato com a oficina da cidade indicada para liberar o atendimento. Há algo mais em que eu possa ajudar?
                """
            else:
                # Mudança para prestador preferencial
                return f"""
                Entendo que você gostaria de mudar para um prestador preferencial.
                
                A troca de oficina será realizada. Temos um prazo de 48 horas para encaminhar, via link, as informações do agendamento.
                
                Nossa equipe entrará em contato com a oficina para liberar o atendimento via telefone e/ou email. Posso ajudar com mais alguma coisa?
                """
        else:
            # Resposta simulada para consulta de status
            status_response = ""
            if "Agendar cliente" in sub_status:
                status_response = "Nossa equipe entrará em contato em breve para agendar seu atendimento. Temos um prazo de 48 horas para realizar este contato."
            elif "Negociar Carglass" in sub_status:
                status_response = "Estamos verificando disponibilidade, peças e condições para o serviço solicitado. Nossa equipe entrará em contato assim que tivermos novidades."
            elif "Análise Auditoria" in sub_status:
                status_response = "Seu atendimento está na fase de análise pela nossa auditoria. Este é um procedimento padrão para garantir a qualidade do serviço."
            else:
                status_response = f"Seu atendimento está atualmente com status: {sub_status}. Você pode acompanhar as atualizações do seu atendimento por aqui ou entrar em contato com nossa central: 0800-727-2327."
            
            return f"""
            Olá {nome}! Com base nos dados do seu atendimento, posso informar que:
            
            {status_response}
            
            Posso ajudar com mais alguma informação? 😊
            """
    
    try:
        # Extrair dados do cliente
        dados = client_data.get("dados", {})
        nome = dados.get("nome", "Cliente")
        status = dados.get("status", "Em processamento")
        ordem = dados.get("ordem", "N/A")
        sub_status = dados.get("subStatus", "")
        
        # Informações adicionais sobre mudança de prestador para o contexto da IA
        mudanca_info = """
        Se o cliente solicitar mudança de prestador, existem dois cenários:
        
        1. Mudança para prestador preferencial:
           - A troca de oficina será realizada
           - Prazo de 48 horas para encaminhar, via link, as informações do agendamento
           - Equipe entra em contato com a oficina para liberar o atendimento
           
        2. Mudança de cidade:
           - A troca de cidade será realizada
           - Prazo de 48 horas para encaminhar o agendamento
           - Equipe realiza a troca no sistema e contata a oficina da cidade indicada
        
        Importante: Para qualquer mudança, a oficina precisa estar credenciada e ter disponibilidade.
        """
        
        # Construir prompt para o GPT-4 Turbo com personalidade mais amigável
        system_message = f"""
        Você é Clara, assistente virtual da CarGlass, amigável, prestativa e especializada em atendimento ao cliente.
        
        Personalidade: Use um tom amigável, caloroso e empático. Seja conversacional e natural como uma atendente humana que se importa.
        Refira-se ao cliente pelo nome quando possível. Use linguagem simples e direta, evitando termos técnicos desnecessários.
        Ocasionalmente use emojis adequados (😊, 👍, etc.) para tornar a conversa mais amigável, mas sem exagerar.
        
        Você está conversando com {nome}, que tem um atendimento com as seguintes informações:
        - Status: {status}
        - Situação: {sub_status}
        - Ordem: {ordem}
        - Serviço: {dados.get('tipo_servico', 'N/A')}
        - Veículo: {dados.get('veiculo', {}).get('modelo', 'N/A')} - {dados.get('veiculo', {}).get('ano', 'N/A')}
        - Placa: {dados.get('veiculo', {}).get('placa', 'N/A')}
        
        {mudanca_info}
        
        Instruções adicionais para SubStatus específicos:
        - "Agendar cliente": Explique que a equipe entrará em contato para agendar o atendimento (prazo de 48h)
        - "Negociar Carglass": Informe que estamos verificando disponibilidade, peças e condições
        - "Análise Auditoria": Explique que é um procedimento padrão de qualidade
        
        Forneça respostas úteis, empáticas e precisas com base no contexto do atendimento.
        Identifique se o cliente está perguntando sobre status ou solicitando mudança de prestador.
        Limite suas respostas a no máximo 3 parágrafos. Seja concisa e direta.
        Não invente informações que não estão no contexto.
        Se não souber a resposta, sugira contatar a central de atendimento de forma amigável.
        
        Quando apropriado, mostre entusiasmo com pequenas expressões como "Claro!", "Com prazer!" ou "Sem problema!" no início das respostas.
        """
        
        # Chamada para o modelo GPT-4 Turbo da OpenAI
        response = client.chat.completions.create(
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
                sub_status = dados.get("subStatus", "")
                
                # Exibir mensagem personalizada com os dados
                status_tag = ""
                if status.lower() == "concluído":
                    status_tag = '<span class="status-tag complete">Concluído</span>'
                elif status.lower() == "em andamento":
                    status_tag = '<span class="status-tag progress">Em andamento</span>'
                else:
                    status_tag = '<span class="status-tag scheduled">Agendado</span>'
                
                # Usa mensagem mais conversacional
                response_message = f"""
                Olá {nome}! 😊 Encontrei suas informações.
                
                Seu atendimento está com status: {status_tag}
                Situação atual: {sub_status}
                
                Ordem de serviço: {ordem}
                Serviço: {dados.get('tipo_servico', 'N/A')}
                
                Como posso ajudar você hoje? Você pode me perguntar sobre detalhes do seu atendimento, previsão de conclusão ou solicitar mudança de prestador.
                
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
        {"role": "assistant", "content": "Olá! Sou a Clara, assistente virtual da CarGlass. Estou aqui para ajudar com informações sobre seu atendimento, status do serviço e esclarecer qualquer dúvida que você tenha! 😊 Por favor, digite seu CPF, telefone, placa do veículo, número da ordem ou chassi para começarmos."}
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
    <p>© 2025 CarGlass Brasil - Em teste e criado por Vinicius Paschoa</p>
    <p>Central de Atendimento: 0800-727-2327 | WhatsApp: (11) 4003-8070</p>
</div>
""", unsafe_allow_html=True)
