# create_db.py

from pymongo import MongoClient
from . import config


def initialize_db():
    """
    Inicializa o banco de dados MongoDB e insere uma oferta imobiliária de exemplo.
    """
    # Conectar ao MongoDB usando a URI definida em config.py
    client = MongoClient(config.MONGO_URI)

    # Selecionar o banco de dados
    db = client[config.DATABASE_NAME]

    # Selecionar a coleção (collection)
    collection = db['ofertas_imobiliarias']

    # Exemplo de oferta a ser inserida
    oferta = {
        "localizacao": {
            "endereco": "Rua Exemplo, 123",
            "bairro": "Centro",
            "cidade": "Porto Alegre",
            "estado": "RS",
            "cep": "90000-000"
        },
        "tipo_oferta": "Venda",
        "tipo_imovel": "Apartamento",
        "valor": 350000,
        "tamanho": 80,
        "vaga_garagem": True
    }

    # Inserir o documento na coleção
    result = collection.insert_one(oferta)
    print(f"Oferta inserida com o ID: {result.inserted_id}")
