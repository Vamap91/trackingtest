import streamlit as st
import requests
import json
import time

# Configuração da página
st.set_page_config(
    page_title="CarGlass - Consulta de Atendimento",
    page_icon="🚗",
    layout="centered"
)

# Título e descrição
st.title('Consulta de Cliente CarGlass')
st.subheader('Interface para teste do webhook n8n')

# Alerta sobre o modo de teste
st.warning("""
**IMPORTANTE - Modo de Teste:**
1. Antes de fazer uma consulta, você precisa clicar no botão 'Test workflow' no canvas do n8n
2. Cada clique no botão 'Test workflow' permite apenas UMA chamada ao webhook
3. Se receber erro 404, volte ao n8n e clique novamente no botão 'Test workflow'
""")

# Criar o formulário
with st.form("consulta_form"):
    tipo_consulta = st.selectbox(
        'Selecione o tipo de consulta:',
        ('cpf', 'telefone', 'ordem')
    )
    
    # Campo de entrada com validação diferente dependendo do tipo
    if tipo_consulta == 'cpf':
        valor = st.text_input('Digite o CPF (apenas números):', max_chars=11)
        st.caption("Ex: 12345678900")
    elif tipo_consulta == 'telefone':
        valor = st.text_input('Digite o telefone (com DDD, apenas números):', max_chars=11)
        st.caption("Ex: 11987654321")
    else:  # Ordem
        valor = st.text_input('Digite o número da ordem:')
        st.caption("Ex: ORD123456")
    
    # Botão de submit
    submitted = st.form_submit_button("Consultar")

# Processar o formulário quando for enviado
if submitted:
    # URL do webhook n8n
    webhook_url = "https://carglasspaschoa.app.n8n.cloud/webhook-test/18504dee-bedd-462d-874a-df828daff30c"
    
    # Preparar os dados para enviar
    payload = {
        "tipo": tipo_consulta,
        "valor": valor
    }
    
    # Verificar se há um valor inserido
    if not valor:
        st.error("Por favor, insira um valor para consulta.")
    else:
        try:
            # Fazer a requisição POST para o webhook
            with st.spinner('Aguarde, realizando consulta...'):
                # Simular um pequeno delay para melhor experiência do usuário
                time.sleep(0.5)
                response = requests.post(webhook_url, json=payload)
            
            # Verificar a resposta
            if response.status_code == 200:
                result = response.json()
                
                # Verifica se há dados
                if result.get("sucesso", False):
                    st.success("Consulta realizada com sucesso!")
                else:
                    st.warning("Não foram encontrados registros para esta consulta")
                
                # Exibe a mensagem da IA em destaque
                if "mensagem_ia" in result:
                    st.markdown("### Mensagem da CarGlass")
                    st.markdown(f'<div style="background-color:#f0f7ff; padding:20px; border-radius:10px; border-left:5px solid #0066cc;">{result["mensagem_ia"]}</div>', unsafe_allow_html=True)
                
                # Exibe os dados técnicos em uma seção expansível
                with st.expander("Detalhes técnicos"):
                    dados = result.get("dados", {})
                    
                    if dados:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("Informações do Cliente")
                            st.write(f"**Nome:** {dados.get('nome', 'Não informado')}")
                            st.write(f"**CPF:** {dados.get('cpf', 'Não informado')}")
                            st.write(f"**Telefone:** {dados.get('telefone', 'Não informado')}")
                        
                        with col2:
                            st.subheader("Informações do Serviço")
                            st.write(f"**Ordem:** {dados.get('ordem', 'Não informado')}")
                            st.write(f"**Status:** {dados.get('status', 'Não informado')}")
                            st.write(f"**Tipo de Serviço:** {dados.get('tipo_servico', 'Não informado')}")
                        
                        # Informações do veículo se disponíveis
                        if "veiculo" in dados:
                            veiculo = dados.get('veiculo', {})
                            st.subheader("Informações do Veículo")
                            st.write(f"**Modelo:** {veiculo.get('modelo', 'Não informado')}")
                            st.write(f"**Placa:** {veiculo.get('placa', 'Não informado')}")
                            st.write(f"**Ano:** {veiculo.get('ano', 'Não informado')}")
                    else:
                        st.info("Não há detalhes técnicos disponíveis para esta consulta")
                
            elif response.status_code == 404:
                st.error("Webhook não encontrado ou não ativado.")
                st.info("""
                **Para resolver:**
                1. Abra o n8n e clique no botão 'Test workflow' no canvas
                2. Volte para esta página e tente novamente
                3. Lembre-se: cada clique no botão 'Test workflow' permite apenas UMA consulta
                """)
            else:
                st.error(f"Erro ao consultar: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"Ocorreu um erro na requisição: {str(e)}")
            st.info("Verifique se o webhook está ativo e configurado corretamente.")

# Seção de ajuda
with st.expander("Como usar esta interface de teste"):
    st.markdown("""
    ### Instruções:
    
    1. **Prepare o n8n**:
       - Abra seu fluxo no n8n
       - Clique no botão 'Test workflow' no canvas
       - Isso ativará o webhook temporariamente para UMA chamada
    
    2. **Faça a consulta**:
       - Selecione o tipo de consulta (CPF, Telefone ou Ordem)
       - Digite o valor correspondente
       - Clique em "Consultar"
    
    3. **Se receber erro 404**:
       - O webhook não está ativo ou já foi usado
       - Volte ao n8n e clique novamente no botão 'Test workflow'
       - Retorne a esta página e tente a consulta novamente
    
    ### Canais de Contato da CarGlass:
    
    - **Central de Atendimento**: 0800-727-2327
    - **WhatsApp**: (11) 4003-8070
    - **Site**: [www.carglass.com.br](https://www.carglass.com.br)
    """)

# Rodapé
st.markdown("""
<div style="margin-top: 50px; text-align: center; color: #666;">
    <p>© 2025 CarGlass Brasil - Sistema de Consulta de Atendimento</p>
</div>
""", unsafe_allow_html=True)
