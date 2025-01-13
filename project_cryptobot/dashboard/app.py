# app.py
from flask import Flask, render_template, jsonify, request
from crypto_analysis import CryptoAnalyzer
import plotly
import json
import os

app = Flask(__name__)
analyzer = CryptoAnalyzer()

@app.route('/')
def index():
    return render_template('index.html', symbols=analyzer.available_symbols)

@app.route('/api/analysis/<symbol>')
def get_analysis(symbol):
    try:
        analysis = analyzer.analyze_symbol(symbol)
        if not analysis:
            return jsonify({"error": "Analysis failed"}), 400
            
        # Convertir les graphiques Plotly en JSON
        price_volume_json = json.dumps(analysis['price_volume_chart'], cls=plotly.utils.PlotlyJSONEncoder)
        technical_json = json.dumps(analysis['technical_chart'], cls=plotly.utils.PlotlyJSONEncoder)
        
        return jsonify({
            "price_volume_chart": price_volume_json,
            "technical_chart": technical_json
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/symbols')
def get_symbols():
    return jsonify(analyzer.available_symbols)

if __name__ == '__main__':
    app.run(debug=True, port=5000)