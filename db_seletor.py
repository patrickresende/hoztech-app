import sqlite3
import os


DATABASES = {
    "Funcionários":"plan.db",
    "Livros":"livros.db"


}

def inicializar_bancos():
    for nome, arquivo in DATABASES.items():
        if not os.path.exists(arquivo):
            try:
                conn = sqlite3.connect(arquivo)
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS controle (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        info TEXT
            );
            """)
                conn.commit()
                print(f"[INFO] Banco '{nome}' criado em '{arquivo}'.")
            except sqlite3.Error as e:
        
                print(f"[ERRO] Falha ao criar o banco '{nome}': {e}")
            finally:
                conn.close()
        else:
            print(f"[INFO] Banco '{nome}' já existe em '{arquivo}'.")


def get_db_path(nome_db):
    caminho = DATABASES.get(nome_db)
    if caminho:
        return caminho
    
    else:
        print(f"[ERRO] Banco '{nome_db}' não está registrado.")
        return None


def listar_bancos_disponíveis():
    return list(DATABASES.keys())


#print("[DEBUG] Funções disponíveis:", dir())