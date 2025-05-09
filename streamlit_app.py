import streamlit as st
import requests
import json

st.title('Consulta de Cliente CarGlass')

# Criar o formulário
with st.form("consulta_form"):
    tipo_consulta = st.selectbox(
        'Selecione o tipo de consulta:',
        ('CPF', 'Telefone', 'Ordem')
    )
    
    # Campo de entrada com validação diferente dependendo do tipo
    if tipo_consulta == 'CPF':
        valor = st.text_input('Digite o CPF (apenas números):', max_chars=11)
        placeholder = "Ex: 12345678900"
    elif tipo_consulta == 'Telefone':
        valor = st.text_input('Digite o telefone (com DDD, apenas números):', max_chars=11)
        placeholder = "Ex: 11987654321"
    else:  # Ordem
        valor = st.text_input('Digite o número da ordem:')
        placeholder = "Ex: ORD123456"
    
    # Botão de submit
    submitted = st.form_submit_button("Consultar")

# Processar o formulário quando for enviado
if submitted:
    # URL do seu webhook n8n
    webhook_url = "https://carglasspaschoa.app.n8n.cloud/webhook-test/18504dee-bedd-462d-874a-df828daff30c"
    
    # Preparar os dados para enviar
    payload = {
        "tipo": tipo_consulta.lower(),  # Converter para minúsculo para corresponder ao seu n8n
        "valor": valor
    }
    
    # Verificar se há um valor inserido
    if not valor:
        st.error("Por favor, insira um valor para consulta.")
    else:
        try:
            # Fazer a requisição POST para o webhook
            response = requests.post(webhook_url, json=payload)
            
            # Verificar a resposta
            if response.status_code == 200:
                result = response.json()
                st.success("Consulta realizada com sucesso!")
                
                # Exibir os dados retornados de forma organizada
                st.json(result)
            else:
                st.error(f"Erro ao consultar: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"Ocorreu um erro na requisição: {str(e)}")
