from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

#Defining the DAG
with DAG(
    'cryptobot_workflow',
    default_args={
        'owner': 'airflow',
    },
    description='A workflow for cryptobot',
    # Every 4 hours
    schedule_interval='*/4 * * * *',
    start_date=datetime(2025, 1, 1),
    catchup=False
) as dag:

    # Task 1: Data Collection
    fetch_data = BashOperator(
        task_id='fetch_data',
        bash_command='',
    )

    # Task 2: Preprocess Data
    preprocess_data = BashOperator(
        task_id='preprocess_data',
        bash_command='',
    )

    # Task 3: Model Prediction
    model_prediction = BashOperator(
        task_id='model_prediction',
        bash_command='',
    )

    # Task 4: Database Update
    db_update = BashOperator(
        task_id='db_update',
        bash_command='',
    )

    # Task 5: Dashboard Update
    dashboard_update = BashOperator(
        task_id='dashboard_update',
        bash_command='',
    )

    # Define task dependencies
    fetch_data >> preprocess_data >> model_prediction >> db_update >> dashboard_update
