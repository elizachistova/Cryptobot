    // Configuration du thème sombre pour Plotly
const darkThemeLayout = {
    paper_bgcolor: '#161B22',
    plot_bgcolor: '#161B22',
    font: {
        color: '#E6EDF3',
        family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif'
    },
    xaxis: {
        gridcolor: '#30363D',
        linecolor: '#30363D',
        zerolinecolor: '#30363D'
    },
    yaxis: {
        gridcolor: '#30363D',
        linecolor: '#30363D',
        zerolinecolor: '#30363D'
    },
    margin: {
        l: 40,
        r: 40,
        t: 20,
        b: 40
    }
};

// Fonction pour formater les nombres
function formatNumber(number, decimals = 2) {
    if (number === undefined || number === null) return '-';
    return Number(number).toLocaleString('en-US', {
        minimumFractionDigits: decimals,
        maximumFractionDigits: decimals
    });
}

// Fonction de gestion du redimensionnement
function handleResize() {
    const technicalChart = document.getElementById('technical-chart');
    if (technicalChart && technicalChart.data) {
        Plotly.Plots.resize(technicalChart);
    }
}

// Fonction pour forcer le redimensionnement initial
function forceChartResize() {
    setTimeout(() => {
        handleResize();
    }, 100);
}

// Configuration du MutationObserver pour surveiller les changements
function setupResizeObserver() {
    const chartContainer = document.getElementById('technical-chart');
    if (!chartContainer) return;

    const observer = new ResizeObserver(() => {
        handleResize();
    });

    observer.observe(chartContainer);
}

