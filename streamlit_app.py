import streamlit as st
import requests
import json

st.title('Consulta de Cliente CarGlass')
st.subheader('Interface para teste do webhook n8n')

# Alerta sobre o modo de teste
st.warning("""
**IMPORTANTE - Modo de Teste**: 
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
    # URL do seu webhook n8n - usando exatamente o link que você já tem
    webhook_url = "https://carglasspaschoa.app.n8n.cloud/webhook-test/18504dee-bedd-462d-874a-df828daff30c"
    
    # Preparar os dados para enviar
    payload = {
        "tipo": tipo_consulta,  # Já usando o valor em minúsculo do selectbox
        "valor": valor
    }
    
    # Verificar se há um valor inserido
    if not valor:
        st.error("Por favor, insira um valor para consulta.")
    else:
        try:
            # Fazer a requisição POST para o webhook
            with st.spinner('Aguarde, realizando consulta...'):
                response = requests.post(webhook_url, json=payload)
            
            # Verificar a resposta
            if response.status_code == 200:
                result = response.json()
                st.success("Consulta realizada com sucesso!")
                
                # Exibir os dados retornados de forma organizada
                st.subheader("Resultado da consulta:")
                st.json(result)
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
       - Clique no botão 'Test workflow' que você adicionou no canvas
       - Isso ativará o webhook temporariamente para UMA chamada
    
    2. **Faça a consulta**:
       - Selecione o tipo de consulta (CPF, Telefone ou Ordem)
       - Digite o valor correspondente
       - Clique em "Consultar"
    
    3. **Se receber erro 404**:
       - O webhook não está ativo ou já foi usado
       - Volte ao n8n e clique novamente no botão 'Test workflow'
       - Retorne a esta página e tente a consulta novamente
    
    ### Limitações do modo de teste:
    
    No ambiente de teste do n8n, os webhooks são temporários e funcionam apenas para uma única chamada após ativar o modo de teste. Para testes contínuos, você precisaria:
    
    - Ativar seu fluxo no n8n (modo de produção)
    - Ou clicar no botão 'Test workflow' antes de cada consulta nesta interface
    """)
