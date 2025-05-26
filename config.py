import logging
import os



#Setup logger

def setup_logger():
        logging.basicConfig(
            level=logging.INFO, 
            format="%(asctime)s - %(message)s", 
            datefmt="%d-%m-Y %H:%M:%S"
        )

    # Utility functions
def sanitize_input(value, field_name):
        """Validates and sanitizes input."""
        if not value.strip():
            raise ValueError(f"{field_name} não pode estar vazio.")
        return value.strip()

'''def select_folder():
        select_directory = filedialog.askdirectory(initialdir=initial_directory)
        print("Select Directory:", select_directory)'''


def validate_year_month(year, month):
        """Validates the year and month inputs."""
        if not (year.isdigit() and len(year) == 4):
            raise ValueError("Ano inválido! Insira no formato yyyy.")
        if not (month.isdigit() and 1 <= int(month) <= 12):
            raise ValueError("Mês inválido! Insira no formato mm.")
        return year, month.zfill(2)  # Add leading zero to month if missing


'''//////////////////////////////////////////////////////'''



def cancel_processing():
        global cancel_process
        cancel_process = True




loglevel = 'DEBUG'
numeric_level = getattr(logging, loglevel.upper(), None)
if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: (loglevel)')

logging.basicConfig(
        filename='D:/RH/Desktop/holerites v.1.1/example.log',
        filemode='a',
        level=numeric_level
    )

print(f"Diretório atual: {os.getcwd()}")

logging.info("Mensagem Teste - Criando arquivo de log")

print ("Verifique o arquivo no diretório")

    # Logger
setup_logger()