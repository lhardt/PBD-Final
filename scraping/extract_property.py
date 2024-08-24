import aiohttp
from bs4 import BeautifulSoup

async def extract_property_details(session, url):
    async with session.get(url) as response:
        if response.status == 200:
            soup = BeautifulSoup(await response.text(), 'html.parser')

            property_details = {}
            caracteristicas_condominio = {}

            # Extract Title of the Property from <h2> with class "titulo-imovel-detalhe"
            title_h2 = soup.find('h2', class_='titulo-imovel-detalhe')
            title = title_h2.get_text(strip=True) if title_h2 else "N/A"
            property_details['Title'] = title

            # Extract Address from <p> with class "text title medium endereco-caracteristicas"
            address_p = soup.find('p', class_='text title medium endereco-caracteristicas')
            address = address_p.get_text(strip=True) if address_p else "N/A"
            property_details['Address'] = address

            # Extract Property Value and ID-source from "valores-imovel-caracteristicas"
            valor_div = soup.find('div', class_='valores-imovel-caracteristicas')
            if valor_div:
                valor_span = valor_div.find('span')
                if valor_span:
                    property_value_text = valor_span.get_text(strip=True).replace("R$", "").strip()
                    property_value = ''.join(char for char in property_value_text if char in ['0','1','2','3','4','5','6','7','8','9'])
                    property_details['Property Value'] = int(property_value) if property_value.isdigit() else "N/A"

                id_source_p = valor_div.find('p')
                if id_source_p:
                    id_source_text = id_source_p.get_text(strip=True).replace("ref: ", "").strip()
                    property_details['ID-source'] = id_source_text

            # Process each relevant div for additional features (text title medium caracteristica-imovel)
            divs = soup.find_all('div', class_='text title medium caracteristica-imovel')
            for div in divs:
                img = div.find('img')
                if img and 'alt' in img.attrs:
                    alt_text = img['alt']
                    if "Ícone de " in alt_text:
                        feature_title = alt_text.split("Ícone de ")[-1].strip()
                        span = div.find('span')
                        if span:
                            span_text = span.get_text(strip=True)
                            cleaned_value = ''.join(char for char in span_text if char in ['0','1','2','3','4','5','6','7','8','9'])
                            value = int(cleaned_value) if cleaned_value.isdigit() else True
                            property_details[feature_title] = value

            # Process each relevant div for "caracteristica-imovel-sobre"
            sobre_divs = soup.find_all('div', class_='caracteristica-imovel-sobre')
            for div in sobre_divs:
                img = div.find('img')
                if img and 'alt' in img.attrs:
                    alt_text = img['alt']
                    if "Ícone de " in alt_text:
                        sobre_title = alt_text.split("Ícone de ")[-1].strip()
                        span = div.find('span')
                        if span:
                            span_text = span.get_text(strip=True)
                            cleaned_value = ''.join(char for char in span_text if char in ['0','1','2','3','4','5','6','7','8','9'])
                            value = int(cleaned_value) if cleaned_value.isdigit() else True
                            caracteristicas_condominio[sobre_title] = value

            property_details['caracteristicas-condominio'] = caracteristicas_condominio

            return property_details

        else:
            print(f"Failed to retrieve the page. Status code: {response.status}")
            return None
