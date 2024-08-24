from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import unicodedata
import re

sys.path.append('..')
from db.connection import get_db_client

def normalize_neighborhood_name(name):
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    name = name.lower()
    name = re.sub(r"[-']", ' ', name)
    name = re.sub(r'\s+', ' ', name)
    name = name.strip()
    return name

# Conectar ao MongoDB
client = get_db_client()
if not client:
    print("Failed to connect to the database.")
    exit(1)
db = client['ImoveisDB']

# Coletar dados das coleções
property_listings = pd.DataFrame(list(db.PropertyListing.find()))

# Normalizar nomes dos bairros
property_listings['bairro'] = property_listings['Address'].apply(lambda x: normalize_neighborhood_name(x.split(',')[1].strip()))

# Filtrar bairros que são vazios ou que contêm apenas números
property_listings = property_listings[~property_listings['bairro'].str.isdigit()]
property_listings = property_listings[property_listings['bairro'].str.len() > 0]

# Remover entradas com preços nulos ou zero
property_listings = property_listings[property_listings['Property Value'] > 0]

# **Remover Outliers por Bairro**
def remove_outliers_by_neighborhood(df):
    # Calcula estatísticas por bairro
    neighborhood_stats = df.groupby('bairro')['Property Value'].agg(mean='mean', std='std').reset_index()

    # Converte o DataFrame para um dicionário
    neighborhood_stats = neighborhood_stats.set_index('bairro').to_dict(orient='index')

    def is_outlier(row, neighborhood_stats):
        bairro = row['bairro']
        if bairro in neighborhood_stats:
            stats = neighborhood_stats[bairro]
            mean = stats['mean']
            std_dev = stats['std']
            price = row['Property Value']
            return price < (mean - 3 * std_dev) or price > (mean + 3 * std_dev)
        else:
            # Caso o bairro não tenha estatísticas calculadas, considerar como não outlier
            return False

    df['is_outlier'] = df.apply(is_outlier, axis=1, neighborhood_stats=neighborhood_stats)
    return df[~df['is_outlier']]

# Remover outliers
property_listings_cleaned = remove_outliers_by_neighborhood(property_listings)

# Gráfico 1: Média de Preços das Listagens por Bairro
fig, axes = plt.subplots(1, 2, figsize=(18, 8))

avg_price_per_neighborhood = property_listings_cleaned.groupby('bairro')['Property Value'].mean().sort_values()
sns.barplot(x=avg_price_per_neighborhood.index, y=avg_price_per_neighborhood.values, ax=axes[0])
axes[0].set_title('Média de Preços das Listagens de Propriedades por Bairro (sem Outliers)')
axes[0].set_xlabel('Bairro')
axes[0].set_ylabel('Média de Preço')

for i, value in enumerate(avg_price_per_neighborhood.values):
    axes[0].text(i, value + 5000, f'{int(value):,}', ha='center', va='bottom')

axes[0].set_xticks(range(len(avg_price_per_neighborhood.index)))
axes[0].set_xticklabels(avg_price_per_neighborhood.index, rotation=45, ha='right')

# Gráfico 2: Bairros com Mais Listagens
listings_count_by_neighborhood = property_listings_cleaned['bairro'].value_counts()
sns.barplot(x=listings_count_by_neighborhood.index, y=listings_count_by_neighborhood.values, ax=axes[1])
axes[1].set_title('Bairros com Mais Listagens (sem Outliers)')
axes[1].set_xlabel('Bairro')
axes[1].set_ylabel('Número de Listagens')

for i, value in enumerate(listings_count_by_neighborhood.values):
    axes[1].text(i, value + 1, f'{value}', ha='center', va='bottom')

axes[1].set_xticks(range(len(listings_count_by_neighborhood.index)))
axes[1].set_xticklabels(listings_count_by_neighborhood.index, rotation=45, ha='right')

plt.tight_layout()
plt.show()
