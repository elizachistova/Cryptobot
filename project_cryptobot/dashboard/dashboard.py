from flask import Flask, render_template, jsonify, request
from crypto_analysis import CryptoAnalyzer
import plotly
import json
import os

app = Flask(__name__, static_folder='/app/ProjetFormationData/code/dashboard/static')


DATA_DIR = '/app/ProjetFormationData/code/data/data_processed'
analyzer = CryptoAnalyzer(data_dir=DATA_DIR)

@app.route('/')
def index():
    return render_template('index.html', symbols=analyzer.available_symbols)

@app.route('/api/analysis/<symbol>')
def get_analysis(symbol):
    try:
   
        if symbol not in analyzer.available_symbols:
            return jsonify({"error": f"Symbol {symbol} not found"}), 404
            

        analysis = analyzer.analyze_symbol(symbol)
        
        if not analysis:
            return jsonify({"error": "Analysis failed"}), 400
            

        charts = {}
        for chart_name in ['price_volume_chart', 'technical_chart']:
            if chart_name in analysis:
                charts[chart_name] = json.dumps(
                    analysis[chart_name], 
                    cls=plotly.utils.PlotlyJSONEncoder
                )
        
        return jsonify(charts)
        
    except Exception as e:
        app.logger.error(f"Error analyzing {symbol}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/symbols')
def get_symbols():
    return jsonify(analyzer.available_symbols)

if __name__ == '__main__':

    if not os.path.exists(DATA_DIR):
        print(f"Warning: Data directory {DATA_DIR} does not exist!")
    app.run(host='0.0.0.0', debug=True)