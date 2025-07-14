from typing import Any
import httpx
import os
import time
import random
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cloudapi_server.log"),
        logging.StreamHandler()
    ]
)


class FoxitCloudAPI:
    def __init__(self, host, client_id,client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.host = host  
    
    def _make_request_with_retry(self, method, url, **kwargs):
        """
        Make an HTTP request with retry logic for 429 errors
        
        Args:
            method: HTTP method (get, post, etc.)
            url: Request URL
            **kwargs: Additional arguments to pass to the request
            
        Returns:
            httpx.Response object
        """
        max_retries = 15
        retry_count = 0
        base_wait_time = 1  # Initial wait time in seconds
        max_wait_time = 60  # Maximum wait time in seconds
        while True:
            logging.info(f"Request url: {url}")
            logging.info(f"Request Headers: {kwargs.get('headers')}")
            logging.info(f"Request Files: {kwargs.get('files')}")
            try:
                response = getattr(httpx, method)(url, **kwargs)
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                logging.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
                raise Exception(f"HTTP Error: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                logging.error(f"Other Error: {e}")
                raise Exception(f"Other Error: {e}")
            if response.status_code != 429 or retry_count >= max_retries:
                break
            # Calculate wait time with exponential backoff and jitter
            wait_time = min(base_wait_time * (2 ** retry_count) + random.uniform(0, 1), max_wait_time)
            logging.warning(f"Rate limit exceeded. Retrying in {wait_time:.2f} seconds... (Attempt {retry_count + 1}/{max_retries})")
            time.sleep(wait_time)
            retry_count += 1
        
        response.raise_for_status()
        return response
        
    """
    Upload a document to the Foxit Cloud API.
    Return the document ID. if success. Other Raise an exception.
    """
    def upload_document(self, file_path:str) -> str:
        logging.info(f"Uploading document: {file_path}")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        url = f"{self.host}/documents/upload"
        headers = {
            "client_id": f"{self.client_id}",
            "client_secret":f"{self.client_secret}"
        }
        with open(file_path, "rb") as file: 
            files = {"file": file}
            try:
                response = self._make_request_with_retry("post", url, headers=headers, files=files)
            except httpx.HTTPStatusError as e:
                logging.error(f"Upload failed with HTTP error: {e.response.status_code} - {e.response.text}")
                raise Exception(f"Upload failed with HTTP error: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                logging.error(f"Upload failed with other error: {e}")
                raise Exception(f"Upload failed with other error: {e}")
            data = response.json()
            document_id = data.get("documentId")
            if not document_id:
                code = data.get("code")
                message = data.get("message")
                raise Exception(f"Upload failed: {code} - {message}")
            return document_id
        
    """
    Download the document from the Foxit Cloud API.
    return the file path if success. Other Raise an exception.
    """
    def download_document(self,document_id, file_name:str) -> bytes:
        logging.info(f"Starting Downloading document: {document_id} to {file_name}")
        headers = {
            "Accept": "*/*",
            "client_id": f"{self.client_id}",
            "client_secret":f"{self.client_secret}"
        }
        if file_name is None or file_name == "":
            url = f"{self.host}/documents/{document_id}/download"
        else:
            url = f"{self.host}/documents/{document_id}/download?filename={file_name}"
        try:
            response = self._make_request_with_retry("get", url, headers=headers)
        except httpx.HTTPStatusError as e:
            logging.error(f"Download failed with HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Download failed with HTTP error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logging.error(f"Download failed with other error: {e}")
            raise Exception(f"Download failed with other error: {e}")
        
        # Check if the response's Content-Type is application/json, if so it indicates an error, otherwise it's a downloadable file
        content_type = response.headers.get("Content-Type")
        if content_type == "application/json":
            data = response.json()
            code = data.get("code")
            message = data.get("message")
            raise Exception(f"Download failed: {code} - {message}")
        
        return response.content
    
    """
    Get the current status of an asynchronous operation. 
    The response includes:
    Task state (PENDING, PROCESSING, COMPLETED, FAILED)
    Progress percentage (0-100)
    Result document ID (when completed successfully)
    Error details (if failed)
    reponse:{
        "taskId": "<string>",
        "status": "<string>",
        "progress": "<integer>",
        "resultDocumentId": "<string>",
        "error": {
            "code": "<string>",
            "message": "<string>"
        }
    }
    """
    def get_task_status(self, task_id:str) -> dict[str, Any]:
        url = f"{self.host}/tasks/{task_id}"
        headers = {
            "client_id": f"{self.client_id}",
            "client_secret":f"{self.client_secret}"
        }
        try:
            response = self._make_request_with_retry("get", url, headers=headers)
        except httpx.HTTPStatusError as e:
            logging.error(f"Failed to get task status with HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Failed to get task status with HTTP error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logging.error(f"Failed to get task status with other error: {e}")
            raise Exception(f"Failed to get task status with other error: {e}")
        return response.json()
    
    @staticmethod
    def get_file_format(file_path:str) -> str:
        """
        Get the file format from the file path.
        """
        original_format = None
        file_format = os.path.splitext(file_path)[1][1:].lower()
        if file_format in ["docx","doc"]:
            original_format = "word"
        elif file_format in ["pptx","ppt"]:
            original_format = "ppt"
        elif file_format in ["xlsx","xls"]:
            original_format = "excel"
        elif file_format in ["jpg","jpeg","png","bmp","gif","zip"]:
            original_format = "image"
        elif file_format in ["text","txt"]:
            original_format = "text"
        elif file_format in ["html","htm"]:
            original_format = "html"
        return original_format
    
    def wait_task_and_download_result(self, task_id, output_path: str):
        # Check task status
        status = "PENDING"
        while True:
            status = self.get_task_status(task_id)
            if status["status"] == "COMPLETED":
                result_document_id = status["resultDocumentId"]
                break
            elif status["status"] == "FAILED":
                logging.error(f"Task failed with error: {status['error']['message']}")
                raise Exception(f"Task failed: {status['error']['message']}")
            else:
                # Wait for a while before checking the task status again
                time.sleep(5)
        logging.info(f"Task completed successfully. Result document ID: {result_document_id}.")
        logging.info(f"Downloading result document to: {output_path}")
        document_data = self.download_document(result_document_id, None)
        if document_data:
            with open(output_path, "wb") as file:
                file.write(document_data)
        else:
            raise ValueError("Failed to download document or document is empty.")




