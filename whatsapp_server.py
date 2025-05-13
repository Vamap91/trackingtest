"""
Servidor para receber webhooks do WhatsApp
Executar com: uvicorn whatsapp_server:app --host 0.0.0.0 --port 8000
"""

import uvicorn
from src.channels.whatsapp.gateway import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
