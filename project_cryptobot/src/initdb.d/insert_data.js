print("Début de l'initialisation MongoDB");

db = db.getSiblingDB("Cryptobot");

if (!db.getUser("CryptoBot")) {
    db.createUser({
        user: "CryptoBot",
        pwd: "bot123", 
        roles: [{ role: "readWrite", db: "Cryptobot" }]
    });
    print("Utilisateur 'CryptoBot' créé avec succès.");
} else {
    print("L'utilisateur 'CryptoBot' existe déjà.");
}

db.market_data.insertMany([
    {
        symbol: 'BTCUSDT',
        last_updated: ISODate('2025-01-20T15:49:31.375Z'),
        rows: 16246,
        openTime: ISODate('2025-01-17T08:00:00.000Z'),
        open: 101440.51,
        high: 102581.45,
        low: 101439.77,
        close: 102237.6,
        volume: 5380.48,
        trend: 1,
        volume_price_ratio: 0.0526,
        indicator: {
          BB_MA: 104412.67,
          BB_UPPER: 107717.46,
          BB_LOWER: 101107.88,
          RSI: 33.45,
          DOJI: 0,
          HAMMER: 0,
          SHOOTING_STAR: 0
        }
      },
      {
        symbol: 'ETHUSDT',
        last_updated: ISODate('2025-01-20T15:50:07.168Z'),
        rows: 16246,
        openTime: ISODate('2025-01-17T08:00:00.000Z'),
        open: 3373.14,
        high: 3439,
        low: 3372.52,
        close: 3423.24,
        volume: 70486.33,
        trend: 1,
        volume_price_ratio: 20.5905,
        indicator: {
          BB_MA: 3338.26,
          BB_UPPER: 3486.04,
          BB_LOWER: 3190.48,
          RSI: 50.28,
          DOJI: 0,
          HAMMER: 0,
          SHOOTING_STAR: 0
        }
      },
      {
        symbol: 'SOLUSDT',
        last_updated: ISODate('2025-01-20T15:50:30.718Z'),
        rows: 9722,
        openTime: ISODate('2025-01-17T08:00:00.000Z'),
        open: 213.27,
        high: 219.7,
        low: 213.22,
        close: 218.77,
        volume: 841428.75,
        trend: 1,
        volume_price_ratio: 3846.1798,
        indicator: {
          BB_MA: 247.73,
          BB_UPPER: 289,
          BB_LOWER: 206.46,
          RSI: 25.84,
          DOJI: 0,
          HAMMER: 0,
          SHOOTING_STAR: 0
        }
      }
      
]);

db.prediction_ml.insertMany([
    {
        symbol: 'BTCUSDT',
        predictions: [
          {
            timestamp: ISODate('2025-01-17T12:00:00.000Z'),
            prediction: 91697.31
          },
          {
            timestamp: ISODate('2025-01-17T16:00:00.000Z'),
            prediction: 91542.41
          },
          {
            timestamp: ISODate('2025-01-17T20:00:00.000Z'),
            prediction: 91395.25
          },
          {
            timestamp: ISODate('2025-01-18T00:00:00.000Z'),
            prediction: 91040.82
          },
          {
            timestamp: ISODate('2025-01-18T04:00:00.000Z'),
            prediction: 91095.34
          },
          {
            timestamp: ISODate('2025-01-18T08:00:00.000Z'),
            prediction: 91420.84
          },
          {
            timestamp: ISODate('2025-01-18T12:00:00.000Z'),
            prediction: 91479.09
          },
          {
            timestamp: ISODate('2025-01-18T16:00:00.000Z'),
            prediction: 92055.69
          },
          {
            timestamp: ISODate('2025-01-18T20:00:00.000Z'),
            prediction: 92467.45
          },
          {
            timestamp: ISODate('2025-01-19T00:00:00.000Z'),
            prediction: 92779.18
          }
        ],
        metadata: { created_at: ISODate('2025-01-23T13:57:32.828Z') }
      },
      {
        symbol: 'ETHUSDT',
        predictions: [
          {
            timestamp: ISODate('2025-01-17T12:00:00.000Z'),
            prediction: 3512.46
          },
          {
            timestamp: ISODate('2025-01-17T16:00:00.000Z'),
            prediction: 3472.26
          },
          {
            timestamp: ISODate('2025-01-17T20:00:00.000Z'),
            prediction: 3435.84
          },
          {
            timestamp: ISODate('2025-01-18T00:00:00.000Z'),
            prediction: 3405.73
          },
          {
            timestamp: ISODate('2025-01-18T04:00:00.000Z'),
            prediction: 3380.4
          },
          {
            timestamp: ISODate('2025-01-18T08:00:00.000Z'),
            prediction: 3407.27
          },
          {
            timestamp: ISODate('2025-01-18T12:00:00.000Z'),
            prediction: 3368.02
          },
          {
            timestamp: ISODate('2025-01-18T16:00:00.000Z'),
            prediction: 3399.42
          },
          {
            timestamp: ISODate('2025-01-18T20:00:00.000Z'),
            prediction: 3433.77
          },
          {
            timestamp: ISODate('2025-01-19T00:00:00.000Z'),
            prediction: 3457.11
          }
        ],
        metadata: { created_at: ISODate('2025-01-23T13:59:18.801Z') }
      },
      {
        symbol: 'SOLUSDT',
        predictions: [
          {
            timestamp: ISODate('2025-01-17T12:00:00.000Z'),
            prediction: 206.38
          },
          {
            timestamp: ISODate('2025-01-17T16:00:00.000Z'),
            prediction: 202.07
          },
          {
            timestamp: ISODate('2025-01-17T20:00:00.000Z'),
            prediction: 204.88
          },
          {
            timestamp: ISODate('2025-01-18T00:00:00.000Z'),
            prediction: 209.08
          },
          {
            timestamp: ISODate('2025-01-18T04:00:00.000Z'),
            prediction: 211.94
          },
          {
            timestamp: ISODate('2025-01-18T08:00:00.000Z'),
            prediction: 214.53
          },
          {
            timestamp: ISODate('2025-01-18T12:00:00.000Z'),
            prediction: 209.81
          },
          {
            timestamp: ISODate('2025-01-18T16:00:00.000Z'),
            prediction: 208.87
          },
          {
            timestamp: ISODate('2025-01-18T20:00:00.000Z'),
            prediction: 214.35
          },
          {
            timestamp: ISODate('2025-01-19T00:00:00.000Z'),
            prediction: 218.11
          }
        ],
        metadata: { created_at: ISODate('2025-01-23T14:01:55.506Z') }
      }
      
      
]);
console.log("Data inserted successfully for prediction_ml");
db.prediction_ml.find().pretty();

console.log("Data inserted successfully for market_data and prediction_ml");
db.market_data.find().pretty();
print("Fin de l'initialisation MongoDB");
