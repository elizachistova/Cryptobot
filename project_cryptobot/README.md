# Cryptobot

/project_cryptobot
    ├── /docker/                    #Docker-related files
    │   ├── Dockerfile              
    │   ├── requirements.txt        
    │   └── docker-compose.yml   
    ├── /airflow/                   #Airflow files
    │   ├── dags/              
    │   ├── logs/        
    │   └── plugins/   
    ├── /config/                    #Config files
    │   ├── .env
    │   └── config.json 
    ├── /dashboard/                 #Dash
    │   ├── static/
    │   ├── templates/
    │   ├── __init__.py
    │   ├── app.py
    │   ├── crypto_analysis.py
    │   └── dashboard.py         
    ├── /data/                      #Data storage (exploration)
    │   ├── data_predicted/
    │   ├── data_processed/
    │   └── data_raw/
    ├── /Model/                     #ML scripts
    │   ├── predictions.py
    │   └── train_model.py
    ├── /models/                    #ML models and artifacts
    │   ├── tuning/
    │   ├── best_models/
    │   └── scalers/
    ├── /notebooks/                 #Jupyter notebooks (for exploration)
    │   └── models.ipynb
    ├── /src/                       #Application code
    │   ├── extract.py 
    │   ├── data_processor.py
    │   ├── fastapi-mongo.py
    │   ├── load.py
    │   └── models.py
    ├── /tests/                     #Unit tests/scripts
    ├── README.md                   #Project documentation
    ├── CONVENTIONS.md              #Project conventions
    └── .gitignore      