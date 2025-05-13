from fastapi import FastAPI, Request, Response, Depends, HTTPException
import logging
import json
import hmac
import hashlib
from src.core.orchestrator import ActionOrchestrator
from src.core.session_manager import SessionManager
from src.core.service_registry import ServiceRegistry
from src.services.whatsapp import WhatsAppService

# Configurar logging
logger = logging.getLogger(__name__)

# Criar aplicação FastAPI
app = FastAPI(title="CarGlass WhatsApp Gateway")

# Injeção de dependências
def get_orchestrator():
    registry = ServiceRegistry()
    storage = registry.get("storage_client")
    session_manager = SessionManager(storage)
    return ActionOrchestrator(session_manager, registry)

def get_whatsapp_service():
    registry = ServiceRegistry()
    return registry.get("whatsapp_service")

@app.get("/")
async def root():
    """Endpoint de verificação de saúde"""
    return {"status": "online", "service": "CarGlass WhatsApp Gateway"}

@app.get("/webhook")
async def verify_webhook(request: Request):
    """
    Endpoint para verificação do webhook do WhatsApp (desafio de autenticação)
    """
    # Obter parâmetros da query
    params = dict(request.query_params)
    
    # Verificar se é uma solicitação de verificação
    if "hub.mode" in params and "hub.verify_token" in params:
        mode = params["hub.mode"]
        token = params["hub.verify_token"]
        challenge = params.get("hub.challenge", "")
        
        # Verificar token (deve ser configurado no secrets/config)
        verify_token = "WEBHOOK_VERIFY_TOKEN"  # Em produção, usar st.secrets
        
        if mode == "subscribe" and token == verify_token:
            logger.info("Webhook verificado com sucesso!")
            return Response(content=challenge, media_type="text/plain")
        else:
            logger.warning(f"Falha na verificação do webhook. Token inválido.")
            return Response(status_code=403)
    
    return Response(status_code=400)

@app.post("/webhook")
async def receive_webhook(
    request: Request, 
    orchestrator: ActionOrchestrator = Depends(get_orchestrator),
    whatsapp_service: WhatsAppService = Depends(get_whatsapp_service)
):
    """
    Endpoint para receber mensagens do WhatsApp
    """
    try:
        # Obter corpo da requisição
        body = await request.body()
        
        # Verificar assinatura (em produção)
        # self._verify_signature(request, body)
        
        # Processar payload
        payload = await request.json()
        logger.debug(f"Webhook recebido: {json.dumps(payload)}")
        
        # Verificar tipo de evento
        if "object" in payload and payload["object"] == "whatsapp_business_account":
            for entry in payload.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    
                    if "messages" in value:
                        for message in value["messages"]:
                            # Extrair informações da mensagem
                            sender = message.get("from")
                            message_id = message.get("id")
                            
                            # Extrair conteúdo da mensagem
                            if "text" in message:
                                # Mensagem de texto
                                content = message["text"]["body"]
                                
                                # Processar a mensagem
                                response = orchestrator.process_input(
                                    user_input=content,
                                    channel="whatsapp",
                                    user_id=sender
                                )
                                
                                # Enviar resposta de volta
                                whatsapp_service.send_message(sender, response)
                                
                                logger.info(f"Mensagem processada - De: {sender}, ID: {message_id}")
                            
                            # Suporte para outros tipos de mensagem (futuramente)
                            # elif "image" in message:
                            #     # Processar imagem
                            #     pass
        
        # Sempre responder com 200 OK para o webhook
        return Response(status_code=200)
    
    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}")
        # Sempre responder com 200 OK para o webhook (requisito da plataforma)
        return Response(status_code=200)
    
    def _verify_signature(self, request, body):
        """Verifica assinatura do webhook (em produção)"""
        signature = request.headers.get("X-Hub-Signature-256", "")
        
        if not signature:
            logger.warning("Sem assinatura no cabeçalho")
            return False
        
        # Verificar assinatura (em produção, usar st.secrets para a chave)
        app_secret = "YOUR_APP_SECRET"
        
        # Calcular assinatura esperada
        expected_signature = "sha256=" + hmac.new(
            app_secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        # Comparar assinaturas
        if not hmac.compare_digest(signature, expected_signature):
            logger.warning("Assinatura inválida no webhook")
            raise HTTPException(status_code=403, detail="Invalid signature")
        
        return True
