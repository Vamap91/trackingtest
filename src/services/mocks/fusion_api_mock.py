from datetime import datetime

class FusionAPIMock:
    """
    Versão mock da API Fusion para desenvolvimento.
    """
    
    def get_client_data(self, id_type, identifier):
        """
        Consulta dados do cliente (mock)
        
        Args:
            id_type (str): Tipo de identificador (cpf, telefone, placa, ordem, chassi)
            identifier (str): Valor do identificador
            
        Returns:
            dict: Dados do cliente ou None em caso de erro
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
                },
                "98765432100": {
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
                },
                "21987654321": {
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
                },
                "ORD789012": {
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
                },
                "GHI9012": {
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
