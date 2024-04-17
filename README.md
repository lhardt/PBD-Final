# Home Pricing Monitor

This project is intended to scrap, store, and display interactively data about home prices in the region of Greater Porto Alegre. Each of these responsibilities will be executed by a different module.

---

### 1. Scrapper 



**Possible Sites to Monitor:**

- [AuxiliadoraPredial](https://www.auxiliadorapredial.com.br/comprar/residencial/rs+porto-alegre)
- [Leindecker](https://www.leindecker.com.br/busca/locacao/cidade/Porto;Alegre/categoria/08;20;09;11;10;13;21;16;12;19/0/) - Filtrar Categorias
- [Benin](https://www.benin.com.br/pesquisa#tipo_negociacao=-2&cidade=Porto+Alegre&estado=RS&ordem=8&) - Note the direct `List.aspx` API calls
- [Crédito Real](https://www.creditoreal.com.br/vendas?tipoImovel=Flat/Loft/Studio/JK,Apartamento,Apartamento%20Garden,Cobertura,Casa,Casa%20em%20Condom%C3%ADnio,Geminado,Terreno,Duplex)
- [Bridge Imóveis](https://www.bridgeimoveis.com.br/busca/comprar)

**Relevant links:** 

- [BeautifulSoup](https://beautiful-soup-4.readthedocs.io/en/latest/), Python web scraping
- [Selenium](https://www.selenium.dev/pt-br/documentation/) - Python/Java/* WebDriver.

---

### 2. Database

We plan to host a Docker image of a database such as **MongoDB** (Document-oriented database) on an **AWS** cluster.

**Possible Fields:**

- Value (R$)
- Offer type (1 month rent or sale)
- 

**Relevant links:** 

- .

---

### 3. Visualizer

We can either **(1)** host a custom web app to query data from the DB (such as Jupyter Notebooks?), or **(2)** have an offline script to build a ready-made visualization. 

**Relevant links:** 

- Python [Folium](https://python-visualization.github.io/folium/latest/): a data visualization library that compiles into HTML