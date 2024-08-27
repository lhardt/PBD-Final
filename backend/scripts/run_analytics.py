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
    property_listings = property_listings[property_listings['Property Value'] > 0]
    return property_listings

def plot_graphs():
    property_listings = get_data()
    if property_listings.empty:
        return

    fig, axes = plt.subplots(1, 2, figsize=(18, 8))

    avg_price_per_neighborhood = property_listings.groupby('bairro')['Property Value'].mean().sort_values()
    sns.barplot(x=avg_price_per_neighborhood.index, y=avg_price_per_neighborhood.values, ax=axes[0])
    axes[0].set_title('Média de Preços das Listagens de Propriedades por Bairro (sem Outliers)')
    axes[0].set_xlabel('Bairro')
    axes[0].set_ylabel('Média de Preço')

    for i, value in enumerate(avg_price_per_neighborhood.values):
        axes[0].text(i, value + 5000, f'{int(value):,}', ha='center', va='bottom')

    axes[0].set_xticks(range(len(avg_price_per_neighborhood.index)))
    axes[0].set_xticklabels(avg_price_per_neighborhood.index, rotation=45, ha='right')

    listings_count_by_neighborhood = property_listings['bairro'].value_counts()
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
    property_listings = get_data()
    top_properties = property_listings.sort_values("Property Value", -1).limit(10)
    for prop in top_properties:
        print(prop)
def main():
    root = tk.Tk()
    root.title("Análise de Imóveis")

    tk.Button(root, text="Visualizar Gráficos", command=plot_graphs).pack(pady=10)
    tk.Button(root, text="Consultar Preço Médio por Bairro", command=get_avg_price_by_neighborhood).pack(pady=10)
    tk.Button(root, text="10 Propriedades mais caras", command=get_highest_value).pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    main()
