import tkinter as tk
from tkinter import simpledialog, messagebox, ttk
import pandas as pd
import matplotlib.pyplot as plt
import pymongo
import seaborn as sns
import unicodedata
import re
import sys
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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
    property_listings = property_listings[property_listings['areaPrivativa'] > 0]
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

def insert_estate():
    root = tk.Toplevel()
    root.title("Inserir Novo Imóvel")
    root.geometry("1200x800")
    root.configure(bg='#f0f0f0')

    # Load Roboto font
    font_title = ('Roboto', 24, 'bold')
    font_label = ('Roboto', 14)
    font_entry = ('Roboto', 14)

    # Configure styles
    style = ttk.Style()
    style.configure('TFrame', background='#f0f0f0')
    style.configure('TLabel', font=font_label, background='#f0f0f0')
    style.configure('TEntry', font=font_entry)
    style.configure('TButton', font=font_label, padding=15, background='#4CAF50', foreground='white')
    style.map('TButton', background=[('active', '#45a049')])

    # Main frame
    main_frame = ttk.Frame(root, padding="30 30 30 30")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Title
    title_label = ttk.Label(main_frame, text="Inserir Novo Imóvel", font=font_title, background='#f0f0f0')
    title_label.pack(pady=(0, 30))

    # Create a canvas with a scrollbar
    canvas = tk.Canvas(main_frame, bg='#f0f0f0')
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    property_details = {}
    
    fields = [
        ('Title', str),
        ('Address', str),
        ('Property Value', float),
        ('ID-source', str),
        ('areaPrivativa', float),
        ('dormitorios', int),
        ('banheiros', int),
        ('vagas', int),
        ('caracteristicas-condominio', dict)
    ]
    
    entries = {}
    
    for field, field_type in fields:
        frame = ttk.Frame(scrollable_frame)
        frame.pack(fill='x', padx=10, pady=10)
        
        label = ttk.Label(frame, text=f"{field}:", width=25)
        label.pack(side=tk.LEFT, padx=(0, 10))
        
        if field == 'caracteristicas-condominio':
            entry = ttk.Button(frame, text="Adicionar características", command=lambda: add_characteristics(property_details))
        else:
            entry = ttk.Entry(frame, font=font_entry)
        entry.pack(side=tk.LEFT, expand=True, fill='x')
        
        entries[field] = entry

    def submit():
        for field, field_type in fields:
            if field == 'caracteristicas-condominio':
                continue
            value = entries[field].get()
            if field_type in [int, float]:
                try:
                    value = field_type(value)
                except ValueError:
                    messagebox.showerror("Erro", f"Valor inválido para {field}. Por favor, insira um número.")
                    return
            property_details[field] = value
        
        client = get_db_client()
        db = client['ImoveisDB']
        
        try:
            db.PropertyListing.insert_one(property_details)
            messagebox.showinfo("Sucesso", "Imóvel inserido com sucesso no banco de dados.")
            root.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao inserir imóvel: {str(e)}")
        finally:
            client.close()

    submit_button = ttk.Button(main_frame, text="Inserir Imóvel", command=submit)
    submit_button.pack(pady=30)

def add_characteristics(property_details):
    characteristics = {}
    while True:
        dialog = tk.Toplevel()
        dialog.title("Adicionar Característica")
        dialog.geometry("600x250")
        dialog.configure(bg='#f0f0f0')

        frame = ttk.Frame(dialog, padding="20 20 20 20")
        frame.pack(fill=tk.BOTH, expand=True)

        label = ttk.Label(frame, text="Digite uma característica do condomínio:", font=('Roboto', 12))
        label.pack(pady=(0, 10))

        entry = ttk.Entry(frame, font=('Roboto', 12), width=40)
        entry.pack(pady=(0, 20))

        added = False
        def add_characteristic():
            key = entry.get().strip()
            if key:
                characteristics[key] = True
                entry.delete(0, tk.END)
                added = True
            else:
                dialog.destroy()

        add_button = ttk.Button(frame, text="Adicionar", command=add_characteristic)
        add_button.pack(side=tk.LEFT, padx=(0, 10))

        finish_button = ttk.Button(frame, text="Finalizar", command=dialog.destroy)
        finish_button.pack(side=tk.RIGHT)

        dialog.wait_window()
        if not added:
            break
    if characteristics:
        property_details['caracteristicas-condominio'] = characteristics

