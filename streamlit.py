import os
import boto3
import openai
from PIL import Image
import streamlit as st
from dotenv import load_dotenv
from main_functions import list_files_in_folder, upload_file_s3_bucket, transcribe_media_file, generate_answer

load_dotenv()
openai.api_key = os.environ.get('OPENAI_API_KEY')

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

def uploading_file():
    # Add a file uploader to the app
    file = st.file_uploader('Please attach an audio file')
    
    if file is not None:
        # Display some information about the file
        st.write('Filename:', file.name)
        st.write('File size:', file.size, 'bytes')
        st.write('File type:', file.type)
        types_file = ["audio/mpeg", "audio/x-mpeg", "audio/mpeg3", "audio/x-mpeg-3", "audio/wav", "audio/x-wav", "application/octet-stream"]
        
        if file.type not in types_file:
            st.error('Only MP3 audio formats are supported. Please try to upload a different file !!!')

        else:
            st.success(file.name + ' Selected')
            transfer_file = st.button('Upload file on S3 Bucket !!!')
            
            if transfer_file:
                file_folder = 'Adhoc-Folder/'
                file_key = file_folder + file.name
                s3_files_keys = []
                for s3_files_list in user_bucket_access.objects.all():
                    s3_files_keys.append(s3_files_list.key)
                
                if file_key in s3_files_keys:
                    st.warning('File is already available in the folder !!!')
                    st.warning('Please upload different file !!!')
                
                else:
                    with st.spinner('Uploading...'):
                        try:
                            upload_file_s3_bucket(file, 'Adhoc-Folder')
                            st.success('File uploaded successfully !!!')
                            st.success(f"Successfully uploaded {file.name} to {user_s3_bucket}")

                        except Exception as e:
                            st.error('Error uploading file: ' + str(e))
                            st.write('Please try again later !!!')
            
            transcribe_file = st.button('Transcribe the file')
            
            if transcribe_file:
                if file is not None:
                    with st.spinner('Transcribing...'):
                        try:
                            s3_object_key = f'Adhoc-Folder/{file.name}'
                            transcript = transcribe_media_file(s3_object_key)
                            st.write(transcript)
                            
                            file_upload_name = (file.name)[:-4] + ".txt"
                            with open(file_upload_name, 'w') as f:
                                f.write(transcript)
                            
                            # Upload text data to S3 bucket
                            s3Client.put_object(Body = transcript, Bucket = user_s3_bucket, Key = f"Processed-Text-Folder/{file_upload_name}")
                            st.success('File transcribed successfully !!!')

                        except Exception as  e:
                            st.error('Error transcribing the file: ' + str(e))
                            st.write('Please try again later !!!')
                else:
                    st.warning('Please select the file first !!!')
            else:
                st.write('Please upload the file first !!!')

def get_text_analysis():
    selected_file = st.selectbox('Please Select the transcript file from the processed list:', list_files_in_folder('Processed-Text-Folder'))
    
    if selected_file is not None:
        question_input = st.text_input("Please Enter Your Questions:")
        ask_button = st.button('Ask Question:')
        
        if ask_button:
            answer = generate_answer(question_input, selected_file)
            st.write(answer)
        else:
            st.warning("Please ask the question")

    else:
        st.warning("Please select the file first !!!")

# Create the Streamlit app
def app():
    st.title('Meeting Intelligence Application')
    page = st.sidebar.selectbox("Choose a page", ["--Select Page--", "Upload File", "Get Text Analysis"])
    
    if page == "--Select Page--":
        st.write('')
        st.image(Image.open('meeting-intelligence-application.jpeg'))
        st.subheader("Please select a page from the list given on the sidebar")
    
    elif page == "Upload File":
        st.write('')
        st.header('Upload Media File')
        st.write('')
        uploading_file()
    
    elif page == "Get Text Analysis":
        st.write('')
        st.header('Transcribe Audio File')
        st.write('')
        get_text_analysis()

# Run the app
if __name__ == '__main__':
    app()
