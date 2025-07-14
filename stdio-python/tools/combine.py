import os
from server.cloudapi_server import FoxitCloudAPI

def combine(input_files, output_file, config=None):
    """
    Combine multiple PDF files into a single PDF file using Foxit Cloud API.

    Args:
        input_files (list): List of input PDF file paths.
        output_file (str): Path to save the combined PDF file.

    Raises:
        Exception: If any step in the process fails.
    """
    # Initialize FoxitCloudAPI
    host = os.environ.get("FOXIT_CLOUD_API_HOST", None)
    client_id = os.environ.get("FOXIT_CLOUD_API_CLIENT_ID", None)
    client_secret = os.environ.get("FOXIT_CLOUD_API_CLIENT_SECRET", None)
    cloud_api = FoxitCloudAPI(host=host, client_id=client_id, client_secret=client_secret)

    # Upload files and collect document IDs
    document_infos = []
    for file_path in input_files:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        # check if input is pdf files
        if not file_path.lower().endswith('.pdf'):
            raise ValueError(f"Input file {file_path} is not a PDF file.")
        #check if input is larger than 100MB
        if os.path.getsize(file_path) > 100 * 1024 * 1024:
            raise ValueError(f"Input file {file_path} is larger than 100MB.")
        document_id = cloud_api.upload_document(file_path)
        document_infos.append({"documentId": document_id})
    
    # Check if output_file's path is valid
    if not os.path.exists(os.path.dirname(output_file)):
        raise FileNotFoundError(f"Output directory does not exist: {os.path.dirname(output_file)}")

    # Use provided config or default values
    if config is None:
        config = {
            "addBookmark": True,
            "continueMergeOnError": True,
            "retainPageNumbers": False,
            "addTOC": True,
            "tocBookmarkLevels": "1-3",
            "tocTitle": "Combined Document"
        }

    # Construct request body for PDF combine
    request_body = {
        "documentInfos": document_infos,
        "config": config
    }

    # Submit combine task
    path = "/documents/enhance/pdf-combine"
    api_url = f"{cloud_api.host}"+path
    headers = {
        "client_id": cloud_api.client_id,
        "client_secret": cloud_api.client_secret
    }
    try:
        response = cloud_api._make_request_with_retry("post", api_url, headers=headers, json=request_body)
    except Exception as e:
        raise Exception(f"Failed to submit combine task: {e}")
    task_id = response.json().get("taskId")
    if not task_id:
        code = response.json().get("code")
        message = response.json().get("message")
        raise Exception(f"Combine task submission failed: {code} - {message}")

    # Wait for task completion and download result
    cloud_api.wait_task_and_download_result(task_id, output_file)
