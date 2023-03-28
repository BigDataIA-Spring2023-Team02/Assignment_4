import os
import json
import boto3
import openai
import pandas as pd
from airflow import DAG
from pathlib import Path
from dotenv import load_dotenv
from airflow.models.param import Param
from datetime import timedelta, datetime
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 3, 22),
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

user_input = {
        "user_sleep_timer": Param(30, type='integer', minimum=10, maximum=120),
        }

dag = DAG(
    dag_id="Batch-DAG",
    default_args=default_args,
    schedule="0 5 * * *",   # https://crontab.guru/
    params=user_input,
)

# Create an AWS S3 client to store in user bucket
s3Client = boto3.client('s3',
                    region_name='us-east-1',
                    aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                    aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                    )

# Create an AWS S3 Resource to access resources available in user bucket
s3Res = boto3.resource('s3',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY'))

# Create an AWS S3 log client to store all the logs in the log folder
s3ClientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOGS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOGS_SECRET_KEY')
                        )

#load env variables
dotenv_path = Path('/.env')
load_dotenv(dotenv_path)
openai.api_key = os.environ.get('OPENAI_API_KEY')
# Defining User Bucket to store file
user_s3_bucket = os.environ.get('USER_BUCKET_NAME')
user_bucket_access = s3Res.Bucket(user_s3_bucket)
