import streamlit as st
import time
import os
from src.core.orchestrator import ActionOrchestrator
from src.core.session_manager import SessionManager
from src.core.service_registry import ServiceRegistry

# Inicializar componentes core
registry = ServiceRegistry()
storage = registry.get("storage_client")
session_manager = SessionManager(storage)
orchestrator = ActionOrchestrator(session_manager, registry)

# Configuração da página
st.set_page_config(
    page_title="CarGlass - Assistente Virtual",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Carregar CSS personalizado
css_path = os.path.join("assets", "styles.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    logo_path = os.path.join("assets", "logo.png")
    if os.path.exists(logo_path):
        st.image(logo_path, width=200)
    else:
        st.markdown('<div class="main-header"><h1>CarGlass</h1></div>', unsafe_allow_html=True)

# Inicializar estado da sessão Streamlit
if "session_id" not in st.session_state:
    st.session_state.session_id = f"web_{int(time.time())}"

# Obter sessão do usuário
session = session_manager.get_session("web", st.session_state.session_id)
conversation_history = session.get_conversation_history()

# Exibir histórico de mensagens
for msg in conversation_history:
    avatar_url = "https://api.dicebear.com/7.x/bottts/svg?seed=CarGlass" if msg["role"] == "assistant" else "https://api.dicebear.com/7.x/personas/svg?seed=Client"
    
    with st.container():
        st.markdown(f"""
        <div class="chat-message {msg['role']}">
            <img src="{avatar_url}" class="avatar" alt="{msg['role']}">
            <div class="message">{msg['content']}</div>
        </div>
        """, unsafe_allow_html=True)

# Função para processar entrada do usuário
def process_user_input():
    user_input = st.session_state.user_input
    
    if not user_input:
        return
    
    # Adicionar mensagem do usuário ao histórico
    session.add_message("user", user_input)
    
    # Processar entrada através do orquestrador
    with st.spinner("Processando..."):
        response = orchestrator.process_input(
            user_input=user_input,
            channel="web",
            user_id=st.session_state.session_id
        )
    
    # Adicionar resposta do assistente ao histórico
    session.add_message("assistant", response)
    
    # Limpar campo de entrada
    st.session_state.user_input = ""

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
        if st.button("Nova Consulta"):
            # Reiniciar sessão
            session.reset()
            st.rerun()

# Footer
st.markdown("""
<div class="footer" style="text-align: center; margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #eee; color: #666;">
    <p>© 2025 CarGlass Brasil - Assistente Virtual</p>
    <p>Central de Atendimento: 0800-727-2327 | WhatsApp: (11) 4003-8070</p>
</div>
""", unsafe_allow_html=True)
