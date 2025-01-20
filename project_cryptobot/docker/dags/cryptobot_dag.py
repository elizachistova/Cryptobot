from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime
import subprocess

def installs():
    subprocess.run(["pip", "install", "pymongo"])
    subprocess.run(["pip", "install", "joblib"])
    subprocess.run(["pip", "install", "scikit-learn"])

with DAG(
    'cryptobot_workflow',
    default_args={
        'owner': 'airflow',
    },
    description='A workflow for cryptobot',
    # Every 4 hours
    schedule_interval='0 */4 * * *',
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=['cryptobot'],
) as dag:
    
    #install_task = PythonOperator(
    #    task_id="installs",
    #    python_callable=installs,
    #)

    # Task 1: Data Collection
    fetch_data = BashOperator(
        task_id='fetch_data',
        bash_command="python /opt/airflow/src/extract.py",
    )

    # Task 2: Preprocess Data
    preprocess_data = BashOperator(
        task_id='preprocess_data',
        bash_command='python /opt/airflow/src/Data_processor.py',
    )

     # Task 3: Load Data
    load_data = BashOperator(
        task_id='load_data',
        bash_command='python /opt/airflow/src/load.py',
    )

    # Task 4: Model Prediction
    model_prediction = BashOperator(
        task_id='model_prediction',
        bash_command='python /opt/airflow/src/predictions.py',
    )

    # Task 5: Database Update
    fastapi = BashOperator(
        task_id='fastapi',
        bash_command='python /opt/airflow/src/fastapi-mongo.py',
    )

    # Task 6: Dashboard Update
    #dashboard_update = BashOperator(
     #   task_id='dashboard_update',
      #  bash_command='',
    #)

    # Define task dependencies
    fetch_data >> preprocess_data >> load_data >> model_prediction >> fastapi 