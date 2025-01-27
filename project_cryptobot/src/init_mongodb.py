import os
from pymongo import MongoClient, ASCENDING, DESCENDING
from dotenv import load_dotenv

def setup_mongodb_indexes(db):
    """Configure les index pour raw_market_data et market_data"""
    try:
        # Index pour raw_market_data
        raw_market = db.raw_market_data
        raw_market.create_index([("symbol", ASCENDING), ("openTime", DESCENDING)])
        raw_market.create_index([("openTime", ASCENDING)])
        print("Index créés pour raw_market_data")

        # Index pour market_data
        market = db.market_data
        market.create_index([("symbol", ASCENDING), ("openTime", DESCENDING)])
        market.create_index([("symbol", ASCENDING), ("last_updated", DESCENDING)])
        market.create_index([("symbol", ASCENDING), ("openTime", ASCENDING), ("close", ASCENDING)])
        # TTL index pour suppression automatique après 7 jours
        market.create_index([("openTime", ASCENDING)], expireAfterSeconds=604800)
        print("Index créés pour market_data")

    except Exception as e:
        print(f"Erreur lors de la création des index: {e}")
        raise

def create_collection_with_validation(db):
    """Crée raw_market_data avec validation de schéma"""
    try:
        if "raw_market_data" not in db.list_collection_names():
            validator = {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["symbol", "openTime", "open", "high", "low", "close", "volume"],
                    "properties": {
                        "symbol": {"bsonType": "string"},
                        "openTime": {"bsonType": "date"},
                        "open": {"bsonType": "number"},
                        "high": {"bsonType": "number"},
                        "low": {"bsonType": "number"},
                        "close": {"bsonType": "number"},
                        "volume": {"bsonType": "number"}
                    }
                }
            }
            db.create_collection("raw_market_data", validator=validator)
            print("Collection raw_market_data créée avec validation")
        else:
            print("Collection raw_market_data existe déjà")

    except Exception as e:
        print(f"Erreur lors de la création de la collection: {e}")
        raise

def main():
    # Charger les variables d'environnement
    dotenv_path = os.path.join(os.path.dirname(__file__), '../config/.env')
    load_dotenv(dotenv_path)

    # Configuration MongoDB
    host = os.getenv("HOST", "localhost").strip(",")
    port = int(os.getenv("PORT", "27017").strip(","))
    username = os.getenv("USERNAME", "").strip()
    password = os.getenv("PASSWORD", "").strip()

    try:
        # Connexion à MongoDB
        client = MongoClient(
            host=host,
            port=port,
            username=username,
            password=password
        )
        db = client.Cryptobot

        # Initialisation
        create_collection_with_validation(db)
        setup_mongodb_indexes(db)

        # Vérification des index
        print("\nIndex pour raw_market_data:")
        for index in db.raw_market_data.list_indexes():
            print(index)

        print("\nIndex pour market_data:")
        for index in db.market_data.list_indexes():
            print(index)

        client.close()
        print("\nInitialisation terminée avec succès")

    except Exception as e:
        print(f"Erreur lors de l'initialisation: {e}")

if __name__ == "__main__":
    main()