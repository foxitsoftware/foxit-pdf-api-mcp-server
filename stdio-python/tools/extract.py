import os
from server.cloudapi_server import FoxitCloudAPI

def extract(input_file, output_dir, password = "",extract_type="TEXT", page_range="all"):
    """
    Extract content (text, images, or pages) from a PDF file using Foxit Cloud API.

    Args:
        input_file (str): Path to the input PDF file.
        output_dir (str): Directory to save the extracted content.
        extract_type (str): Type of content to extract ("TEXT", "IMAGE", "PAGE").
        page_range (str): Page range to extract (e.g., "1-5", "all").

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
    
    # Check if output_dir is a file path or directory
    output_file_name = None
    if os.path.splitext(output_dir)[1]:  # Has extension, treat as file path
        #get filename from path
        output_file_name = os.path.basename(output_dir)
        output_file_name = os.path.splitext(output_file_name)[0]
        output_dir = os.path.dirname(output_dir)
        
    if not os.path.exists(output_dir):
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")
   
    # check if input is pdf file
    if not input_file.lower().endswith('.pdf'):
        raise ValueError(f"Input file {input_file} is not a PDF file.")
    
    # check if input is larger than 100MB
    if os.path.getsize(input_file) > 100 * 1024 * 1024:
        raise ValueError(f"Input file {input_file} is larger than 100MB.")
    
    document_id = cloud_api.upload_document(input_file)

    # Construct request body for PDF extract
    request_body = {
        "documentId": document_id,
        "extractType": extract_type,
        "pageRange": page_range,
        "password": password
    }

    # Submit extract task
    path = "/documents/modify/pdf-extract"
    api_url = f"{cloud_api.host}{path}"
    headers = {
        "client_id": cloud_api.client_id,
        "client_secret": cloud_api.client_secret
    }
    try:
        response = cloud_api._make_request_with_retry("post", api_url, headers=headers, json=request_body)
    except Exception as e:
        raise Exception(f"Failed to submit extract task: {e}")
    task_id = response.json().get("taskId")
    if not task_id:
        code = response.json().get("code")
        message = response.json().get("message")
        raise Exception(f"Extract task submission failed: {code} - {message}")

    # Wait for task completion and download result
    if not output_file_name:
        output_file_name = f"extracted_{extract_type.lower()}.zip" if extract_type == "IMAGE" else f"extracted_{extract_type.lower()}.txt"
    else:
        output_file_name = output_file_name + ".zip" if extract_type == "IMAGE" else output_file_name + ".txt"
    result_file = os.path.join(output_dir, f"{output_file_name}")
    cloud_api.wait_task_and_download_result(task_id, result_file)
    print(f"Extraction completed. Result saved to {result_file}")
