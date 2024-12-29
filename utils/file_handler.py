from google.cloud import storage
import os
import yaml

with open("/home/sangu/vakil-ai/config.yaml", "r") as config:
    config = yaml.safe_load(config)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config["service_account"]["path"]

bucket_name = config["storage"]["bucket_name"]

def upload_file_to_gcs(source_file, destination_blob, bucket_name=bucket_name):

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob)

    blob.upload_from_file(source_file, content_type="application/pdf")

    gcs_path = f"gs://{bucket_name}/{destination_blob}"

    return gcs_path 
