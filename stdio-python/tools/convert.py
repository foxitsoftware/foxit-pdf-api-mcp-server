import os
from server.cloudapi_server import FoxitCloudAPI

to_pdf_tools= {
    "word":{
        "path":"documents/create/pdf-from-word",
    },
    "text":{
        "path":"documents/create/pdf-from-text",
    },
    "ppt":{
        "path":"documents/create/pdf-from-ppt",
    },
    "excel":{
        "path":"documents/create/pdf-from-excel",
    },
    "image":{
        "path":"documents/create/pdf-from-image",
    },
    "html":{
        "path":"documents/create/pdf-from-html",
            "config": {
            "dimension": {
            "width": "595",
            "height": "842"
            },
            "rotation": "NONE",
            "pageMode": "MULTIPLE_PAGE",
            "scalingMode": "SCALE"
        }
    }
}

"""
Submit a task to convert a url to PDF.
Return the task ID if success. Other Raise an exception.
"""
def _sumbit_convert_url_to_pdf_task(cloud_api,url:str) -> str:
    path = "documents/create/pdf-from-url"
    api_url = f"{cloud_api.host}/{path}"
    headers = {
        "client_id": f"{cloud_api.client_id}",
        "client_secret":f"{cloud_api.client_secret}"
    }
    data = {
        "url": url,
        "config": {
                "dimension": {
                "width": "595",
                "height": "842"
                },
                "rotation": "NONE",
                "pageMode": "MULTIPLE_PAGE",
                "scalingMode": "SCALE"
        }   
    }
    try:
        response = cloud_api._make_request_with_retry("post", api_url, headers=headers, json=data)
    except Exception as e:
        raise Exception(f"submit convert url task failed: {e}")
    taskId = response.json().get("taskId")
    if not taskId:
        code = response.json().get("code")
        message = response.json().get("message")
        raise Exception(f"submit convert task failed: {code} - {message}")
    return taskId

"""
Sumbit a task to convert the document to PDF.
Return the task ID if success. Other Raise an exception.
"""
def _sumbit_convert_to_pdf_task(cloud_api,document_id:str, original_format:str) -> str:
    if not original_format in to_pdf_tools.keys():
        raise Exception(f"Unsupported format: {original_format}. Supported formats are {to_pdf_tools.keys()}")
    
    path = to_pdf_tools[original_format]["path"]
    config = to_pdf_tools[original_format].get("config", {})
    url = f"{cloud_api.host}/{path}"
    headers = {
        "client_id": f"{cloud_api.client_id}",
        "client_secret":f"{cloud_api.client_secret}"
    }
    data = {
        "documentId": document_id,
    }
    
    data.update(config)
    
    response = cloud_api._make_request_with_retry("post", url, headers=headers, json=data)
    taskId = response.json().get("taskId")
    if not taskId:
        code = response.json().get("code")
        message = response.json().get("message")
        raise Exception(f"submit convert task failed: {code} - {message}")
    return taskId
    

def convert_file(file_path: str, output_file:str, file_format:str=None):
    print (f"convert_file_to_pdf processing, file_path: {file_path}, output_path: {output_file}")
    host = os.environ.get("FOXIT_CLOUD_API_HOST", None)
    client_id = os.environ.get("FOXIT_CLOUD_API_CLIENT_ID", None)
    client_secret = os.environ.get("FOXIT_CLOUD_API_CLIENT_SECRET",None)
    print(f"host: {host}, client_id: {client_id}, client_secret: {client_secret}")
    cloud_api = FoxitCloudAPI(host=host, client_id=client_id, client_secret=client_secret)
  
    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    # check if the file is larger than 100MB
    if os.path.getsize(file_path) > 100 * 1024 * 1024:
        raise ValueError(f"File {file_path} is larger than 100MB.")
    
    # Check if the output path is valid
    if not os.path.exists(os.path.dirname(output_file)):
        raise FileNotFoundError(f"Output directory does not exist: {os.path.dirname(output_file)}")

    if file_format == None:
        file_format = cloud_api.get_file_format(file_path)
    print(f"Convert to File format: {file_format}")
    # Upload the file
    document_id = cloud_api.upload_document(file_path)
    print(f"Document ID: {document_id}")
    try:
        # Submit conversion task
        task_id = _sumbit_convert_to_pdf_task(cloud_api,document_id, file_format)
    except Exception as e:
        raise Exception(f"Failed to submit conversion task: {e}")
    print(f"Task ID: {task_id}")
    # Wait for task to complete and download the result
    cloud_api.wait_task_and_download_result(task_id, output_file)
        
def convert_url( url:str, output_path:str):
    host = os.environ.get("FOXIT_CLOUD_API_HOST", None)
    client_id = os.environ.get("FOXIT_CLOUD_API_CLIENT_ID", None)
    client_secret = os.environ.get("FOXIT_CLOUD_API_CLIENT_SECRET",None)
    print(f"host: {host}, client_id: {client_id}, client_secret: {client_secret}")
    cloud_api = FoxitCloudAPI(host=host, client_id=client_id, client_secret=client_secret)
    # Submit conversion task
    try:
        task_id = _sumbit_convert_url_to_pdf_task(cloud_api,url)
    except Exception as e:
        raise Exception(f"Failed to submit conversion task: {e}")
    # Wait for task to complete and download the result
    cloud_api.wait_task_and_download_result(task_id, output_path)

