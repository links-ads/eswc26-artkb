import logging
import os
import sys

import boto3
import requests
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

logging.basicConfig(
    level=logging.INFO,  
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)] 
)

log = logging.getLogger(__name__)

log.info("Loading environment variables...")
# Carica il file .env
load_dotenv()

# =====================================================
# MinIO Configuration
log.info("Configuring MinIO service...")

MINIO_ENDPOINT = f"http://{os.getenv('MINIO_HOST')}:{os.getenv('MINIO_PORT')}"
IMG_BUCKET_NAME = os.getenv("MINIO_IMAGE_BUCKET_NAME") 
FILE_BUCKET_NAME = os.getenv("MINIO_FILE_BUCKET_NAME") 

# Creazione client MinIO
s3_client = boto3.client(
    "s3",
    endpoint_url=MINIO_ENDPOINT,
    aws_access_key_id=os.getenv("MINIO_ROOT_USER"),
    aws_secret_access_key=os.getenv("MINIO_ROOT_PASSWORD"),
)

try:
    s3_client.head_bucket(Bucket=IMG_BUCKET_NAME)
    log.info(f"Bucket {IMG_BUCKET_NAME} already exists")
except:
    s3_client.create_bucket(Bucket=IMG_BUCKET_NAME)
    log.info(f"Bucket {IMG_BUCKET_NAME} created")

try:
    s3_client.head_bucket(Bucket=FILE_BUCKET_NAME)
    log.info(f"Bucket {FILE_BUCKET_NAME} already exists")
except:
    s3_client.create_bucket(Bucket=FILE_BUCKET_NAME)
    log.info(f"Bucket {FILE_BUCKET_NAME} created")

log.info("Configuration of MinIO completed.")

# =====================================================
# QDrant Configuration

log.info("Configuring QDrant service...")
client = QdrantClient(url=f"http://{os.getenv('QDRANT_HOST')}:{os.getenv('QDRANT_PORT')}", api_key=os.getenv("QDRANT_API_KEY"))

collection_name = os.getenv("QDRANT_COLLECTION_NAME")

if client.collection_exists(collection_name=collection_name):
    log.info(f"Collection {collection_name} already exists")
else:
    log.info(f"Creating collection {collection_name}...")

    client.create_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(size=int(os.getenv("QDRANT_COLLECTION_SIZE")), distance=models.Distance.COSINE),
    )

log.info("Configuration of Qdrant completed.")

# =====================================================
# GraphDB Configuration
log.info("Configuring GraphDB service...")


GRAPHDB_BASE_URL = f"http://{os.getenv('GRAPHDB_HOST')}:{os.getenv('GRAPHDB_PORT')}"
ROOT_USER = os.getenv("GRAPHDB_ROOT_USER")
ROOT_PASSWORD = os.getenv("GRAPHDB_ROOT_PASSWORD")
REPO_NAME = os.getenv("GRAPHDB_REPO_NAME")

USER_NAME = os.getenv("GRAPHDB_USER")
USER_PASSWORD = os.getenv("GRAPHDB_PASSWORD")

auth = (ROOT_USER, ROOT_PASSWORD)

security_url = f"{GRAPHDB_BASE_URL}/rest/security"

response = requests.request("GET", security_url, auth=auth)

log.info("Enabling security on GraphDB service...")
if response.status_code != 200:
    log.error("Error contacting GraphDB for security status")
    exit()
else:
    security_status = response.json()

if security_status:
    log.info("Security already enabled")
else:
    headers = {
            'Content-Type': 'application/json'  # Nessun charset=UTF-8
    }

    response = requests.request("POST", security_url, headers=headers, data="true")
    if response.status_code != 200:
        log.info(f"Errore while enabling security: {response.text}")
        exit()
    else:
        log.info(f"Security successfully enabled")

# Endpoint per la creazione di un repository
log.info("Creating repository on GraphDB service...")

repo_url = f"{GRAPHDB_BASE_URL}/rest/repositories"

response = requests.request("GET", repo_url, auth=auth)

if response.status_code != 200:
    log.error(f"Error while listing repositories: {response.text}")
    exit()

result = response.json()
if REPO_NAME not in [repo["id"] for repo in result]:

    log.info(f"Repository {REPO_NAME} does not esists, creating...")

    url = f"{GRAPHDB_BASE_URL}/repositories/{REPO_NAME}"

    with open("repo-config.ttl", "r") as file:
        data = file.read()
        data = data.replace("REPO_NAME", REPO_NAME)
        
    headers = {
            'Content-Type': 'text/turtle'  # Nessun charset=UTF-8
    }

    response = requests.put(url, auth=auth, data=data, headers=headers)

    if response.status_code != 204:
        log.info(f"Error while creating repository: {response.text}")
        exit()
    else:
        log.info(f"Repository {REPO_NAME} successfully created!")
else:
    log.info(f"Repository {REPO_NAME} already exists")
# Create new USER

url = f"{GRAPHDB_BASE_URL}/rest/security/users/{USER_NAME}"

headers = {
    'Content-Type': 'application/json'  # Nessun charset=UTF-8
}

data = {
    "username": USER_NAME,
    "password": USER_PASSWORD,
    "grantedAuthorities": [f"WRITE_REPO_{REPO_NAME}", f"READ_REPO_{REPO_NAME}"]
}

response = requests.post(url, auth=auth, json=data, headers=headers)

if response.status_code != 201:
    log.info(f"Error while creating user: {response.text}")
    exit()
else:
    log.info(f"User {USER_NAME} successfully created!")

log.info("Configuration of GraphDB completed.")
log.info("Configuration completed.")