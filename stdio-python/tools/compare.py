import os
from server.cloudapi_server import FoxitCloudAPI

def compare(pdf1, pdf2, output_file, config=None):
    """
    Compare two PDF files and save the comparison result.

    Args:
        pdf1 (str): Path to the first PDF file.
        pdf2 (str): Path to the second PDF file.
        output_file (str): Path to save the comparison result.
        config (dict, optional): Comparison configuration.
            - compareType (str): Type of comparison. Options:
                * "ALL" (default): Compare all content.
                * "TEXT": Compare text content only.
                * "ANNOTATION": Compare annotations only.
                * "TEXT_AND_ANNOTATION": Compare text and annotations.
            - resultType (str): Result format. Options:
                * "JSON": Machine-readable difference report.
                * "PDF" (default): Visual difference document.

    Raises:
        Exception: If any step in the process fails.
    """
    # Initialize FoxitCloudAPI
    host = os.environ.get("FOXIT_CLOUD_API_HOST")
    client_id = os.environ.get("FOXIT_CLOUD_API_CLIENT_ID")
    client_secret = os.environ.get("FOXIT_CLOUD_API_CLIENT_SECRET")
    cloud_api = FoxitCloudAPI(host, client_id, client_secret)

    #check if input files exist
    if not os.path.exists(pdf1):
        raise FileNotFoundError(f"File not found: {pdf1}")
    if not os.path.exists(pdf2):
        raise FileNotFoundError(f"File not found: {pdf2}")
    
    #check if input is pdf files
    if not pdf1.lower().endswith('.pdf'):
        raise ValueError(f"Input file {pdf1} is not a PDF file.")
    if not pdf2.lower().endswith('.pdf'):
        raise ValueError(f"Input file {pdf2} is not a PDF file.")

    #check if input is larger than 100MB
    if os.path.getsize(pdf1) > 100 * 1024 * 1024:
        raise ValueError(f"Input file {pdf1} is larger than 100MB.")
    if os.path.getsize(pdf2) > 100 * 1024 * 1024:
        raise ValueError(f"Input file {pdf2} is larger than 100MB.")
    
    # Check if output_file's path is valid
    if not os.path.exists(os.path.dirname(output_file)):
        raise FileNotFoundError(f"Output directory does not exist: {os.path.dirname(output_file)}")

    # Upload PDFs
    base_document_id = cloud_api.upload_document(pdf1)
    compare_document_id = cloud_api.upload_document(pdf2)

    # Default config
    if config is None:
        config = {
            "compareType": "ALL",
            "resultType": "PDF"
        }

    # Construct request body
    request_body = {
        "baseDocument": {"documentId": base_document_id},
        "compareDocument": {"documentId": compare_document_id},
        "config": config
    }

    # Submit compare task
    path = "/documents/analyze/pdf-compare"
    api_url = f"{cloud_api.host}{path}"
    headers = {
        "client_id": cloud_api.client_id,
        "client_secret": cloud_api.client_secret
    }
    try:
        response = cloud_api._make_request_with_retry("post", api_url, headers=headers, json=request_body)
    except Exception as e:
        raise Exception(f"Failed to submit compare task: {e}")
    task_id = response.json().get("taskId")
    if not task_id:
        raise Exception("Failed to submit compare task.")

    # Wait for task completion and download result
    cloud_api.wait_task_and_download_result(task_id, output_file)
