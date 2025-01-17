from flask import Flask, render_template, jsonify, request, send_from_directory
import plotly
import json
from datetime import datetime
from crypto_analysis import CryptoAnalyzer
import logging
import os

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
MONGODB_URI = "mongodb://CryptoBot:bot123@mongodb:27017/Cryptobot?authSource=admin"


# Définition du chemin vers les données de prédiction
DATA_PREDICTED_DIR = os.path.join(os.path.dirname(__file__), '../data/data_predicted')

# Initialisation de l'analyseur
analyzer = CryptoAnalyzer(mongodb_uri=MONGODB_URI)

@app.route('/')
def index():
    """Route principale"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return render_template('index.html', 
                             symbols=analyzer.available_symbols,
                             current_time=current_time)
    except Exception as e:
        logger.error(f"Erreur dans index: {str(e)}")
        return str(e), 500

@app.route('/api/analysis/<symbol>')
def get_analysis(symbol):
    """Route d'analyse avec gestion des timeframes"""
    try:
        timeframe = request.args.get('timeframe', '1D')
        indicators = request.args.getlist('indicators')
        
        if isinstance(indicators, str):
            indicators = [indicators]
        
        logger.info(f"Analyse demandée: {symbol}, timeframe: {timeframe}, indicateurs: {indicators}")
        
        results = analyzer.analyze_symbol(symbol, timeframe, indicators)
        
        if not results:
            logger.error(f"Aucune donnée trouvée pour {symbol}")
            return jsonify({"error": "No data available"}), 400
        
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Erreur dans get_analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/data/data_predicted/<filename>')
def get_prediction_data(filename):
    """Route pour servir les fichiers de prédiction"""
    try:
        logger.info(f"Demande de fichier de prédiction: {filename}")
        logger.info(f"Chemin recherché: {os.path.join(DATA_PREDICTED_DIR, filename)}")
        
        # Vérifier que le fichier existe
        if not os.path.exists(os.path.join(DATA_PREDICTED_DIR, filename)):
            logger.error(f"Fichier de prédiction non trouvé: {filename}")
            return jsonify({"error": "Prediction file not found"}), 404
            
        return send_from_directory(DATA_PREDICTED_DIR, filename)
    except Exception as e:
        logger.error(f"Erreur lors de l'accès au fichier de prédiction {filename}: {str(e)}")
        return jsonify({"error": str(e)}), 500

def setup_folders():
    """Vérifie et crée les dossiers nécessaires au démarrage"""
    try:
        logger.info(f"Vérification du dossier des prédictions: {DATA_PREDICTED_DIR}")
        if not os.path.exists(DATA_PREDICTED_DIR):
            os.makedirs(DATA_PREDICTED_DIR, exist_ok=True)
            logger.warning(f"Création du dossier des prédictions: {DATA_PREDICTED_DIR}")
        
        # Liste les fichiers existants
        prediction_files = os.listdir(DATA_PREDICTED_DIR)
        logger.info(f"Fichiers de prédiction disponibles: {prediction_files}")
    except Exception as e:
        logger.error(f"Erreur lors de la configuration des dossiers: {str(e)}")

# Appeler la fonction directement au démarrage
setup_folders()

@app.before_request
def check_folders():
    """Vérifie les dossiers avant chaque requête"""
    if not os.path.exists(DATA_PREDICTED_DIR):
        setup_folders()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)