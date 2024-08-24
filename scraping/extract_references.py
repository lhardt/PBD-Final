import requests
from bs4 import BeautifulSoup
import time

def extract_references_from_url(url):
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        listings = soup.find_all('div', class_='sc-90105e55-0')

        references = []
        for listing in listings:
            if '-4' in listing.get('class', []):
                continue

            ref_div = listing.find('div', class_='ref')
            if ref_div:
                ref_text = ref_div.get_text(strip=True)
                ref_number = ref_text.replace('ref: ', '')  
                references.append(ref_number)

        return references
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return []

def scrape_all_pages(start_page, end_page, base_url, output_file):
    all_references = []

    for page in range(start_page, end_page + 1):
        url = f"{base_url}&page={page}"
        print(f"Scraping page {page}...")
        
        references = extract_references_from_url(url)
        all_references.extend(references)
        
        # Delay between requests
        time.sleep(0.5)
    
    # Save references to a file
    with open(output_file, 'w') as file:
        for ref in all_references:
            file.write(f"{ref}\n")
    
    print(f"Scraping complete. Total references saved: {len(all_references)}")

def main():
    base_url = 'https://www.auxiliadorapredial.com.br/comprar/residencial/rs+porto-alegre?order=Menor-Valor&tipoImovel=Casa,Casa-em-condom%C3%ADnio,Ch%C3%A1cara/S%C3%ADtio/Fazenda,Apartamento-garden,Apartamento,Cobertura,Kitnet/JK,Sobrado,Flat,Loft,Cobertura-horizontal'
    start_page = 1
    end_page = 1034
    output_file = 'property_references.txt'

    scrape_all_pages(start_page, end_page, base_url, output_file)

if __name__ == "__main__":
    main()