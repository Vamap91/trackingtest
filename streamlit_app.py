import streamlit as st
import re

# Configuração da página - DEVE ser a primeira chamada Streamlit
st.set_page_config(
    page_title="CarGlass - Assistente Virtual",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado - simplificado
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    * {font-family: 'Inter', sans-serif;}
    
    .main-header {text-align: center; margin-bottom: 1.5rem;}
    
    .chat-message {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 8px;
        display: flex;
        align-items: flex-start;
    }
    
    .chat-message.user {background-color: #e6f3ff;}
    .chat-message.assistant {
        background-color: #f0f7ff;
        border-left: 4px solid #0066cc;
    }
    
    .chat-message .avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        margin-right: 10px;
    }
    
    .chat-message .message {flex-grow: 1;}
    
    .footer {
        text-align: center;
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid #eee;
        color: #666;
        font-size: 0.8rem;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Cabeçalho
st.markdown('<div class="main-header"><img src="https://www.carglass.com.br/wp-content/uploads/2023/02/logoCarglass.png" width="180"></div>', unsafe_allow_html=True)

# Banner de ambiente de teste
st.warning("⚠️ AMBIENTE DE TESTE - Usando dados simulados")

# DADOS SIMULADOS - Hardcoded para garantir desempenho e confiabilidade
DADOS_CLIENTES = {
    # Ordens
    "2653636": {
        "nome": "João Silva",
        "ordem": "2653636",
        "status": "Em andamento 🔄",
        "situacao": "Agendar cliente",
        "servico": "Parabrisa",
        "veiculo": "S10 Pick-Up LS 2.8",
        "placa": "EUH6E61",
        "ano": "2022"
    },
    "2653624": {
        "nome": "Maria Souza",
        "ordem": "2653624",
        "status": "Agendado 📅",
        "situacao": "Negociar Carglass",
        "servico": "Farol Direito/Passageiro",
        "veiculo": "Strada Freedom 1.3",
        "placa": "CAR0009",
        "ano": "2024"
    },
    "2653623": {
        "nome": "Carlos Ferreira",
        "ordem": "2653623",
        "status": "Agendado 📅",
        "situacao": "Análise Auditoria",
        "servico": "Under Car",
        "veiculo": "Fox Connect 1.6",
        "placa": "CAR0015",
        "ano": "2022"
    },
    
    # CPFs
    "12345678900": {
        "nome": "João Silva",
        "ordem": "2653636",
        "status": "Em andamento 🔄",
        "situacao": "Agendar cliente",
        "servico": "Parabrisa",
        "veiculo": "S10 Pick-Up LS 2.8",
        "placa": "EUH6E61",
        "ano": "2022"
    },
    
    # Telefones
    "11987654321": {
        "nome": "João Silva",
        "ordem": "2653636",
        "status": "Em andamento 🔄",
        "situacao": "Agendar cliente",
        "servico": "Parabrisa",
        "veiculo": "S10 Pick-Up LS 2.8",
        "placa": "EUH6E61",
        "ano": "2022"
    },
    
    # Placas
    "EUH6E61": {
        "nome": "João Silva",
        "ordem": "2653636",
        "status": "Em andamento 🔄",
        "situacao": "Agendar cliente",
        "servico": "Parabrisa",
        "veiculo": "S10 Pick-Up LS 2.8",
        "placa": "EUH6E61",
        "ano": "2022"
    }
}

# Mapeamento para respostas rápidas baseadas em palavras-chave
RESPOSTAS_RAPIDAS = {
    "mudanca_prestador": """
    Entendo que você gostaria de mudar para um prestador preferencial.
    
    A troca de oficina será realizada. Temos um prazo de 48 horas para encaminhar, via link, as informações do agendamento.
    
    Nossa equipe entrará em contato com a oficina para liberar o atendimento via telefone e/ou email. Posso ajudar com mais alguma coisa?
    """,
    
    "mudanca_cidade": """
    Entendo que você deseja mudar o local de atendimento para outra cidade.
    
    A troca de cidade será realizada. Temos um prazo de 48 horas para encaminhar, via link, as informações do agendamento.
    
    Nossa equipe realizará a troca no sistema e entrará em contato com a oficina da cidade indicada para liberar o atendimento. Há algo mais em que eu possa ajudar?
    """,
    
    "status_agendar": """
    Nossa equipe entrará em contato em breve para agendar seu atendimento. Temos um prazo de 48 horas para realizar este contato.
    
    Você receberá uma ligação ou mensagem para definir a data e horário mais convenientes.
    
    Posso ajudar com mais alguma informação?
    """,
    
    "status_negociar": """
    Estamos verificando disponibilidade, peças e condições para o serviço solicitado. 
    
    Nossa equipe entrará em contato assim que tivermos novidades, normalmente dentro de 24-48 horas.
    
    Posso esclarecer mais alguma dúvida?
    """,
    
    "status_auditoria": """
    Seu atendimento está na fase de análise pela nossa auditoria. Este é um procedimento padrão para garantir a qualidade do serviço.
    
    Esta etapa geralmente leva até 24 horas para ser concluída.
    
    Assim que a análise for concluída, entraremos em contato para os próximos passos. Posso ajudar com mais alguma coisa?
    """
}

# Inicializar variáveis de sessão
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou a Clara, assistente virtual da CarGlass. Estou aqui para ajudar com informações sobre seu atendimento! 😊 Por favor, digite seu CPF, telefone, placa do veículo, número da ordem ou chassi para começarmos."}
    ]

if "identificado" not in st.session_state:
    st.session_state.identificado = False

if "cliente_dados" not in st.session_state:
    st.session_state.cliente_dados = None

# Função simplificada para identificar o cliente
def identificar_cliente(input_text):
    # Limpar o input
    clean_text = re.sub(r'[^a-zA-Z0-9]', '', input_text)
    
    # Verificar CPF (11 dígitos)
    if re.match(r'^\d{11}$', clean_text) and clean_text in DADOS_CLIENTES:
        return "cpf", DADOS_CLIENTES[clean_text]
    
    # Verificar telefone (10-11 dígitos)
    if re.match(r'^\d{10,11}$', clean_text) and clean_text in DADOS_CLIENTES:
        return "telefone", DADOS_CLIENTES[clean_text]
    
    # Verificar ordem (5-8 dígitos ou começando com ORD)
    if (re.match(r'^\d{5,8}$', clean_text) or clean_text.upper().startswith("ORD")) and clean_text in DADOS_CLIENTES:
        return "ordem", DADOS_CLIENTES[clean_text]
    
    # Verificar placa
    placa_upper = clean_text.upper()
    if (re.match(r'^[A-Z]{3}\d{4}$', placa_upper) or re.match(r'^[A-Z]{3}\d[A-Z]\d{2}$', placa_upper)) and placa_upper in DADOS_CLIENTES:
        return "placa", DADOS_CLIENTES[placa_upper]
    
    # Verificação direta - para testes
    if clean_text in DADOS_CLIENTES:
        return "identificador", DADOS_CLIENTES[clean_text]
    
    return None, None

# Função para determinar resposta para perguntas
def responder_pergunta(pergunta, cliente_dados):
    pergunta_lower = pergunta.lower()
    
    # Verificar mudança de prestador/cidade
    mudanca_patterns = ["mudar", "trocar", "outra oficina", "outro prestador", "mudança", "preferencial"]
    cidade_patterns = ["cidade", "local", "localidade", "município", "outra cidade"]
    
    if any(pattern in pergunta_lower for pattern in mudanca_patterns):
        if any(pattern in pergunta_lower for pattern in cidade_patterns):
            return RESPOSTAS_RAPIDAS["mudanca_cidade"]
        else:
            return RESPOSTAS_RAPIDAS["mudanca_prestador"]
    
    # Verificar status específicos
    situacao = cliente_dados.get("situacao", "").lower()
    
    if "agendar cliente" in situacao:
        return RESPOSTAS_RAPIDAS["status_agendar"]
    elif "negociar carglass" in situacao:
        return RESPOSTAS_RAPIDAS["status_negociar"]
    elif "análise auditoria" in situacao:
        return RESPOSTAS_RAPIDAS["status_auditoria"]
    
    # Resposta padrão
    return f"""
    Olá {cliente_dados['nome']}! Com base nos dados do seu atendimento, posso informar que:
    
    Seu atendimento para o serviço de {cliente_dados['servico']} no veículo {cliente_dados['veiculo']} está com status: {cliente_dados['status']}
    
    Situação atual: {cliente_dados['situacao']}
    
    Para mais detalhes específicos ou outras dúvidas, estou à disposição. Você também pode entrar em contato com nossa central pelo 0800-727-2327.
    """

# Função para processar a entrada do usuário
def processar_entrada():
    user_input = st.session_state.user_input
    
    if not user_input:
        return
    
    # Adicionar mensagem do usuário
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.user_input = ""  # Limpar campo
    
    # Se ainda não identificou o cliente
    if not st.session_state.identificado:
        tipo, dados = identificar_cliente(user_input)
        
        if dados:
            # Cliente identificado com sucesso
            st.session_state.identificado = True
            st.session_state.cliente_dados = dados
            
            # Gerar mensagem de boas-vindas
            welcome_msg = f"""
            Olá {dados['nome']}! 😊 Encontrei suas informações.
            
            Seu atendimento está com status: {dados['status']}
            Situação atual: {dados['situacao']}
            
            Ordem de serviço: {dados['ordem']}
            Serviço: {dados['servico']}
            Veículo: {dados['veiculo']} - {dados['ano']}
            Placa: {dados['placa']}
            
            Como posso ajudar você hoje? Você pode me perguntar sobre detalhes do seu atendimento, previsão de conclusão ou solicitar mudança de prestador.
            """
            
            st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
        else:
            # Cliente não identificado
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"""
                Não consegui encontrar informações com o identificador fornecido. 😕
                
                Por favor, verifique se digitou corretamente ou tente outro tipo de identificação:
                - CPF (11 dígitos)
                - Telefone (com DDD)
                - Placa do veículo
                - Número da ordem de serviço
                
                Estou aqui para ajudar quando estiver pronto! 👍
                """
            })
    else:
        # Cliente já identificado - processar perguntas
        resposta = responder_pergunta(user_input, st.session_state.cliente_dados)
        st.session_state.messages.append({"role": "assistant", "content": resposta})

