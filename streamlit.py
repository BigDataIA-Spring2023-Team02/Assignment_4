import os
import time
import boto3
from PIL import Image
import streamlit as st
from dotenv import load_dotenv
from main_functions import list_files_in_folder, upload_file_s3_bucket, transcribe_media_file, generate_answer, transcript_file_s3, gpt_default_answers, write_logs

load_dotenv()

# Create an AWS S3 Resource to access resources available in user bucket
s3Res = boto3.resource('s3',
                        region_name='us-east-1',
                        aws_access_key_id = os.environ.get('AWS_ACCESS_KEY'),
                        aws_secret_access_key = os.environ.get('AWS_SECRET_KEY'))

# Defining User Bucket to store file
user_s3_bucket = os.environ.get('USER_BUCKET_NAME')
user_bucket_access = s3Res.Bucket(user_s3_bucket)

def uploading_file():
    # Add a file uploader to the app
    file = st.file_uploader('Please attach an audio file')
    
    if file is not None:
        # Display some information about the file
        write_logs(f"{file.name} File attached to upload in user s3 bucket.")
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
                    write_logs(f"File already available in the user bucket folder.")
                    st.warning('File is already available in the folder !!!')
                    st.warning('Please upload different file !!!')
                
                else:
                    with st.spinner('Uploading...'):
                        try:
                            upload_file_s3_bucket(file, 'Adhoc-Folder')
                            st.success('File uploaded successfully !!!')
                            st.success(f"Successfully uploaded {file.name} to {user_s3_bucket}")
                            write_logs(f"Successfully uploaded {file.name} to Adhoc-Folder.")

                        except Exception as e:
                            st.error('Error uploading file: ' + str(e))
                            write_logs(f"Error uploading file: {str(e)}")
                            st.write('Please try again later !!!')

def transcribe_file():
    selected_file = st.selectbox('Please Select the media file to transcribe:', [" "] + list_files_in_folder('Adhoc-Folder'))
    transcribe_file = st.button('Transcribe the file')
    if transcribe_file:
        if selected_file != " ":
            with st.spinner('Transcribing...'):
                try:
                    s3_object_key = f'Adhoc-Folder/{selected_file}'
                    transcript = transcribe_media_file(s3_object_key)
                    st.write(transcript)
                    st.success('File transcribed successfully !!!')
                    write_logs(f"File transcribed successfully {transcript}")
                    st.write('')
                    
                    key = transcript_file_s3(s3_object_key, transcript)
                    st.success(f"Successfully uploaded transcript to {key}")
                    write_logs(f"Successfully uploaded transcript to {key}")

                except Exception as  e:
                    st.error('Error transcribing the file: ' + str(e))
                    write_logs(f"Error transcribing file: {str(e)}")
                    st.write('Please try again later !!!')
        else:
            st.warning('Please select the file first !!!')
    else:
        st.write('Please upload the file first !!!')

def get_text_analysis():
    selected_file = st.selectbox('Please Select the transcript file from the processed list:', [" "] + list_files_in_folder('Processed-Text-Folder'))
    default_button = st.button('Generate Deafult Question:')
    question_input = st.text_input("Please Enter Your Questions:")
    ask_button = st.button('Ask Question:')
    
    if selected_file != " ":
        if default_button:
            st.write('')
            write_logs(f"Generating Default Questions:")
            st.write('Default Questions:')
            st.write('Q1: What is the summary of this transcript?')
            write_logs("Q1: What is the summary of this transcript?")
            st.write('Q2: How many speakers are present?')
            write_logs("Q2: How many speakers are present?")
            st.write('Q3: Give the highlights in 3 short points.')
            write_logs("Q3: Give the highlights in 3 short points.")
            st.write('')
            st.write('Answer:')
            default_answer = gpt_default_answers(selected_file)
            write_logs(f"Answers: {default_answer}")
            st.write(default_answer)
        else:
            st.warning('Please Generate Default Questions')
        
        if ask_button:
            write_logs(f"Asking Question: {question_input}")
            answer = generate_answer(question_input, selected_file)
            write_logs(f"Answers: {answer}")
            st.write(answer)
        else:
            st.warning("Please ask the question")
    else:
        st.warning("Please select the file first !!!")

# Create the Streamlit app
def app():
    st.title('Meeting Intelligence Application')
    page = st.sidebar.selectbox("Choose a page", ["--Select Page--", "Upload File", "Transcribe File", "Get Text Analysis"])
    
    if page == "--Select Page--":
        st.write('')
        st.image(Image.open('meeting-intelligence-application.jpeg'))
        st.subheader("Please select a page from the list given on the sidebar")
    
    elif page == "Upload File":
        st.write('')
        st.header('Upload Media File')
        st.write('')
        uploading_file()
    
    elif page == "Transcribe File":
        st.write('')
        st.header('Trasncribe Media File')
        st.write('')
        transcribe_file()
    
    elif page == "Get Text Analysis":
        st.write('')
        st.header('Ask Questions on Transcript Files')
        st.write('')
        get_text_analysis()

# Run the app
if __name__ == '__main__':
    app()
