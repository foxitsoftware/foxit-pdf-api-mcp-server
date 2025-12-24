import os
from server.cloudapi_server import FoxitCloudAPI

def protect(input_file, output_file, password, owner_password,userPermissions,cipher,encryptMetadata):
    """
    Protect a PDF file with a password.

    Args:
        input_file (str): Path to the input PDF file.
        output_file (str): Path to the output protected PDF file.
        password (str): Password to protect the PDF file.

    Raises:
        Exception: If any step in the process fails.
    """
    # Initialize FoxitCloudAPI
    host = os.environ.get("FOXIT_CLOUD_API_HOST", None)
    client_id = os.environ.get("FOXIT_CLOUD_API_CLIENT_ID", None)
    client_secret = os.environ.get("FOXIT_CLOUD_API_CLIENT_SECRET", None)
    cloud_api = FoxitCloudAPI(host=host, client_id=client_id, client_secret=client_secret)

    # Upload file and get document ID
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"File not found: {input_file}")
    
    # Check if input is a PDF file
    if not input_file.lower().endswith('.pdf'):
        raise ValueError(f"Input file {input_file} is not a PDF file.")
    # Check if input is larger than 100MB
    if os.path.getsize(input_file) > 100 * 1024 * 1024:
        raise ValueError(f"Input file {input_file} is larger than 100MB.")
    
    # Check if output_file's path is valid
    if not os.path.exists(os.path.dirname(output_file)):
        raise FileNotFoundError(f"Output directory does not exist: {os.path.dirname(output_file)}")

    document_id = cloud_api.upload_document(input_file)

    # Construct request body for PDF protection
    #if password == owner_password:
    #    raise ValueError("User password and owner password cannot be the same.")
    if userPermissions is None:
        userPermissions = ["PRINT_HIGH_QUALITY", "EDIT_FILL_AND_SIGN_FORM_FIELDS"]
    if cipher is None:
        cipher = "AES_256"
    if encryptMetadata is None:
        encryptMetadata = True
    request_body = {
        "documentId": document_id,
        "config": {
            "userPassword": password,
            "ownerPassword": owner_password,
            "userPermissions": userPermissions,
            "cipher": cipher,
            "encryptMetadata": encryptMetadata
        }
    }

    # Submit protect task
    path = "/documents/security/pdf-protect"
    api_url = f"{cloud_api.host}{path}"
    headers = {
        "client_id": cloud_api.client_id,
        "client_secret": cloud_api.client_secret
    }
    try:
        response = cloud_api._make_request_with_retry("post", api_url, headers=headers, json=request_body)
    except Exception as e:
        raise Exception(f"Failed to submit protect task: {e}")
    task_id = response.json().get("taskId")
    if not task_id:
        code = response.json().get("code")
        message = response.json().get("message")
        raise Exception(f"Protect task submission failed: {code} - {message}")

    # Wait for task completion and download result
    cloud_api.wait_task_and_download_result(task_id, output_file)


def remove_password(input_file, output_file, password):
    """
    Remove password protection from a PDF file.

    Args:
        input_file (str): Path to the input PDF file.
        output_file (str): Path to the output unprotected PDF file.
        password (str): Password to unlock the PDF file.

    Raises:
        Exception: If any step in the process fails.
    """
    # Initialize FoxitCloudAPI
    host = os.environ.get("FOXIT_CLOUD_API_HOST", None)
    client_id = os.environ.get("FOXIT_CLOUD_API_CLIENT_ID", None)
    client_secret = os.environ.get("FOXIT_CLOUD_API_CLIENT_SECRET", None)
    cloud_api = FoxitCloudAPI(host=host, client_id=client_id, client_secret=client_secret)

    # Upload file and get document ID
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"File not found: {input_file}")
    document_id = cloud_api.upload_document(input_file)

    # Construct request body for removing password
    request_body = {
        "documentId": document_id,
        "password": password
    }

    # Submit remove password task
    path = "/documents/security/pdf-remove-password"
    api_url = f"{cloud_api.host}{path}"
    headers = {
        "client_id": cloud_api.client_id,
        "client_secret": cloud_api.client_secret
    }
    try:
        response = cloud_api._make_request_with_retry("post", api_url, headers=headers, json=request_body)
    except Exception as e:
        raise Exception(f"Failed to submit remove password task: {e}")
    task_id = response.json().get("taskId")
    if not task_id:
        code = response.json().get("code")
        message = response.json().get("message")
        raise Exception(f"Remove password task submission failed: {code} - {message}")

    # Wait for task completion and download result
    cloud_api.wait_task_and_download_result(task_id, output_file)
