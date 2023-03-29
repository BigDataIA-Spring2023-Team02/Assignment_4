import io
import os
import json
import time
import boto3
import openai
import requests
from dotenv import load_dotenv

load_dotenv()

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

# Defining User Bucket to store file
user_s3_bucket = os.environ.get('USER_BUCKET_NAME')
user_bucket_access = s3Res.Bucket(user_s3_bucket)
openai.api_key = os.environ.get('OPENAI_API_KEY')

# Define a function to write logs to AWS CloudWatch
def write_logs(message: str):
    s3ClientLogs.put_log_events(
        logGroupName = "Assignment-04",
        logStreamName = "UI-Logs",
        logEvents = [
            {
                'timestamp' : int(time.time() * 1e3),
                'message' : message
            }
        ]
    )

def list_files_in_folder(folder_name: str):
    file_list = []
    user_s3_bucket_files = s3Client.list_objects(Bucket = user_s3_bucket, Prefix = f"{folder_name}/").get('Contents')
    
    for objects in user_s3_bucket_files:
        file_path = objects['Key']
        file_path = file_path.split('/')
        if file_path[-1] != '':
            file_list.append(file_path[-1])
    
    if (len(file_list)!=0):
        return file_list

# Define a function to upload a file to S3.
def upload_file_s3_bucket(file: str, folder_name: str):
    file_name = file.name
    s3_object_key = f'{folder_name}/{file_name}'
    s3Res.Bucket(user_s3_bucket).put_object(Key=s3_object_key, Body=file.read())

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

def generate_answer(question_input, selected_file):
    prompt = f'Question: {question_input}\nContext: {selected_file}\nAnswer:'
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