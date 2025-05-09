import streamlit as st
import requests
import json

st.title('Consulta de Cliente CarGlass')
st.subheader('Interface para teste do webhook n8n')

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
            else:
                st.error(f"Erro ao consultar: {response.status_code}")
                st.text(response.text)
        except Exception as e:
            st.error(f"Ocorreu um erro na requisição: {str(e)}")
            st.info("Verifique se o webhook está ativo e configurado corretamente.")
