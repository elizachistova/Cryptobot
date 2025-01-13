db=connect("mongodb://CryptoBot:bot123@localhost/Cryptobot");

db.market_data.insertMany([
    {
        symbol: 'BTCUSDT',
        last_updated: ISODate('2025-01-13T01:25:00.000Z'),
        rows: 16201,
        openTime: ISODate('2025-01-06T20:00:00.000Z'),
        open: 101817.22,
        high: 102329.98,
        low: 101600.05,
        close: 102235.6,
        volume: 3269.77,
        trend: 1,
        volume_price_ratio: 0.032,
        indicator: {
          BB_MA: 96224.74,
          BB_UPPER: 102709.9,
          BB_LOWER: 89739.58,
          RSI: 86.43,
          DOJI: 0,
          HAMMER: 0,
          SHOOTING_STAR: 0
        }
      },
      {
        symbol: 'BTCUSDT',
        last_updated: ISODate('2025-01-13T01:25:00.000Z'),
        rows: 16201,
        openTime: ISODate('2025-01-06T16:00:00.000Z'),
        open: 102147.95,
        high: 102480,
        low: 101250,
        close: 101817.22,
        volume: 5128.13,
        trend: -1,
        volume_price_ratio: 0.0504,
        indicator: {
          BB_MA: 96652.93,
          BB_UPPER: 103444.52,
          BB_LOWER: 89861.34,
          RSI: 82.5,
          DOJI: 0,
          HAMMER: 0,
          SHOOTING_STAR: 0
        }
      },
      {
        symbol: 'ETHUSDT',
        last_updated: ISODate('2025-01-13T01:25:01.000Z'),
        rows: 16201,
        openTime: ISODate('2025-01-07T00:00:00.000Z'),
        open: 3687.44,
        high: 3700.86,
        low: 3663,
        close: 3682.25,
        volume: 27692.08,
        trend: -1,
        volume_price_ratio: 7.5204,
        indicator: {
          BB_MA: 3375.62,
          BB_UPPER: 3660.18,
          BB_LOWER: 3091.06,
          RSI: 88.13,
          DOJI: 0,
          HAMMER: 0,
          SHOOTING_STAR: 0
        }
      },
      {
        symbol: 'ETHUSDT',
        last_updated: ISODate('2025-01-13T01:25:01.000Z'),
        rows: 16201,
        openTime: ISODate('2025-01-06T20:00:00.000Z'),
        open: 3687.44,
        high: 3703.38,
        low: 3666.37,
        close: 3687.45,
        volume: 29594.63,
        trend: 1,
        volume_price_ratio: 8.0258,
        indicator: {
          BB_MA: 3395.7,
          BB_UPPER: 3708.36,
          BB_LOWER: 3083.04,
          RSI: 90.53,
          DOJI: 1,
          HAMMER: 0,
          SHOOTING_STAR: 0
        }
      },
      {
        symbol: 'ETHUSDT',
        last_updated: ISODate('2025-01-13T01:25:01.000Z'),
        rows: 16201,
        openTime: ISODate('2025-01-06T16:00:00.000Z'),
        open: 3714.45,
        high: 3744.83,
        low: 3655.55,
        close: 3687.44,
        volume: 72164.67,
        trend: -1,
        volume_price_ratio: 19.5704,
        indicator: {
          BB_MA: 3418.36,
          BB_UPPER: 3749.51,
          BB_LOWER: 3087.21,
          RSI: 89.77,
          DOJI: 0,
          HAMMER: 0,
          SHOOTING_STAR: 0
        }
      },
      {
        symbol: 'BNBUSDT',
        last_updated: ISODate('2025-01-13T01:24:59.000Z'),
        rows: 15716,
        openTime: ISODate('2025-01-07T00:00:00.000Z'),
        open: 729.42,
        high: 731.6,
        low: 725.18,
        close: 728.92,
        volume: 43601.51,
        trend: -1,
        volume_price_ratio: 59.8166,
        indicator: {
          BB_MA: 699.47,
          BB_UPPER: 727.5,
          BB_LOWER: 671.44,
          RSI: 70.98,
          DOJI: 1,
          HAMMER: 0,
          SHOOTING_STAR: 0
        }
      },
      {
        symbol: 'BNBUSDT',
        last_updated: ISODate('2025-01-13T01:24:59.000Z'),
        rows: 15716,
        openTime: ISODate('2025-01-06T20:00:00.000Z'),
        open: 732.3,
        high: 745.29,
        low: 728.5,
        close: 729.42,
        volume: 96960.3,
        trend: -1,
        volume_price_ratio: 132.9279,
        indicator: {
          BB_MA: 701.52,
          BB_UPPER: 733.41,
          BB_LOWER: 669.63,
          RSI: 82.33,
          DOJI: 0,
          HAMMER: 0,
          SHOOTING_STAR: 1
        }
      },
      {
        symbol: 'BNBUSDT',
        last_updated: ISODate('2025-01-13T01:24:59.000Z'),
        rows: 15716,
        openTime: ISODate('2025-01-06T16:00:00.000Z'),
        open: 725.76,
        high: 735.65,
        low: 721.95,
        close: 732.3,
        volume: 77453.01,
        trend: 1,
        volume_price_ratio: 105.7668,
        indicator: {
          BB_MA: 703.67,
          BB_UPPER: 737.18,
          BB_LOWER: 670.16,
          RSI: 81.45,
          DOJI: 0,
          HAMMER: 0,
          SHOOTING_STAR: 0
        }
      },
      {
        symbol: 'AVAXUSDT',
        last_updated: ISODate('2025-01-13T01:25:00.000Z'),
        rows: 9425,
        openTime: ISODate('2025-01-06T20:00:00.000Z'),
        open: 44.31,
        high: 44.44,
        low: 43.71,
        close: 44.05,
        volume: 284580.46,
        trend: -1,
        volume_price_ratio: 6460.3964,
        indicator: {
          BB_MA: 39.09,
          BB_UPPER: 44.68,
          BB_LOWER: 33.5,
          RSI: 96.86,
          DOJI: 0,
          HAMMER: 0,
          SHOOTING_STAR: 0
        }
      },
      {
        symbol: 'AVAXUSDT',
        last_updated: ISODate('2025-01-13T01:25:00.000Z'),
        rows: 9425,
        openTime: ISODate('2025-01-06T16:00:00.000Z'),
        open: 44.75,
        high: 45.05,
        low: 43.63,
        close: 44.32,
        volume: 433380.95,
        trend: -1,
        volume_price_ratio: 9778.451,
        indicator: {
          BB_MA: 39.47,
          BB_UPPER: 45.4,
          BB_LOWER: 33.54,
          RSI: 96.65,
          DOJI: 0,
          HAMMER: 0,
          SHOOTING_STAR: 0
        }
      },
      {
        symbol: 'XRPUSDT',
        last_updated: ISODate('2025-01-13T01:24:57.000Z'),
        rows: 14131,
        openTime: ISODate('2025-01-06T16:00:00.000Z'),
        open: 2.44,
        high: 2.46,
        low: 2.4,
        close: 2.42,
        volume: 41007513,
        trend: -1,
        volume_price_ratio: 16945253.3058,
        indicator: {
          BB_MA: 2.34,
          BB_UPPER: 2.45,
          BB_LOWER: 2.23,
          RSI: 58.14,
          DOJI: 0,
          HAMMER: 0,
          SHOOTING_STAR: 0
        }
      },
      {
        symbol: 'ADAUSDT',
        last_updated: ISODate('2025-01-13T01:24:58.000Z'),
        rows: 12066,
        openTime: ISODate('2025-01-06T20:00:00.000Z'),
        open: 1.11,
        high: 1.11,
        low: 1.09,
        close: 1.09,
        volume: 15643397.7,
        trend: -1,
        volume_price_ratio: 14351741.0092,
        indicator: {
          BB_MA: 0.99,
          BB_UPPER: 1.14,
          BB_LOWER: 0.84,
          RSI: 75,
          DOJI: 0,
          HAMMER: 0,
          SHOOTING_STAR: 0
        }
      },
      {
        symbol: 'ADAUSDT',
        last_updated: ISODate('2025-01-13T01:24:58.000Z'),
        rows: 12066,
        openTime: ISODate('2025-01-06T16:00:00.000Z'),
        open: 1.1,
        high: 1.12,
        low: 1.09,
        close: 1.11,
        volume: 40411345.4,
        trend: 1,
        volume_price_ratio: 36406617.4775,
        indicator: {
          BB_MA: 1,
          BB_UPPER: 1.15,
          BB_LOWER: 0.85,
          RSI: 74.29,
          DOJI: 0,
          HAMMER: 0,
          SHOOTING_STAR: 0
        }
      },
      {
        symbol: 'TRXUSDT',
        last_updated: ISODate('2025-01-13T01:24:57.000Z'),
        rows: 5330,
        openTime: ISODate('2025-01-06T08:00:00.000Z'),
        open: 0.26,
        high: 0.26,
        low: 0.26,
        close: 0.26,
        volume: 62700204.4,
        trend: -1,
        volume_price_ratio: 241154632.3077,
        indicator: {
          BB_MA: 0.26,
          BB_UPPER: 0.28,
          BB_LOWER: 0.24,
          RSI: 66.67,
          DOJI: 1,
          HAMMER: 0,
          SHOOTING_STAR: 0
        }
      }
        

]);    