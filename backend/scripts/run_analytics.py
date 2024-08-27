import tkinter as tk
from tkinter import simpledialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import pymongo
import seaborn as sns
import unicodedata
import re
import sys

sys.path.append('..')
from db.connection import get_db_client


def normalize_neighborhood_name(name):
    name = unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    name = name.lower()
    name = re.sub(r"[-']", ' ', name)
    name = re.sub(r'\s+', ' ', name)
    name = name.strip()
    return name

def get_data():
    client = get_db_client()
    db = client['ImoveisDB']
    print("Coleções disponíveis:", db.list_collection_names())  # Verifica as coleções
    property_listings = db.PropertyListing.find()
    property_listings_list = list(property_listings)
    if not property_listings_list:
        print("A coleção PropertyListing está vazia.")
        return pd.DataFrame()
    property_listings = pd.DataFrame(property_listings_list)
    if 'Address' in property_listings.columns:
        property_listings['bairro'] = property_listings['Address'].apply(lambda x: normalize_neighborhood_name(x.split(',')[1].strip()))
    property_listings = property_listings[~property_listings['bairro'].str.isdigit()]
    property_listings = property_listings[property_listings['bairro'].str.len() > 0]
    property_listings = property_listings[property_listings['Property Value'] > 5000]
    property_listings = property_listings[property_listings['Property Value'] < 30000000]
    return property_listings

def plot_graphs():
    property_listings = get_data()
    if property_listings.empty:
        return

    # Calcula a média de preço por bairro
    avg_price_per_neighborhood = property_listings.groupby('bairro')['Property Value'].mean().sort_values()

    # Calcula a densidade de listagens por bairro
    listings_count_by_neighborhood = property_listings['bairro'].value_counts()

    # Separação dos top 10 e bottom 10 para preço médio
    top_10_avg_price = avg_price_per_neighborhood.tail(10)
    bottom_10_avg_price = avg_price_per_neighborhood.head(10)

    # Top 10 para densidade de listagens
    top_10_listings_count = listings_count_by_neighborhood.head(10)

    fig, axes = plt.subplots(1, 3, figsize=(18, 8))

    # Gráfico Top 10 bairros por preço médio
    sns.barplot(x=top_10_avg_price.index, y=top_10_avg_price.values, ax=axes[0])
    axes[0].set_title('Top 10 Bairros por Preço Médio')
    axes[0].set_xlabel('Bairro')
    axes[0].set_ylabel('Média de Preço')

    for i, value in enumerate(top_10_avg_price.values):
        axes[0].text(i, value + 5000, f'{int(value):,}', ha='center', va='bottom')

    axes[0].set_xticks(range(len(top_10_avg_price.index)))
    axes[0].set_xticklabels(top_10_avg_price.index, rotation=45, ha='right')

    # Gráfico Bottom 10 bairros por preço médio
    sns.barplot(x=bottom_10_avg_price.index, y=bottom_10_avg_price.values, ax=axes[1])
    axes[1].set_title('Bottom 10 Bairros por Preço Médio')
    axes[1].set_xlabel('Bairro')
    axes[1].set_ylabel('Média de Preço')

    for i, value in enumerate(bottom_10_avg_price.values):
        axes[1].text(i, value + 5000, f'{int(value):,}', ha='center', va='bottom')

    axes[1].set_xticks(range(len(bottom_10_avg_price.index)))
    axes[1].set_xticklabels(bottom_10_avg_price.index, rotation=45, ha='right')

    # Gráfico Top 10 bairros por densidade de listagens
    sns.barplot(x=top_10_listings_count.index, y=top_10_listings_count.values, ax=axes[2])
    axes[2].set_title('Top 10 Bairros por Densidade de Listagens')
    axes[2].set_xlabel('Bairro')
    axes[2].set_ylabel('Número de Listagens')

    for i, value in enumerate(top_10_listings_count.values):
        axes[2].text(i, value + 1, f'{value}', ha='center', va='bottom')

    axes[2].set_xticks(range(len(top_10_listings_count.index)))
    axes[2].set_xticklabels(top_10_listings_count.index, rotation=45, ha='right')

    plt.tight_layout()
    plt.show()


def get_avg_price_by_neighborhood():
    property_listings = get_data()
    if property_listings.empty:
        return
    neighborhood = simpledialog.askstring("Input", "Digite o nome do bairro:")
    if neighborhood:
        normalized_neighborhood = normalize_neighborhood_name(neighborhood)
        neighborhood_data = property_listings[property_listings['bairro'] == normalized_neighborhood]
        if not neighborhood_data.empty:
            avg_price = neighborhood_data['Property Value'].mean()
            messagebox.showinfo("Resultado", f"A média de preço para o bairro '{neighborhood}' é: R$ {avg_price:,.2f}")
        else:
            messagebox.showwarning("Aviso", "Nenhum dado encontrado para o bairro fornecido.")
    else:
        messagebox.showwarning("Aviso", "Nenhum bairro foi fornecido.")


def get_highest_value():
    client = get_db_client()
    db = client['ImoveisDB']
    collection = db['PropertyListing']
    top_properties = collection.find().sort("Property Value", -1).limit(10)
    for property in top_properties:
        print(property)
        print("\n")

def main():
    root = tk.Tk()
    root.title("Análise de Imóveis")

    tk.Button(root, text="Visualizar Gráficos", command=plot_graphs).pack(pady=10)
    tk.Button(root, text="Consultar Preço Médio por Bairro", command=get_avg_price_by_neighborhood).pack(pady=10)
    tk.Button(root, text="10 Propriedades mais caras", command=get_highest_value).pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    main()
