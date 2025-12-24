import os
import json

def load_env(host, client_id, client_secret):
    # Validate input parameters
    if not host:
        raise ValueError("Error: 'host' parameter is required but not provided.")
    if not client_id:
        raise ValueError("Error: 'client_id' parameter is required but not provided.")
    if not client_secret:
        raise ValueError("Error: 'client_secret' parameter is required but not provided.")

    # Use the passed parameters instead of reading from settings.json
    print(f"Environment loaded with host: {host}, client_id: {client_id}, client_secret: {client_secret}")
    os.environ["FOXIT_CLOUD_API_HOST"] = host
    os.environ["FOXIT_CLOUD_API_CLIENT_ID"] = client_id
    os.environ["FOXIT_CLOUD_API_CLIENT_SECRET"] = client_secret