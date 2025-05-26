import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox
from tkinter.ttk import Progressbar

from pdf_processor import process_pdf
from db_seletor import inicializar_bancos, get_db_path, DATABASES

from delete_subfolders import FolderCleanupApp
from config import *

from banco_de_dados import *


    # Event handlers
def load_pdf():
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            pdf_label.config(text=os.path.basename(file_path))
            global pdf_file_path
            pdf_file_path = file_path


def start_processing():
        global year, month
        try:
            year = sanitize_input(year_entry.get(), "Ano")
            month = sanitize_input(month_entry.get(), "Mês")
            output_dir = sanitize_input(folder_entry.get(), "Pasta de destino")

            validate_year_month(year, month)

            if not pdf_file_path:
                raise ValueError("Nenhum arquivo PDF foi carregado.")

            def progress_callback(current, total):
                progress["maximum"] = total
                progress["value"] = current
                root.update_idletasks()

            def cancel_callback():
                return cancel_process

            process_pdf(
                pdf_file_path, 
                output_dir, 
                year, 
                month, 
                progress_callback, 
                cancel_callback,
                #select_folder
            )

            messagebox.showinfo("Sucesso", "Processo concluído com sucesso!")

        except ValueError as e:
            logging.error(str(e))
            messagebox.showerror("Erro", str(e))


# GUI Setup
root = tk.Tk()
root.title("Processador de Contracheques")

'''initial_directory = "Documentos"'''
root.geometry("500x600")
root.configure(bg='white')



# TTK Notebook

notebook = ttk.Notebook (root)
notebook.pack(pady=10, expand=True)

frame_one = ttk.Frame(notebook, width=500, height=600)
frame_two = ttk.Frame(notebook, width=500, height=600)

app_cleanup = FolderCleanupApp(frame_two)

frame_one.pack(fill='both', expand=True)
frame_two.pack(fill='both', expand=True)

notebook.add(frame_one, text='Split PDF')
notebook.add(frame_two, text='Delete Subfolders')



# GUI Widgets

label = ttk.Label(frame_one, text="CONTRACHEQUES")
label.pack()

load_button = ttk.Button(frame_one, text="Carregar PDF", command=load_pdf)
load_button.pack(pady=10)

pdf_label = tk.Label(frame_one, text="Nenhum PDF carregado")
pdf_label.pack(pady=5)

'''///////////// banco de dados /////////////'''

inicializar_bancos()

banco_em_uso = tk.StringVar(value="Funcionários") #Default


'''//////////////////////////////////////////////'''

ttk.Label(frame_one, text="Selecionar banco de dados:").pack(pady=(10,0))
seletor_db = ttk.Combobox(frame_one, values=list(DATABASES.keys()), textvariable=banco_em_uso, state='readonly') 
seletor_db.pack(pady=5)



def usar_banco_selecionado():
    nome = banco_em_uso.get()
    caminho = get_db_path(nome)
    print(f"Banco selecionado: {nome} → {caminho}")


ttk.Button(frame_one, text="Usar banco selecionado", command=usar_banco_selecionado).pack(pady=10)

'''//////////////////////////////////////////////'''



tk.Label(frame_one, text="Pasta de destino:").pack()
folder_entry = tk.Entry(frame_one, width=50)
folder_entry.pack(pady=5)

'''load_button_folder= ttk.Button(text= "Escolher pasta de Destino", command=select_folder)
load_button_folder.pack(pady=10)'''

tk.Label(frame_one, text="Ano (yyyy):").pack()
year_entry = tk.Entry(frame_one, width=10)
year_entry.pack(pady=5)

tk.Label(frame_one, text="Mês (mm):").pack()
month_entry = tk.Entry(frame_one, width=10)
month_entry.pack(pady=5)

process_button = ttk.Button(frame_one, text="Iniciar", command=start_processing)
process_button.pack(pady=10)

cancel_button = ttk.Button(frame_one, text="Cancelar", command=cancel_processing, state=tk.DISABLED)
cancel_button.pack(pady=5)

progress = Progressbar(frame_one, orient=tk.HORIZONTAL, length=300, mode='determinate')
progress.pack(pady=10)

# Control variables
pdf_file_path = None
cancel_process = False


# Main loop
root.mainloop()