# Função para reiniciar conversa
def reiniciar_conversa():
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! Sou a Clara, assistente virtual da CarGlass. Estou aqui para ajudar com informações sobre seu atendimento! 😊 Por favor, digite seu CPF, telefone, placa do veículo, número da ordem ou chassi para começarmos."}
    ]
    st.session_state.identificado = False
    st.session_state.cliente_dados = None

# Mostrar histórico de conversa
for msg in st.session_state.messages:
    avatar = "https://api.dicebear.com/7.x/bottts/svg?seed=CarGlass" if msg["role"] == "assistant" else "https://api.dicebear.com/7.x/personas/svg?seed=Client"
    
    st.markdown(f"""
    <div class="chat-message {msg['role']}">
        <img src="{avatar}" class="avatar" alt="{msg['role']}">
        <div class="message">{msg['content']}</div>
    </div>
    """, unsafe_allow_html=True)

# Campo de entrada e botões
st.text_input(
    "Digite aqui sua mensagem ou identificação", 
    key="user_input",
    on_change=processar_entrada,
    placeholder="CPF, telefone, placa ou ordem de serviço..."
)

col1, col2, col3 = st.columns([3, 2, 3])
with col2:
    st.button("Nova Consulta", on_click=reiniciar_conversa)

# Rodapé
st.markdown("""
<div class="footer">
    <p>© 2025 CarGlass Brasil - Em teste e criado por Vinicius Paschoa</p>
    <p>Central de Atendimento: 0800-727-2327 | WhatsApp: (11) 4003-8070</p>
</div>
""", unsafe_allow_html=True)
