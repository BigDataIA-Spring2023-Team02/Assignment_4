from diagrams import Cluster, Edge, Diagram
from diagrams.onprem.client import User, Users
from diagrams.onprem.container import Docker
from diagrams.onprem.workflow import Airflow
from diagrams.aws.storage import SimpleStorageServiceS3 as S3
from diagrams.onprem.network import Nginx
from diagrams.onprem.database import Postgresql as PostgreSQL
from diagrams.oci.monitoring import Telemetry
from diagrams.aws.database import RDS
from diagrams.custom import Custom

with Diagram("Meeting Intelligence Application", show=False):
    # Defining Nodes
    ingress = Users("User")
    with Cluster("Application Instances"):
        with Cluster("Applications"):
            backend = Docker("FastAPI")
            Edge(label="API calls", color="red", style="dashed") - backend

        with Cluster("SQLite Database"):
            db = RDS("IAM")

        with Cluster("Batch Process"):
            airflow = Airflow("Airflow")
            GE = Telemetry("Data Quality Check")
            hosting = Nginx("Reports")

    backend << Edge(label="Verify Login") << db
    devlopers = User("Developers")
    dataset = S3("Open Dataset")

    GE << Edge(label="CSV of metadata") << db
    GE >> Edge(label="Host the static html report") >> hosting
    airflow >> Edge(label="Run Great Expectation") >> GE

    airflow << Edge(label="metadata collection") << dataset
    airflow >> Edge(label="Update AWS bucket metadata") >> db

    ingress >> Edge(label="Login to Dashboard", color="darkgreen")
    devlopers << Edge(label="View Reports", color="darkgreen") << hosting
    devlopers << Edge(label="View Dashboard", color="darkgreen") << airflow