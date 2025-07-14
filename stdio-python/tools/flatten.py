import os
from server.cloudapi_server import FoxitCloudAPI

def flatten(input_file, output_file,password=""):
    """
    Flatten a PDF file (e.g., remove interactive elements).

    Args:
        input_file (str): Path to the input PDF file.
        output_file (str): Path to the output flattened PDF file.
        password (str, optional): Password for the PDF file if it is encrypted. Default is an empty string.
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
    
    # check if input is pdf file
    if not input_file.lower().endswith('.pdf'):
        raise ValueError(f"Input file {input_file} is not a PDF file.")
    
    # check if input is larger than 100MB
    if os.path.getsize(input_file) > 100 * 1024 * 1024:
        raise ValueError(f"Input file {input_file} is larger than 100MB.")
    
    # Check if output_file's path is vaild
    if not os.path.exists(os.path.dirname(output_file)):
        raise FileNotFoundError(f"Output directory does not exist: {os.path.dirname(output_file)}")
    
    document_id = cloud_api.upload_document(input_file)

    # Construct request body for PDF flatten
    request_body = {
        "documentId": document_id,
        "password": password
    }

    # Submit flatten task
    path = "/documents/modify/pdf-flatten"
    api_url = f"{cloud_api.host}{path}"
    headers = {
        "client_id": cloud_api.client_id,
        "client_secret": cloud_api.client_secret
    }
    try:
        response = cloud_api._make_request_with_retry("post", api_url, headers=headers, json=request_body)
    except Exception as e:
        raise Exception(f"Failed to submit flatten task: {e}")
    task_id = response.json().get("taskId")
    if not task_id:
        code = response.json().get("code")
        message = response.json().get("message")
        raise Exception(f"Flatten task submission failed: {code} - {message}")

    # Wait for task completion and download result
    cloud_api.wait_task_and_download_result(task_id, output_file)