// Fonction de mise à jour des prédictions avec les données réelles
function updatePredictionsData(data, symbol) {
    try {
        fetch(`/api/predictions/${symbol}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                pipeline: [
                    {"$match": {"symbol": symbol}},
                    {"$unwind": "$predictions"},
                    {"$sort": {"predictions.timestamp": -1}},
                    {"$limit": 1}
                ]
            })
        })
        .then(response => response.json())
        .then(predictionData => {
            // Prix réel
            const realPrice = document.getElementById('real-price');
            const realPricePercentage = document.querySelector('#real-price + .percentage');
            
            if (realPrice && data.current_price) {
                realPrice.textContent = `$${formatNumber(data.current_price)}`;
                
                // Variation sur 24h pour le prix réel
                if (data.price_change_percentage_24h !== undefined) {
                    const changePercent = Number(data.price_change_percentage_24h);
                    realPricePercentage.textContent = `(${changePercent >= 0 ? '+' : ''}${formatNumber(changePercent)}%)`;
                    realPricePercentage.classList.remove('positive', 'negative');
                    realPricePercentage.classList.add(changePercent >= 0 ? 'positive' : 'negative');
                }
            }

            // Prix prédit
            if (predictionData && predictionData.predicted_price) {
                const latestPrediction = predictionData.predicted_price;
                const predictedPrice = document.getElementById('predicted-price');
                const predictedPricePercentage = document.querySelector('#predicted-price + .percentage');
                
                if (predictedPrice && data.current_price) {
                    predictedPrice.textContent = `$${formatNumber(latestPrediction)}`;
                    
                    // Calcul du PNL
                    const pnl = latestPrediction - data.current_price;
                    const pnlPercentage = (pnl / data.current_price) * 100;
                    
                    predictedPricePercentage.textContent = `PNL ${formatNumber(pnl)} USDT (${formatNumber(pnlPercentage)}%)`;
                    predictedPricePercentage.classList.remove('positive', 'negative');
                    predictedPricePercentage.classList.add(pnl >= 0 ? 'positive' : 'negative');
                }

                // Variation
                const priceVariation = document.getElementById('price-variation');
                const variationPercentage = document.querySelector('#price-variation + .percentage');
                
                if (priceVariation && data.current_price) {
                    const variation = Math.abs(latestPrediction - data.current_price);
                    const variationPercent = (variation / data.current_price) * 100;
                    
                    priceVariation.textContent = `$${formatNumber(variation)}`;
                    variationPercentage.textContent = `(${formatNumber(variationPercent)}%)`;
                    variationPercentage.classList.remove('positive', 'negative');
                    variationPercentage.classList.add(variationPercent >= 0 ? 'positive' : 'negative');
                }
            }
        })
        .catch(error => {
            console.error("Erreur lors du chargement des prédictions:", error);
            // En cas d'erreur, on affiche des tirets
            document.getElementById('predicted-price').textContent = '-';
            document.getElementById('price-variation').textContent = '-';
            document.querySelector('#predicted-price + .percentage').textContent = '-';
            document.querySelector('#price-variation + .percentage').textContent = '-';
        });
    } catch (error) {
        console.error("Erreur lors de la mise à jour des prédictions:", error);
    }
}

// Fonction de mise à jour du header
function updateHeaderData(data) {
    try {
        // Prix actuel et symbole
        const currentPrice = document.getElementById('current-price');
        const selectedSymbol = document.getElementById('selected-symbol');
        
        if (currentPrice && data.current_price) {
            currentPrice.textContent = `$${formatNumber(data.current_price)}`;
        }
        if (selectedSymbol && data.symbol) {
            selectedSymbol.textContent = data.symbol;
        }

        // Changement de prix sur 24h
        const priceChange = document.getElementById('price-change');
        if (priceChange && data.price_change_24h !== undefined && data.price_change_percentage_24h !== undefined) {
            const changeAmount = Number(data.price_change_24h);
            const changePercent = Number(data.price_change_percentage_24h);
            const changeText = `${changeAmount >= 0 ? '+' : ''}$${formatNumber(changeAmount)} (${formatNumber(changePercent)}%)`;
            
            priceChange.textContent = changeText;
            priceChange.classList.remove('positive', 'negative');
            priceChange.classList.add(changeAmount >= 0 ? 'positive' : 'negative');
        }

        // High/Low Price
        const priceHigh = document.getElementById('price-high');
        const priceLow = document.getElementById('price-low');
        if (priceHigh && data.high_24h) {
            priceHigh.textContent = `$${formatNumber(data.high_24h)}`;
        }
        if (priceLow && data.low_24h) {
            priceLow.textContent = `$${formatNumber(data.low_24h)}`;
        }

        // Volume
        const volume = document.getElementById('volume');
        if (volume && data.volume_24h !== undefined) {
            volume.textContent = `$${formatNumber(data.volume_24h)}`;
            if (data.volume_change_24h !== undefined) {
                volume.classList.remove('positive', 'negative');
                volume.classList.add(data.volume_change_24h >= 0 ? 'positive' : 'negative');
            }
        }
    } catch (error) {
        console.error("Erreur lors de la mise à jour des données:", error);
        showError(error.message);
    }
}

// Fonction principale de chargement des données
function loadCharts(symbol, timeframe = '1D') {
    console.log("loadCharts appelé avec le symbole:", symbol, "et timeframe:", timeframe);
    
    if (!symbol) {
        console.warn("Aucun symbole fourni à loadCharts");
        return;
    }

    showLoading();

    const technicalSelect = document.getElementById('technical-select');
    const selectedIndicators = technicalSelect.value;
    const url = `/api/analysis/${symbol}?timeframe=${timeframe}&indicators=${selectedIndicators}`;
    
    fetch(url)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }

            updateHeaderData(data);
            updatePredictionsData(data, symbol);

            if (data.technical_chart) {
                const technicalChart = JSON.parse(data.technical_chart);

                // Mise à jour de la configuration du thème sombre
                const updatedLayout = {
                    ...technicalChart.layout,
                    paper_bgcolor: '#161B22',
                    plot_bgcolor: '#161B22',
                    font: {
                        color: '#E6EDF3'
                    },
                    xaxis: {
                        ...technicalChart.layout.xaxis,
                        gridcolor: '#30363D',
                        linecolor: '#30363D'
                    },
                    yaxis: {
                        ...technicalChart.layout.yaxis,
                        gridcolor: '#30363D',
                        linecolor: '#30363D'
                    }
                };

                // Appliquer le même style à tous les axes y supplémentaires
                if (updatedLayout.yaxis2) {
                    updatedLayout.yaxis2 = {
                        ...updatedLayout.yaxis2,
                        gridcolor: '#30363D',
                        linecolor: '#30363D'
                    };
                }
                if (updatedLayout.yaxis3) {
                    updatedLayout.yaxis3 = {
                        ...updatedLayout.yaxis3,
                        gridcolor: '#30363D',
                        linecolor: '#30363D'
                    };
                }

                Plotly.newPlot('technical-chart', 
                    technicalChart.data, 
                    updatedLayout,
                    {
                        responsive: true,
                        displayModeBar: true,
                        displaylogo: false,
                        modeBarButtonsToRemove: [
                            'zoom2d',
                            'pan2d',
                            'select2d',
                            'lasso2d',
                            'autoScale2d',
                            'toggleSpikelines'
                        ]
                    }
                ).then(() => {
                    forceChartResize();
                });
            }

            hideLoading();
        })
        .catch(error => {
            console.error("Erreur lors du chargement des données:", error);
            showError(`Erreur: ${error.message}`);
            hideLoading();
        });
}

// Fonctions utilitaires
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
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    }
}

// Initialisation des événements
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM chargé, initialisation...");
    
    // Configuration de l'observateur de redimensionnement
    setupResizeObserver();
    
    // Gestionnaire de redimensionnement de fenêtre
    window.addEventListener('resize', handleResize);
    
    // Gestion des indicateurs techniques
    const technicalSelect = document.getElementById('technical-select');
    const symbolSelect = document.getElementById('symbol-select');
    
    if (technicalSelect) {
        technicalSelect.addEventListener('change', function() {
            if (symbolSelect.value) {
                const activeTimeframe = document.querySelector('.timeframe.active').textContent;
                loadCharts(symbolSelect.value, activeTimeframe);
            }
        });
    }

    // Gestion du sélecteur de symboles
    if (symbolSelect) {
        symbolSelect.addEventListener('change', function() {
            const symbol = this.value;
            const activeTimeframe = document.querySelector('.timeframe.active').textContent;
            loadCharts(symbol, activeTimeframe);
        });
    }

    // Gestion des timeframes
    const timeframeButtons = document.querySelectorAll('.timeframe');
    timeframeButtons.forEach(button => {
        button.addEventListener('click', function() {
            timeframeButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            const symbol = symbolSelect.value;
            const timeframe = this.textContent;
            
            if (symbol) {
                loadCharts(symbol, timeframe);
            }
        });
    });

    // Chargement initial
    if (symbolSelect && symbolSelect.value) {
        const initialTimeframe = document.querySelector('.timeframe.active').textContent;
        loadCharts(symbolSelect.value, initialTimeframe);
    }
});