from diagrams import Cluster, Edge, Diagram
from diagrams.onprem.client import User
from diagrams.onprem.container import Docker
from diagrams.onprem.workflow import Airflow
from diagrams.aws.storage import SimpleStorageServiceS3 as S3
from diagrams.custom import Custom

# Define nodes
with Diagram("Meeting Intelligence Application Architecture Diagram", show=False):
    ingress = User("User")
    with Cluster("Streamlit"):
        streamlit = Custom("Streamlit", "./streamlit.png")     
    with Cluster("Docker Compose"): 
        docker = Docker("Docker")          
        with Cluster("Airflow"): 
          Batch_Dag = Airflow("Batch_Dag")
          Adhoc_Dag = Airflow("Adhoc_Dag")
          Adhoc_Dag << Edge(label="Adhoc Dag Triggered after MP3 Upload") << streamlit 
    with Cluster("Storage"):
        s3 = S3("S3")
        Adhoc_Dag << Edge(label="Retrieve audio file") << s3
        Batch_Dag << Edge(label="") << s3  
        s3 << Edge(label="Mp3 File") << streamlit 
    with Cluster("Audio Transcription"):
        whisper = Custom("Whisper", "./whisper.png")
        whisper << Edge(label="Uploaded MP3 File") << s3  
        whisper << Edge(label="") << Adhoc_Dag
        whisper << Edge(label="Dag Triggered") << Batch_Dag
        s3 << Edge(label="Transcribed Text") << whisper
    with Cluster("Text Query"):
        gpt_api = Custom("GPT API", "./gpt.png")
        gpt_api << Edge(label="Generated text") << s3
        gpt_api << Edge(label="") << Adhoc_Dag
        gpt_api << Edge(label="Dag Triggered") << Batch_Dag                  
    ingress >> Edge(label="Submit audio file") << streamlit
    streamlit >> Edge(label="Query text") << gpt_api


    

    

    
        

    
    
    
    



    
     
        
    
        
    
        

