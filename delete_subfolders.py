import os
import shutil
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class FolderCleanupApp:
    def __init__(self, frame):
        self.frame = frame #corrigido (estava como "self")
        
        # Lista de pastas selecionadas
        self.selected_folders = []
        self.last_directory = os.path.expanduser("~")  # Caminho inicial padrão
        self.cancel_flag = False

        self.btn_color = "#4CAF50"
        self.cancel_color = "#f44336"
    
        self.create_widgets()


    def create_widgets(self):
        
        # Botão de seleção de pastas
        self.select_button = tk.Button(self.frame, text="Selecionar Pastas", command=self.select_folders)
        self.select_button.pack(pady=10)

        # Exibição das pastas selecionadas
        self.folder_list = tk.Listbox(self.frame, width=80, height=10)
        self.folder_list.pack(pady=10)

        # Barra de progresso
        self.progress = ttk.Progressbar(self.frame, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=10)

        # Botão de Iniciar
        self.start_button = tk.Button(self.frame, text="Iniciar", command=self.start_cleanup, bg=self.btn_color, fg="white")
        self.start_button.pack(pady=10)

        # Botão de Cancelar
        self.cancel_button = tk.Button(self.frame, text="Cancelar", command=self.cancel_cleanup, bg=self.cancel_color, fg="white")
        self.cancel_button.pack(pady=10)

    def select_folders(self):
        # Permite seleção de múltiplos diretórios e lembra o último caminho selecionado
        folder = filedialog.askdirectory(mustexist=True, title="Selecione as Pastas", initialdir=self.last_directory)
        if folder:
            self.selected_folders.append(folder)
            self.folder_list.insert(tk.END, folder)
            self.last_directory = os.path.dirname(folder)  # Atualiza o último caminho selecionado

    def start_cleanup(self):
        if not self.selected_folders:
            messagebox.showwarning("Aviso", "Por favor, selecione pelo menos uma pasta.")
            return
        
        self.cancel_flag = False
        threading.Thread(target=self.cleanup_process).start()

    def cleanup_process(self):
        total_folders = len(self.selected_folders)
        self.progress["maximum"] = total_folders

        for idx, pasta_principal in enumerate(self.selected_folders):
            if self.cancel_flag:
                break

            # Percorre as subpastas de primeiro nível
            for nome_subpasta in os.listdir(pasta_principal):
                caminho_subpasta = os.path.join(pasta_principal, nome_subpasta)
                
                if os.path.isdir(caminho_subpasta):
                    # Percorre as subpastas dentro das subpastas de primeiro nível
                    for subdir in os.listdir(caminho_subpasta):
                        caminho_subdir = os.path.join(caminho_subpasta, subdir)
                        
                        if os.path.isdir(caminho_subdir):
                            try:
                                shutil.rmtree(caminho_subdir)
                            except Exception as e:
                                print(f"Erro ao deletar {caminho_subdir}: {e}")
            
            # Atualiza a barra de progresso
            self.progress["value"] = idx + 1
            self.frame.update_idletasks()

        if not self.cancel_flag:
            messagebox.showinfo("Concluído", "Processo de limpeza finalizado com sucesso.")
        else:
            messagebox.showinfo("Cancelado", "Processo de limpeza foi cancelado.")

    def cancel_cleanup(self):
        self.cancel_flag = True
