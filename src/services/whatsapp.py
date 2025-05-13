import requests
import logging
import streamlit as st
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class WhatsAppService:
    """
    Serviço para integração com a API do WhatsApp Business.
    Responsável por enviar mensagens via WhatsApp.
    """
    
    def __init__(self):
        # Tentar obter configurações do secrets
        try:
            self.api_token = st.secrets.get("whatsapp", {}).get("api_token", "")
            self.phone_number_id = st.secrets.get("whatsapp", {}).get("phone_number_id", "")
            self.api_version = st.secrets.get("whatsapp", {}).get("api_version", "v17.0")
            self.api_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"
        except Exception as e:
            logger.warning(f"Não foi possível carregar configurações WhatsApp: {str(e)}")
            self.api_token = ""
            self.phone_number_id = ""
            self.api_version = "v17.0"
            self.api_url = "https://graph.facebook.com/v17.0/messages"
    
    def send_message(self, to, message_text):
        """
        Envia mensagem de texto via WhatsApp
        
        Args:
            to (str): Número do destinatário (com código do país, ex: 5511987654321)
            message_text (str): Texto da mensagem
            
        Returns:
            bool: True se enviado com sucesso, False em caso de erro
        """
        # Se não tiver token configurado, apenas logar
        if not self.api_token or not self.phone_number_id:
            logger.info(f"[MOCK] Enviando mensagem para {to}: {message_text}")
            return True
        
        try:
            # Preparar payload
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": "text",
                "text": {
                    "body": message_text
                }
            }
            
            # Preparar headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}"
            }
            
            # Enviar requisição
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Mensagem enviada com sucesso para {to}")
                return True
            else:
                logger.error(f"Erro ao enviar mensagem: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem WhatsApp: {str(e)}")
            return False
    
    def send_template(self, to, template_name, template_params=None):
        """
        Envia mensagem utilizando template do WhatsApp
        
        Args:
            to (str): Número do destinatário
            template_name (str): Nome do template
            template_params (list): Parâmetros do template
            
        Returns:
            bool: True se enviado com sucesso, False em caso de erro
        """
        # Se não tiver token configurado, apenas logar
        if not self.api_token or not self.phone_number_id:
            logger.info(f"[MOCK] Enviando template {template_name} para {to}")
            return True
        
        try:
            # Preparar componentes do template
            components = []
            if template_params:
                components.append({
                    "type": "body",
                    "parameters": template_params
                })
            
            # Preparar payload
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": "pt_BR"
                    },
                    "components": components
                }
            }
            
            # Preparar headers
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_token}"
            }
            
            # Enviar requisição
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Template enviado com sucesso para {to}")
                return True
            else:
                logger.error(f"Erro ao enviar template: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Erro ao enviar template WhatsApp: {str(e)}")
            return False
