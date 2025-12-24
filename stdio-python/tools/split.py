import os
from server.cloudapi_server import FoxitCloudAPI
# def get_output_file_path(output_dir, default_filename):
#     """
#     Get the correct output file path based on whether output_dir is a file or directory.
    
#     Args:
#         output_dir (str): The output directory or file path
#         default_filename (str): Default filename to use if output_dir is a directory
        
#     Returns:
#         str: The complete file path for output
#     """
#     # Check if output_dir has a file extension (likely a file path)
#     if os.path.splitext(output_dir)[1]:  # Has extension
#         # Treat as file path
#         directory = os.path.dirname(output_dir)
#         if directory and not os.path.exists(directory):
#             os.makedirs(directory, exist_ok=True)
#         return output_dir
#     else:
#         # Treat as directory path
#         if not os.path.exists(output_dir):
#             os.makedirs(output_dir, exist_ok=True)
#         return os.path.join(output_dir, default_filename)
    
def split(input_file, output_dir, split_by_pages):
    """
    Split a PDF file into multiple files using Foxit Cloud API.

    Args:
        input_file (str): Path to the input PDF file.
        output_dir (str): Directory to save the split PDF files.
        split_by_pages (int): Number of pages per split file.

    Raises:
        Exception: If any step in the process fails.
    """
    # Initialize FoxitCloudAPI
    host = os.environ.get("FOXIT_CLOUD_API_HOST", None)
    client_id = os.environ.get("FOXIT_CLOUD_API_CLIENT_ID", None)
    client_secret = os.environ.get("FOXIT_CLOUD_API_CLIENT_SECRET", None)
    cloud_api = FoxitCloudAPI(host=host, client_id=client_id, client_secret=client_secret)

    # Upload the file and get document ID
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"File not found: {input_file}")
    
    # Check if input is a PDF file
    if not input_file.lower().endswith('.pdf'):
        raise ValueError(f"Input file {input_file} is not a PDF file.")
    
    # Check if input is larger than 100MB
    if os.path.getsize(input_file) > 100 * 1024 * 1024:
        raise ValueError(f"Input file {input_file} is larger than 100MB.")
    
    # Check if output_dir's path is valid
    if os.path.splitext(output_dir)[1]:  # Has extension, treat as file path
         #get filename from path
        output_file_name = os.path.basename(output_dir)
        output_file_name = os.path.splitext(output_file_name)[0]
        output_dir = os.path.dirname(output_dir)
    if not os.path.exists(output_dir):
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")
    
    document_id = cloud_api.upload_document(input_file)

    # Construct request body for PDF split
    request_body = {
        "documentId": document_id,
        "pageCount": split_by_pages
    }

    # Submit split task
    path = "/documents/modify/pdf-split"
    api_url = f"{cloud_api.host}{path}"
    headers = {
        "client_id": cloud_api.client_id,
        "client_secret": cloud_api.client_secret
    }
    try:
        response = cloud_api._make_request_with_retry("post", api_url, headers=headers, json=request_body)
    except Exception as e:
        raise Exception(f"Failed to submit split task: {e}")
    task_id = response.json().get("taskId")
    if not task_id:
        code = response.json().get("code")
        message = response.json().get("message")
        raise Exception(f"Split task submission failed: {code} - {message}")    # 使用工具函数获取正确的输出文件路径
    if not output_file_name:
        output_file_name = "split_results"
    output_path = os.path.join(output_dir, f"{output_file_name}.zip")
    # Wait for task completion and download results
    cloud_api.wait_task_and_download_result(task_id, output_path)