def avg_price_per_square_meter_by_neighborhood():
    # Get the data as a pandas DataFrame
    df = get_data()
    
    if df.empty:
        return []

    # Calculate price per square meter
    df['price_per_sqm'] = df['Property Value'] / df['areaPrivativa']

    # Group by neighborhood and calculate average price per square meter
    result = df.groupby('bairro').agg({
        'price_per_sqm': 'mean',
        'Property Value': 'count'
    }).reset_index()

    # Sort by average price per square meter in descending order
    result = result.sort_values('price_per_sqm', ascending=False)

    # Format the results
    formatted_results = []
    for _, row in result.iterrows():
        formatted_results.append({
            "Bairro": row['bairro'],
            "Preço Médio por m²": f"R$ {row['price_per_sqm']:,.2f}",
            "Número de Imóveis": row['Property Value']
        })

    return formatted_results

# The show_avg_price_per_sqm function remains the same
def show_avg_price_per_sqm():
    results = avg_price_per_square_meter_by_neighborhood()
    
    if not results:
        messagebox.showinfo("Informação", "Não há dados disponíveis para exibir.")
        return

    # Create a new window to display results
    result_window = tk.Toplevel()
    result_window.title("Preço Médio por m² por Bairro")
    result_window.geometry("1200x800")
    result_window.configure(bg='#f0f0f0')

    # Main frame
    main_frame = ttk.Frame(result_window, padding="20 20 20 20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Title
    title_label = ttk.Label(main_frame, text="Preço Médio por m² por Bairro", 
                            font=('Roboto', 24, 'bold'), background='#f0f0f0')
    title_label.pack(pady=(0, 20))

    # Create a treeview to display the results in a table format
    style = ttk.Style()
    style.configure("Treeview", font=('Roboto', 16), rowheight=30)
    style.configure("Treeview.Heading", font=('Roboto', 18, 'bold'))

    tree = ttk.Treeview(main_frame, columns=("Bairro", "Preço Médio por m²", "Número de Imóveis"), show="headings")
    tree.heading("Bairro", text="Bairro")
    tree.heading("Preço Médio por m²", text="Preço Médio por m²")
    tree.heading("Número de Imóveis", text="Número de Imóveis")

    tree.column("Bairro", width=300)
    tree.column("Preço Médio por m²", width=300)
    tree.column("Número de Imóveis", width=300)
    
    for result in results:
        tree.insert("", "end", values=(result["Bairro"], result["Preço Médio por m²"], result["Número de Imóveis"]))
    
    tree.pack(expand=True, fill="both", padx=20, pady=20)

    # Scrollbar
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side="right", fill="y")
    tree.configure(yscrollcommand=scrollbar.set)

    # Footer
    footer_label = ttk.Label(main_frame, text="@ Melnickstão", 
                             font=('Roboto', 10), background='#f0f0f0')
    footer_label.pack(side=tk.BOTTOM, pady=(20, 0))

