# db/create_db.py

def create_imoveisdb_collections(client):
    # Select or create the ImoveisDB database
    db = client['ImoveisDB']

    # Create the PropertyListing Collection
    property_listing = db['PropertyListing']
    
    # Define an example document structure for the PropertyListing Collection
    property_listing_structure = {
        "localização": {
            "endereço": "str",
            "bairro": "str",
            "cidade": "str",
            "estado": "str",
            "CEP": "str"
        },
        "tipo_oferta": "str",
        "tipo_imovel": "str",
        "valor_de_venda": 0.0,
        "valor_de_aluguel": 0.0,
        "tamanho": 0.0,
        "vaga_garagem": 0,
        "detalhes": "str",
        "data_coleta": "date",
        "fonte": "str"
    }
    
    # Insert a sample document to create the collection with the desired structure
    property_listing.insert_one(property_listing_structure)
    
    # Create the CrawlerLog Collection
    crawler_log = db['CrawlerLog']
    
    # Define an example document structure for the CrawlerLog Collection
    crawler_log_structure = {
        "timestamp": "date",
        "url_fonte": "str",
        "status_coleta": "str",
        "dados_coletados": [],
        "mensagem_erro": "str"
    }
    
    # Insert a sample document to create the collection with the desired structure
    crawler_log.insert_one(crawler_log_structure)
    
    print("Database and collections created successfully!")
