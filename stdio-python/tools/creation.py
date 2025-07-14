import os
from server.cloudapi_server import FoxitCloudAPI

# Tools for creating files from PDF
# The keys are the file formats, and the values are dictionaries containing the API path for each format.

create_file_tools = {
    "word": {
        "path": "documents/convert/pdf-to-word",
    },
    "text": {
        "path": "documents/convert/pdf-to-text",
    },
    "ppt": {
        "path": "documents/convert/pdf-to-ppt",
    },
    "excel": {
        "path": "documents/convert/pdf-to-excel",
    },
    "image": {
        "path": "documents/convert/pdf-to-image",  # This will return a zip file containing images
    },
    "html": {
        "path": "documents/convert/pdf-to-html",
    }
}

def _submit_create_pdf_task(cloud_api, document_id:str, config:str,file_format:str) -> str:

    print (f"Submitting create task for document ID: {document_id} with format: {file_format}")
    if file_format is None or file_format not in create_file_tools:
        print (f"Unsupported format: {file_format}. Supported formats are txt, docx, pptx, xlsx, jpeg, png, html)")
        raise Exception(f"Unsupported format: {file_format}. Supported formats are txt, docx, pptx, xlsx, jpeg, png, html")
    
    path = create_file_tools[file_format]["path"]
    api_url = f"{cloud_api.host}/{path}"
    headers = {
        "client_id": f"{cloud_api.client_id}",
        "client_secret": f"{cloud_api.client_secret}"
    }
    data = {
        "documentId": document_id,
    }
    if config is not None:
        data.update(config)
    try:
        response = cloud_api._make_request_with_retry("post", api_url, headers=headers, json=data)
    except Exception as e:
        raise Exception(f"Submit create task failed: {e}")
    task_id = response.json().get("taskId")
    if not task_id:
        code = response.json().get("code")
        message = response.json().get("message")
        raise Exception(f"Submit create task failed: {code} - {message}")
    return task_id

def create_file(file_path, output_file,config=None,file_format=None):
    host = os.environ.get("FOXIT_CLOUD_API_HOST", None)
    client_id = os.environ.get("FOXIT_CLOUD_API_CLIENT_ID", None)
    client_secret = os.environ.get("FOXIT_CLOUD_API_CLIENT_SECRET", None)
    cloud_api = FoxitCloudAPI(host=host, client_id=client_id, client_secret=client_secret)
     # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    # Check if the file is larger than 100MB
    if os.path.getsize(file_path) > 100 * 1024 * 1024:
        raise ValueError(f"File {file_path} is larger than 100MB.")
    # Check if the file is a PDF
    if not file_path.lower().endswith('.pdf'):
        raise ValueError(f"Input file {file_path} is not a PDF file.")
    # Check if output_file's path is valid
    if not os.path.exists(os.path.dirname(output_file)):
        raise FileNotFoundError(f"Output directory does not exist: {os.path.dirname(output_file)}")
    # Upload the file
    document_id = cloud_api.upload_document(file_path)
    print(f"Document ID: {document_id}")
    if file_format == None:
        file_format = cloud_api.get_file_format(output_file)
    # Submit creation task
    try:
        task_id = _submit_create_pdf_task(cloud_api, document_id,config,file_format)
    except Exception as e:
        raise Exception(f"Failed to submit create task: {e}")
    print(f"Task ID: {task_id}")
    # Wait for task to complete and download the result
    if file_format == "image":
        #将output_file的后缀改为zip，因为返回的是zip文件
        output_file = os.path.splitext(output_file)[0] + ".zip"
    print(f"Output file: {output_file}")
    cloud_api.wait_task_and_download_result(task_id, output_file)