def get_avg_price_by_neighborhood():
    property_listings = get_data()
    if property_listings.empty:
        messagebox.showinfo("Informação", "Não há dados disponíveis para exibir.")
        return

    # Create a new window to display results
    result_window = tk.Toplevel()
    result_window.title("Preço Médio por Bairro")
    result_window.geometry("800x400")
    result_window.configure(bg='#f0f0f0')

    # Main frame
    main_frame = ttk.Frame(result_window, padding="20 20 20 20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Title
    title_label = ttk.Label(main_frame, text="Preço Médio por Bairro", 
                            font=('Roboto', 24, 'bold'), background='#f0f0f0')
    title_label.pack(pady=(0, 20))

    # Input frame
    input_frame = ttk.Frame(main_frame)
    input_frame.pack(pady=20)

    input_label = ttk.Label(input_frame, text="Digite o nome do bairro:", 
                            font=('Roboto', 14))
    input_label.pack(side=tk.LEFT, padx=(0, 10))

    input_entry = ttk.Entry(input_frame, font=('Roboto', 14), width=30)
    input_entry.pack(side=tk.LEFT)

    # Result frame
    result_frame = ttk.Frame(main_frame)
    result_frame.pack(pady=20, expand=True, fill=tk.BOTH)

    result_label = ttk.Label(result_frame, text="", 
                             font=('Roboto', 18), background='#f0f0f0')
    result_label.pack(expand=True)

    def search():
        neighborhood = input_entry.get().strip()
        if neighborhood:
            normalized_neighborhood = normalize_neighborhood_name(neighborhood)
            neighborhood_data = property_listings[property_listings['bairro'] == normalized_neighborhood]
            if not neighborhood_data.empty:
                avg_price = neighborhood_data['Property Value'].mean()
                result_label.config(text=f"A média de preço para o bairro '{neighborhood}' é:\nR$ {avg_price:,.2f}")
            else:
                result_label.config(text="Nenhum dado encontrado para o bairro fornecido.")
        else:
            result_label.config(text="Por favor, digite o nome de um bairro.")

    # Search button
    search_button = ttk.Button(main_frame, text="Buscar", command=search, width=20)
    search_button.pack(pady=20)

    # Footer
    footer_label = ttk.Label(main_frame, text="@ Melnickstão", 
                             font=('Roboto', 10), background='#f0f0f0')
    footer_label.pack(side=tk.BOTTOM, pady=(20, 0))

    result_window.mainloop()

def create_gui():
    root = tk.Tk()
    root.title("Análise de Imóveis")
    root.geometry("1200x800")
    root.configure(bg='#f0f0f0')

    # Load Roboto font
    font_title = ('Roboto', 30, 'bold')
    font_button = ('Roboto', 20)
    font_label = ('Roboto', 18)

    # Configure styles
    style = ttk.Style()
    style.theme_use('clam')
    
    style.configure('TFrame', background='#f0f0f0')
    style.configure('TButton', font=font_button, padding=30, background='#4CAF50', foreground='white')
    style.map('TButton', background=[('active', '#45a049')])
    style.configure('TLabel', font=font_label, background='#f0f0f0')

    # Main frame
    main_frame = ttk.Frame(root, padding="20 20 20 20")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Title
    title_label = ttk.Label(main_frame, text="Sistema de Análise de Imóveis", 
                            font=font_title, background='#f0f0f0')
    title_label.pack(pady=(0, 20))

    # Button frame
    button_frame = ttk.Frame(main_frame)
    button_frame.pack(pady=20)

    # Buttons
    buttons = [
        ("Mostrar Gráficos", plot_graphs),
        ("Inserir Novo Imóvel", insert_estate),
        ("Preço Médio por m² por Bairro", show_avg_price_per_sqm),
        ("Preço Médio por Bairro", get_avg_price_by_neighborhood)
    ]

    for text, command in buttons:
        btn = ttk.Button(button_frame, text=text, command=command, width=40)
        btn.pack(pady=10)

    # Chart frame
    global chart_frame
    chart_frame = ttk.Frame(main_frame)
    chart_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    # Footer
    footer_label = ttk.Label(main_frame, text="@ Melnickstão", 
                             font=font_label, background='#f0f0f0')
    footer_label.pack(side=tk.BOTTOM, pady=(20, 0))

    root.mainloop()

def main():
    create_gui()

if __name__ == "__main__":
    main()
