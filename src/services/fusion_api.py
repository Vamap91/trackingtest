import requests
import json
import streamlit as st
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)

class FusionAPI:
    """
    Serviço para integração com a API Fusion da CarGlass.
    Responsável por consultas de status por diferentes identificadores.
    """
    
    def __init__(self):
        # Tentar obter configurações de ambiente do secrets
        try:
            self.environment = st.secrets.get("api", {}).get("environment", "dev")
            self.base_urls = {
                "dev": st.secrets.get("api", {}).get("base_url_dev", "http://fusion-dev.carglass.dev.local:3000/api"),
                "hml": st.secrets.get("api", {}).get("base_url_hml", "http://fusion-hml.carglass.hml.local:3000/api"),
                "prod": st.secrets.get("api", {}).get("base_url_prod", "https://fusion.carglass.com.br/api")
            }
        except Exception as e:
            # Fallback para desenvolvimento local
            logger.warning(f"Não foi possível carregar configurações: {str(e)}")
            self.environment = "dev"
            self.base_urls = {
                "dev": "http://fusion-dev.carglass.dev.local:3000/api",
                "hml": "http://fusion-hml.carglass.hml.local:3000/api",
                "prod": "https://fusion.carglass.com.br/api"
            }
    
    def get_client_data(self, id_type, identifier):
        """
        Consulta dados do cliente na API Fusion
        
        Args:
            id_type (str): Tipo de identificador (cpf, telefone, placa, ordem, chassi)
            identifier (str): Valor do identificador
            
        Returns:
            dict: Dados do cliente ou None em caso de erro
        """
        # Em ambiente de desenvolvimento sem acesso à API real, usar dados simulados
        if self.environment == "dev" or self._is_offline():
            return self._get_mock_data(id_type, identifier)
        
        try:
            # Construir URL da API
            base_url = self.base_urls.get(self.environment)
            url = f"{base_url}/status/{id_type}/{identifier}"
            
            # Headers da requisição
            headers = {
                "Accept": "application/json"
            }
            
            # Fazer a requisição GET para a API
            response = requests.get(url, headers=headers, timeout=10)
            
            # Verificar se a resposta foi bem-sucedida
            if response.status_code == 200:
                # Tentar converter a resposta para JSON
                data = response.json()
                
                # Formatar resposta para o padrão esperado pela aplicação
                return self._format_response(data, id_type, identifier)
            else:
                # Log de erro
                logger.error(f"Erro na API Fusion: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            # Log de erro
            logger.error(f"Erro ao consultar API Fusion: {str(e)}")
            return None
    
    def _format_response(self, api_data, id_type, identifier):
        """Formata a resposta da API para o padrão esperado pela aplicação"""
        try:
            return {
                "sucesso": True,
                "tipo": id_type,
                "valor": identifier,
                "dados": {
                    "nome": api_data.get("nome", ""),
                    "cpf": api_data.get("cpf", ""),
                    "telefone": api_data.get("telefone", ""),
                    "ordem": api_data.get("ordem", ""),
                    "status": api_data.get("status", "Em processamento"),
                    "tipo_servico": api_data.get("tipo_servico", ""),
                    "veiculo": {
                        "modelo": api_data.get("veiculo", {}).get("modelo", ""),
                        "placa": api_data.get("veiculo", {}).get("placa", ""),
                        "ano": api_data.get("veiculo", {}).get("ano", "")
                    }
                },
                "mensagem_ia": api_data.get("mensagem_ia", ""),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Erro ao formatar resposta: {str(e)}")
            return None
    
    def _is_offline(self):
        """Verifica se está offline ou sem acesso à API"""
        try:
            # Tentar ping no servidor
            base_url = self.base_urls.get(self.environment)
            requests.get(base_url, timeout=2)
            return False
        except:
            return True
    
    def _get_mock_data(self, id_type, identifier):
        """
        Retorna dados simulados para desenvolvimento e testes
        
        Args:
            id_type (str): Tipo de identificador
            identifier (str): Valor do identificador
            
        Returns:
            dict: Dados simulados
        """
        # Dados simulados para desenvolimento
        test_data = {
            "cpf": {
                "12345678900": {
                    "nome": "João da Silva",
                    "cpf": "12345678900",
                    "telefone": "11987654321",
                    "ordem": "ORD123456",
                    "status": "Em andamento",
                    "tipo_servico": "Troca de Parabrisa",
                    "veiculo": {
                        "modelo": "Honda Civic",
                        "placa": "ABC1234",
                        "ano": "2020"
                    }
                }
            },
            "telefone": {
                "11987654321": {
                    "nome": "Maria Oliveira",
                    "cpf": "98765432100",
                    "telefone": "11987654321",
                    "ordem": "ORD654321",
                    "status": "Concluído",
                    "tipo_servico": "Reparo de Vidro",
                    "veiculo": {
                        "modelo": "Toyota Corolla",
                        "placa": "DEF5678",
                        "ano": "2022"
                    }
                }
            },
            "ordem": {
                "ORD123456": {
                    "nome": "João da Silva",
                    "cpf": "12345678900",
                    "telefone": "11987654321",
                    "ordem": "ORD123456",
                    "status": "Em andamento",
                    "tipo_servico": "Troca de Parabrisa",
                    "veiculo": {
                        "modelo": "Honda Civic",
                        "placa": "ABC1234",
                        "ano": "2020"
                    }
                },
                "ORD654321": {
                    "nome": "Maria Oliveira",
                    "cpf": "98765432100",
                    "telefone": "11987654321",
                    "ordem": "ORD654321",
                    "status": "Concluído",
                    "tipo_servico": "Reparo de Vidro",
                    "veiculo": {
                        "modelo": "Toyota Corolla",
                        "placa": "DEF5678",
                        "ano": "2022"
                    }
                }
            },
            "placa": {
                "ABC1234": {
                    "nome": "João da Silva",
                    "cpf": "12345678900",
                    "telefone": "11987654321",
                    "ordem": "ORD123456",
                    "status": "Em andamento",
                    "tipo_servico": "Troca de Parabrisa",
                    "veiculo": {
                        "modelo": "Honda Civic",
                        "placa": "ABC1234",
                        "ano": "2020"
                    }
                },
                "DEF5678": {
                    "nome": "Maria Oliveira",
                    "cpf": "98765432100",
                    "telefone": "11987654321",
                    "ordem": "ORD654321",
                    "status": "Concluído",
                    "tipo_servico": "Reparo de Vidro",
                    "veiculo": {
                        "modelo": "Toyota Corolla",
                        "placa": "DEF5678",
                        "ano": "2022"
                    }
                }
            },
            "chassi": {
                "9BRBLWHEXG0123456": {
                    "nome": "Carlos Pereira",
                    "cpf": "11122233344",
                    "telefone": "21987654321",
                    "ordem": "ORD789012",
                    "status": "Agendado",
                    "tipo_servico": "Calibração ADAS",
                    "veiculo": {
                        "modelo": "Volkswagen Golf",
                        "placa": "GHI9012",
                        "ano": "2023"
                    }
                }
            }
        }
        
        # Verificar se o tipo e valor existem nos dados de teste
        if id_type in test_data and identifier in test_data[id_type]:
            # Retorna os dados simulados no formato esperado
            return {
                "sucesso": True,
                "tipo": id_type,
                "valor": identifier,
                "dados": test_data[id_type][identifier],
                "mensagem_ia": f"Olá {test_data[id_type][identifier]['nome']}! Encontrei seu atendimento para o veículo {test_data[id_type][identifier]['veiculo']['modelo']}. Seu serviço de {test_data[id_type][identifier]['tipo_servico']} está com status: {test_data[id_type][identifier]['status']}. Como posso ajudar?",
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Simula uma resposta negativa
            return {
                "sucesso": False,
                "tipo": id_type,
                "valor": identifier,
                "mensagem": "Dados não encontrados"
            }
