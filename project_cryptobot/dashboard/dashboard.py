from flask import Flask, render_template, jsonify, request, send_from_directory
import plotly
import json
from datetime import datetime
from crypto_analysis import CryptoAnalyzer
import logging
import os
from dotenv import load_dotenv

# Configuration du logging
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '../config/.env')
load_dotenv(dotenv_path)

# Configuration MongoDB avec gestion d'erreur
try:
    MONGODB_URI = (
        f"mongodb://CryptoBot:bot123@mongodb:27017/Cryptobot?authSource=admin"
    )

    # Initialisation de l'analyseur
    analyzer = CryptoAnalyzer(mongodb_uri=MONGODB_URI)
    logger.info("Connexion MongoDB établie avec succès")
    
except Exception as e:
    logger.error(f"Erreur de configuration MongoDB: {e}")
    analyzer = None

app = Flask(__name__)
DATA_PREDICTED_DIR = os.path.join(os.path.dirname(__file__), '../data/data_predicted')

@app.route('/')
def index():
    """Route principale"""
    try:
        if not analyzer:
            raise Exception("Analyseur non initialisé - Problème de connexion MongoDB")
            
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
        if not analyzer:
            raise Exception("Analyseur non initialisé - Problème de connexion MongoDB")
            
        timeframe = request.args.get('timeframe', '1D')
        indicators = request.args.getlist('indicators')
        
        if isinstance(indicators, str):
            indicators = [indicators]
        
        logger.info(f"Analyse demandée: {symbol}, timeframe: {timeframe}, indicateurs: {indicators}")
        
        results = analyzer.analyze_symbol(symbol, timeframe, indicators)
        
        if not results:
            logger.error(f"Aucune donnée trouvée pour {symbol}")
            return jsonify({"error": "No data available"}), 404
            
        if 'technical_chart' not in results:
            logger.error(f"Données techniques manquantes pour {symbol}")
            return jsonify({"error": "Technical data not available"}), 500
            
        return jsonify(results)
    
    except Exception as e:
        logger.error(f"Erreur dans get_analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/predictions/<symbol>', methods=['GET', 'POST'])
def get_predictions(symbol):
    """Route pour obtenir les prédictions depuis MongoDB avec pipeline personnalisée"""
    try:
        if not analyzer:
            raise Exception("Analyseur non initialisé")

        pipeline = [
            {"$match": {"symbol": symbol}}, 
            {"$unwind": "$predictions"},
            {"$sort": {"predictions.timestamp": -1}},
            {"$limit": 1}
        ]
            
        result = list(analyzer.db.prediction_ml.aggregate(pipeline))
        
        if not result:
            return jsonify({"error": "No prediction available"}), 404

        latest_prediction = result[0]["predictions"]
        return jsonify({
            "predicted_price": latest_prediction["prediction"],
            "timestamp": latest_prediction["timestamp"]
        })

    except Exception as e:
        logger.error(f"Erreur dans get_predictions: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)