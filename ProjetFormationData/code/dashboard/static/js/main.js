// Fonction pour mettre à jour les prédictions
function updatePredictions(prediction) {
    if (prediction) {
        const currentPrice = prediction.last_price.toFixed(2);
        const predictedPrice = prediction.predicted_price.toFixed(2);
        const diff = prediction.prediction_diff;
        const diffPercentage = ((diff / prediction.last_price) * 100).toFixed(2);
        
        $('#current-price').text(`$${currentPrice}`);
        $('#predicted-price').text(`$${predictedPrice}`);
        
        const diffElement = $('#price-diff');
        diffElement.text(`${diffPercentage}%`);
        diffElement.removeClass('positive-diff negative-diff');
        diffElement.addClass(diff >= 0 ? 'positive-diff' : 'negative-diff');
    }
}

// Fonction pour gérer le chargement des graphiques
function loadCharts(symbol) {
    if (!symbol) return;

    showLoading();
    
    fetch(`/api/analysis/${symbol}`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            const priceVolumeData = JSON.parse(data.price_volume_chart);
            const technicalData = JSON.parse(data.technical_chart);

            // Ajouter la configuration responsive
            const config = {
                responsive: true,
                displayModeBar: true,
                scrollZoom: true
            };

            // Configurer les layouts pour être responsive
            const commonLayout = {
                autosize: true,
                margin: { l: 50, r: 50, t: 30, b: 30 }
            };

            // Fusionner les layouts
            priceVolumeData.layout = { ...priceVolumeData.layout, ...commonLayout };
            technicalData.layout = { ...technicalData.layout, ...commonLayout };

            Plotly.newPlot('price-volume-chart', priceVolumeData.data, priceVolumeData.layout, config);
            Plotly.newPlot('technical-chart', technicalData.data, technicalData.layout, config);

            // Mise à jour des prédictions
            if (data.prediction) {
                updatePredictions(data.prediction);
            }

            hideLoading();
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Erreur lors du chargement des données');
            hideLoading();
        });
}

// Gérer le redimensionnement de la fenêtre
window.addEventListener('resize', function() {
    Plotly.Plots.resize('price-volume-chart');
    Plotly.Plots.resize('technical-chart');
});

// Fonctions utilitaires pour gérer l'affichage
function showLoading() {
    document.querySelector('.loading').style.display = 'block';
    document.querySelector('.loading-overlay').style.display = 'block';
}

function hideLoading() {
    document.querySelector('.loading').style.display = 'none';
    document.querySelector('.loading-overlay').style.display = 'none';
}

function showError(message) {
    const errorDiv = document.querySelector('.error-message');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

// Initialisation des événements quand le DOM est chargé
document.addEventListener('DOMContentLoaded', function() {
    const symbolSelect = document.getElementById('symbol-select');
    if (symbolSelect) {
        symbolSelect.addEventListener('change', function() {
            const symbol = this.value;
            loadCharts(symbol);
        });
    }

    // Charger les données initiales si un symbole est présélectionné
    if (symbolSelect && symbolSelect.value) {
        loadCharts(symbolSelect.value);
    }
});