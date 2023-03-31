# Big Data Systems & Intelligence Analytics

## Team Information
| Name     | NUID        |
| ---      | ---         |
| Meet     | 002776055   |
| Ajin     | 002745287   |
| Siddhi   | 002737346   |
| Akhil    | 002766590   |

## About
This repository contains a collection of Big Data Systems & Intelligence Analytics Assignments & Projects that utilize the power of AWS and SQLite to process and analyze data using Streamlit. The assignments are designed to showcase the capabilities of these technologies in handling and processing large and complex datasets in real-time. The assignments cover various topics such as data ingestion, data processing, data storage, and data analysis, among others. Whether you are a big data enthusiast or a professional looking to build your skills in this field, this repository is a great resource to get started. So, go ahead, fork the repository and start working on these assignments to take your big data skills to the next level!

## DAMG7245_Assignment_4

# Link to Live Applications
- Streamlit Application - 
- Airflow - 
- Codelabs - 

### Case summary


### Project Tree:

```bash
.
└── Assignment_4
    ├── airflow
    │   ├── .env
    │   ├── dags
    │   │   ├── adhoc_dag.py
    │   │   └── batch_dag.py
    │   ├── docker-compose.yaml
    │   ├── logs
    │   └── plugins
    ├── arch-diag
    │   ├── arch-diag.py
    ├── .env
    ├── .gitignore
    ├── DAMG7245 Assignment 04.pdf
    ├── main_functions.py
    ├── meeting-intelligence-application.jpeg
    ├── README.md
    ├── requirements.txt
    └── streamlit.py
```

### Prerequisites
To run this project, you will need:
* IDE
* Python 3.x
* Google Cloud Platform account
* Docker
* AWS Access,Secret, log access and log secret keys
* .env file containing the AWS keys in the same directory as the airflow DAGs docker compose

```bash
python -m venv assgn4_venv
source assgn4_venv\bin\activate
```

### Process Flow
* Create a python virtual environment and activate
```bash
python -m venv assgn4_venv
```

* Activate the virtual environment
```bash
source env/bin/activate  # on Linux/macOS
env\Scripts\activate     # on Windows
```

* Install the required packages from requirements.txt file
```bash
pip install -r requirements.txt
```

* Run Streamlit app
```bash
streamlit run streamlit.py
```

### .env file for airflow:
- AWS_ACCESS_KEY = <AWS_ACCESS_KEY>
- AWS_SECRET_KEY = <AWS_SECRET_KEY>
- AWS_LOGS_ACCESS_KEY = <AWS_LOGS_ACCESS_KEY>
- AWS_LOGS_SECRET_KEY = <AWS_LOGS_SECRET_KEY>

### .env file for fastapi and streamlit:
- AWS_ACCESS_KEY = <AWS_ACCESS_KEY>
- AWS_SECRET_KEY = <AWS_SECRET_KEY>
- AWS_LOGS_ACCESS_KEY = <AWS_LOGS_ACCESS_KEY>
- AWS_LOGS_SECRET_KEY = <AWS_LOGS_SECRET_KEY>

========================================================================================================================
> WE ATTEST THAT WE HAVEN’T USED ANY OTHER STUDENTS’ WORK IN OUR ASSIGNMENT AND ABIDE BY THE POLICIES LISTED IN THE STUDENT HANDBOOK.
> Meet: 25%, Ajin: 25%, Siddhi: 25%, Akhil: 25%
