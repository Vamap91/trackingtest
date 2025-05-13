class ServiceRegistry:
    """
    Registro central de todos os serviços e integrações.
    Implementa padrão Service Locator.
    """
    
    def __init__(self):
        self._services = {}
        self._initialize_default_services()
    
    def register(self, name, service):
        """Registra um serviço"""
        self._services[name] = service
    
    def get(self, name):
        """Obtém um serviço pelo nome"""
        if name not in self._services:
            raise ValueError(f"Service not found: {name}")
        return self._services[name]
    
    def __getattr__(self, name):
        """Acesso conveniente para serviços como propriedades"""
        if name in self._services:
            return self._services[name]
        raise AttributeError(f"No service named '{name}'")
    
    def _initialize_default_services(self):
        """Inicializa serviços padrão"""
        try:
            # Importar serviços
            from src.services.intent_detection import IntentDetector
            from src.services.fusion_api import FusionAPI
            from src.services.response_generator import ResponseGenerator
            from src.services.ai_service import AIService
            from src.services.escalation_service import EscalationService
            from src.core.decision_engine import DecisionEngine
            
            # Registrar serviços essenciais
            self.register("intent_detector", IntentDetector())
            self.register("fusion_api", FusionAPI())
            self.register("response_generator", ResponseGenerator())
            self.register("ai_service", AIService())
            self.register("escalation_service", EscalationService())
            self.register("decision_engine", DecisionEngine())
            
            # Dicionário de ações personalizadas
            self.register("custom_actions", {})
            
            # Registrar storage client (em produção, seria Redis ou outro)
            # Para desenvolvimento, deixamos como None e o SessionManager usará memória
            self.register("storage_client", None)
            
        except ImportError
