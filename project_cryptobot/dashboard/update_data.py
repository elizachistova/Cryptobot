import subprocess
import sys
import os
import logging
from datetime import datetime

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='update_data.log'
)

def run_command(command):
    try:
        logging.info(f"Exécution de la commande : {command}")
        result = subprocess.run(
            command, 
            shell=True, 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        logging.info(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        logging.error(f"Erreur lors de l'exécution de {command}")
        logging.error(e.stderr)
        raise

def update_data():
    base_dir = "/app/dashboard"
    scripts = [
        os.path.join(base_dir, "..", "extract.py"),
        os.path.join(base_dir, "..", "Data_processor.py"),
        os.path.join(base_dir, "..", "load.py")
    ]

    start_time = datetime.now()
    logging.info("Début de la mise à jour des données")

    for script in scripts:
        try:
            logging.info(f"Exécution de {script}")
            run_command(f"python {script}")
        except Exception as e:
            logging.error(f"Échec de l'exécution de {script}: {e}")
            # Continuer malgré l'erreur d'un script

    end_time = datetime.now()
    duration = end_time - start_time
    logging.info(f"Mise à jour terminée. Durée totale : {duration}")

def main():
    try:
        update_data()
    except Exception as e:
        logging.error(f"Erreur fatale lors de la mise à jour : {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()