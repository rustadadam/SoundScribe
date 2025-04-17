import json
import boto3
import os
import time

# Initialize AWS clients to interact with S3, EC2, and SSM
s3_client = boto3.client("s3")
ec2_client = boto3.client("ec2")
ssm_client = boto3.client("ssm")

# EC2 Instance configuration details
EC2_INSTANCE_ID = "i-0f0a13b309bef74b7"  # EC2 instance ID where the NLP script is located
EC2_USER = "ec2-user"                   # Username for connecting to the EC2 instance
S3_BUCKET_NAME = "sound-scribe-acessories"  # S3 bucket where the private key is stored
S3_KEY_PATH = "book-tagging.pem"           # S3 key (object path) for the private key file
PRIVATE_KEY_PATH = "/tmp/book-tagging.pem"   # Local temporary path to store the downloaded private key

def download_private_key():
    """
    Downloads a private key file from S3 to a local temporary directory and sets secure file permissions.
    """
    print("Downloading private key from S3...")
    # Download the private key from the specified S3 bucket and key
    s3_client.download_file(S3_BUCKET_NAME, S3_KEY_PATH, PRIVATE_KEY_PATH)
    
    # Set file permissions to read-only for the owner (octal 400)
    os.chmod(PRIVATE_KEY_PATH, 0o400)
    print(f"Private key saved to {PRIVATE_KEY_PATH}")

def lambda_handler(event, context):
    """
    AWS Lambda handler function triggered by S3 events.
    Processes incoming S3 event records, validates text file extensions, downloads the required
    private key, and sends a command to an EC2 instance via SSM to process the file.
    """
    # Iterate over each incoming S3 event record
    for record in event["Records"]:
        # Extract the bucket name and S3 object key from the event record
        bucket_name = record["s3"]["bucket"]["name"]
        s3_key = record["s3"]["object"]["key"]

        # Ensure the file is a text file (.txt extension) before processing
        if not s3_key.endswith(".txt"):
            print(f"Skipping non-text file: {s3_key}")
            return  # Exit early if the file isn't a .txt file

        print(f"New text file detected: {s3_key}")

        # Download the private key needed for secure connection to the EC2 instance
        download_private_key()

        # Construct the bash command to activate a virtual environment and run a Python script on the EC2 instance.
        command = f"/bin/bash -c 'source /home/ec2-user/SoundScribe/.venv/bin/activate && python /home/ec2-user/SoundScribe/book_nlp_s3.py {s3_key}'"

        # Retrieve instance information to ensure the EC2 instance is registered with SSM
        ssm_instances = ssm_client.describe_instance_information()
        ssm_instance_ids = [inst["InstanceId"] for inst in ssm_instances["InstanceInformationList"]]

        # Raise an exception if the target EC2 instance isn't connected to SSM
        if EC2_INSTANCE_ID not in ssm_instance_ids:
            raise Exception(f"EC2 instance {EC2_INSTANCE_ID} is NOT registered with SSM.")

        # Send the constructed command to the specified EC2 instance via SSM to execute it remotely
        response = ssm_client.send_command(
            InstanceIds=[EC2_INSTANCE_ID],
            DocumentName="AWS-RunShellScript",
            Parameters={"commands": [command]},
        )

        # Extract and log the command ID for tracking
        command_id = response['Command']['CommandId']
        print(f"Command sent. Command ID: {command_id}")