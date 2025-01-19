// Sélectionner la base de données Cryptobot
db = db.getSiblingDB('Cryptobot');

// Créer un utilisateur avec des droits spécifiques
db.createUser({
  user: 'CryptoBot',
  pwd: 'bot123',
  roles: [
    { role: 'readWrite', db: 'Cryptobot' }
  ]
});

// Créer les collections nécessaires si elles n'existent pas
if (!db.raw_market_data.exists()) {
    db.createCollection('raw_market_data');
}

if (!db.market_data.exists()) {
    db.createCollection('market_data');
}

// Créer des indexes pour améliorer les performances et éviter les duplications
db.market_data.createIndex(
  { symbol: 1, openTime: 1 }, 
  { unique: true }
);

db.raw_market_data.createIndex(
  { symbol: 1, openTime: 1 }, 
  { unique: true }
);

// Indexes supplémentaires pour des requêtes fréquentes
db.market_data.createIndex({ symbol: 1 });
db.market_data.createIndex({ openTime: -1 });
db.raw_market_data.createIndex({ symbol: 1 });
db.raw_market_data.createIndex({ openTime: -1 });