import os
import io
import json
import boto3
import openai
import requests
import pandas as pd
from airflow import DAG
from pathlib import Path
from botocore import UNSIGNED
from botocore.config import Config
from dotenv import load_dotenv
from airflow.models.param import Param
from datetime import timedelta, datetime
from airflow.utils.dates import days_ago
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator

# Set parameters for user input
user_input = {
        "user_sleep_timer": Param(30, type='integer', minimum=10, maximum=120),
        }

# Create DAG with the given parameters
dag = DAG(
    dag_id="Adhoc-DAG",
    start_date=days_ago(0),
    catchup=False,
    dagrun_timeout=timedelta(minutes=60),
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
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
                        )

# Create an AWS S3 log client to store all the logs in the log folder
s3ClientLogs = boto3.client('logs',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_LOGS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_LOGS_SECRET_KEY')
                        )

#load env variables
dotenv_path = Path('./dags/.env')
load_dotenv(dotenv_path)
openai.api_key = os.environ.get('OPENAI_API_KEY')
whisper_api_key = os.environ.get('WHISPER_API_KEY')

# Defining User Bucket to store file
user_s3_bucket = "damg-7245-audio-transcripts"

def read_audio_file_from_s3():
    """
    Read the audio files from AWS S3 bucket and return the list of file names
    """
    s3_folder_name = "Adhoc-Folder/"
    s3_files = s3Client.list_objects(Bucket = user_s3_bucket, Prefix = s3_folder_name).get('Contents')
    file_list = []
    for s3_file in s3_files:
        file_path = s3_file['Key']
        file_path = file_path.split('/')
        file_list.append(file_path[-1])
    
    return file_list

# Define a function to transcribe a media file using the Whispr API.
def transcribe_media_file(s3_object_key):
    response = s3Client.get_object(Bucket=os.environ.get('USER_BUCKET_NAME'), Key=s3_object_key)
    audio_file = io.BytesIO(response['Body'].read())
    audio_file.name = s3_object_key

    # Transcribe the audio file using the OpenAI API
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    text = transcript["text"]
    return text

def transcript_file_s3(s3_object_key, transcript):
    filename = s3_object_key.split('/')[1].replace('.mp3','.txt')
    s3Client.put_object(Bucket = os.environ.get('USER_BUCKET_NAME'), Key = 'Processed-Text-Folder/'+filename, Body = transcript)
    return 'Processed-Text-Folder/'+filename

def gpt_default_questions(selected_file):
    prompt = f'Context: {selected_file}'+ '\n' + 'Given the transcript, Generate 3-4 default questionnaire on the selected transcript and generate answers for the same:'
    response = openai.Completion.create(
        engine='text-davinci-002',
        prompt=prompt,
        temperature=0.5,
        max_tokens=1024,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    answer = response.choices[0].text.strip()
    return answer

with dag:
    # Creating PythonOperator to read audio file from user s3 bucket
    read_audio_files = PythonOperator(   
    task_id='read_audio_files_s3',
    python_callable = read_audio_file_from_s3,
    provide_context=True,
    dag=dag,
    )

    # Creating PythonOperator to transcribe audio file from user s3 bucket
    transcribe_audio_file = PythonOperator(   
    task_id='transcribe_audio_file_s3',
    python_callable = transcribe_media_file,
    provide_context=True,
    dag=dag,
    )

    read_audio_files >> transcribe_audio_file
