from mcp.server.fastmcp import FastMCP
from tools.convert import convert_file, convert_url
from tools.creation import create_file
from tools.combine import combine
from tools.compare import compare
from tools.compress import compress
from tools.extract import extract
from tools.flatten import flatten
from tools.linearize import linearize
from tools.split import split
from tools.manipulate import manipulate
from tools.protect import protect, remove_password
import uvicorn
import asyncio



# Define MCP tools outside the start_mcp_server function
async def convert_pdf_to_file(file_path: str, output_path: str, config: str = None) -> str:
    """
    Convert a PDF file to various formats such as text, images, Word, Excel, HTML, or PowerPoint.

    Supported output formats:
    - Plain Text (.txt): Extracts text content.
    - Images (JPG): Renders pages as images.
    - Microsoft Word (.docx).
    - Microsoft Excel (.xlsx).
    - HTML.
    - PowerPoint (.pptx).

    Args:
        file_path (str): Path to the input PDF file, e.g., '/path/to/document.pdf'.
        output_path (str): Path to save the converted file, e.g., '/path/to/output.docx'.
        config (str): Optional configuration for the conversion,it must be a JSON string with the following optional parameters:
            - password (str): Optical,Password for the PDF if it is protected.
            - pageRange (str): Optical,Specifies pages to process (only for TXT, JPG):
                * Individual pages: "1,3,5".
                * Page ranges: "1-5".
                * Mixed formats: "1,3,5-10".
                * Special values: "all" (entire document), "even" (even-numbered pages), "odd" (odd-numbered pages).
                * If pageRange is not specified, all pages are processed.
                * Pages are 1-based indexed.
            
    Example:to convert pages 1, 3, and 5-10 of a PDF to Image:
        convert_pdf_to_file('/document.pdf', '/output.jpg', config={"password": "your_password", "pageRange": "1,3,5-10"})

    Returns:
        str: Success message (e.g., 'Conversion successful...') or an error message.

    Limitations:
        - File size should not exceed 100MB.
        - The output format must be one of the supported formats.
        - If you want to convert pdf to image format, the output file should be a zip file, e.g., '/output.zip'.
    """
    try:
        create_file(file_path, output_path, config)
        return f"PDF created successfully and saved to {output_path}"
    except Exception as e:
        return str(f"Failed.Encounter error: {e}")

async def convert_file_to_pdf(file_path: str, output_path: str) -> str:
        """
        Convert files from various formats (e.g., docx, doc, pptx, ppt, xlsx, xls, txt, jpg, jpeg, png, bmp, gif) to PDF format using the Foxit Cloud API.
        The input is a file path in a supported format, and the output is a PDF file saved at the specified path.

        Args:
            file_path (str): Path to the input file to be converted, e.g., '/path/to/document.docx'.
            output_path (str): Path to save the converted PDF file, e.g., '/path/to/output.pdf'.

        Returns:
            str: A success message (e.g., 'File converted successfully...') or an error message.

        Example:
            convert_file_to_pdf('/document.docx', '/output.pdf')  # Converts a docx file to PDF

        Limitations:
            - File size should not exceed 100MB.
        """
        try:
            convert_file(file_path, output_path)
            return f"File converted successfully and saved to {output_path}"
        except Exception as e:
            return str(f"Failed.Encounter error: {e}")

async def convert_url_to_pdf(url: str, output_path: str) -> str:
        """
        Convert a web page from a given URL to a PDF file using the Foxit Cloud API.
        The input is a URL, and the output is a PDF file saved at the specified path.

        Args:
            url (str): The URL of the web page to convert, e.g., 'https://example.com'.
            output_path (str): Path to save the converted PDF file, e.g., '/path/to/output.pdf'.

        Returns:
            str: A success message (e.g., 'URL converted successfully...') or an error message.

        Example:
            convert_url_to_pdf('https://example.com', '/output.pdf')  # Converts the web page to PDF

        """
        try:
            convert_url(url, output_path)
            return f"URL converted successfully and saved to {output_path}"
        except Exception as e:
            return str(f"Failed.Encounter error: {e}")

async def combine_pdfs(input_files: list, output_file: str, config=None) -> str:
        """
        Combine multiple PDF files into a single PDF file using the Foxit Cloud API.
        This tool allows merging an array of PDF files in a specified order to create one consolidated document.
        - Merge multiple PDF files into a single document.
        - Maintain bookmarks and other document properties.

        Args:
            input_files (list): List of input PDF file paths, e.g., ['/file1.pdf', '/file2.pdf'].
            output_file (str): Path to save the combined PDF file, e.g., '/path/to/combined.pdf'.
            config (dict, optional): Configuration for the merge operation. it must be a JSON string with the following optional parameters:
                1. Bookmark Management:
                    - addBookmark (bool): Controls preservation of bookmarks from source documents.
                2. Error Handling:
                    - continueMergeOnError (bool): Determines behavior when merge errors occur.
                3. Page Numbering:
                    - retainPageNumbers (bool): Controls preservation of logical page numbers.
                4. Table of Contents (TOC):
                    - addTOC (bool): Controls automatic TOC generation.
                    - tocBookmarkLevels (str): Specifies which bookmark hierarchy levels to include in the TOC.
                        * Format: Comma-separated list of levels or ranges (e.g., "1,3,5-7").
                        * Default: "1-5" (includes levels 1 through 5).
                    - tocTitle (str): Customizes the TOC page title.

                Example:
                    {
                        "addBookmark": true,
                        "continueMergeOnError": true,
                        "retainPageNumbers": false,
                        "addTOC": true,
                        "tocBookmarkLevels": "1,2-4",
                        "tocTitle": "Document Contents"
                    }

        Returns:
            str: A success message (e.g., 'PDFs combined successfully...') or an error message.

        Example:
            combine_pdfs(['/file1.pdf', '/file2.pdf'], '/combined.pdf', config={"addBookmark": true})

        Limitations:
            - It is recommended to combine no more than 100 files at a time to avoid performance issues.
            - File size should not exceed 100MB to prevent processing failures.
        """
        try:
            combine(input_files, output_file, config)
            return f"PDFs combined successfully and saved to {output_file}"
        except Exception as e:
            return str(f"Failed.Encounter error: {e}")

async def compare_pdfs(pdf1: str, pdf2: str, output_file: str, config=None) -> str:
        """
        Compare two PDF files and save the comparison result using the Foxit Cloud API.
        This tool generates a report or visual difference document highlighting the differences between two PDFs.

        Args:
            pdf1 (str): Path to the first PDF file, e.g., '/path/to/file1.pdf'.
            pdf2 (str): Path to the second PDF file, e.g., '/path/to/file2.pdf'.
            output_file (str): Path to save the comparison result, e.g., '/path/to/diff.pdf' or '/path/to/diff.json'.
            config (dict, optional): Comparison configuration.it must be a JSON string with the following optional parameters:
                - compareType (str): Type of comparison. Options:
                    * "ALL" (default): Compare all content.
                    * "TEXT": Compare text content only.
                    * "ANNOTATION": Compare annotations only.
                    * "TEXT_AND_ANNOTATION": Compare text and annotations.
                - resultType (str): Result format. Options:
                    * "JSON": Machine-readable difference report.
                    * "PDF" (default): Visual difference document.

        Returns:
            str: A success message (e.g., 'PDFs compared successfully...') or an error message.

        Example:
            compare_pdfs('/file1.pdf', '/file2.pdf', '/diff.pdf', config={"compareType": "TEXT", "resultType": "PDF"})

        Limitations:
            - File size should not exceed 100MB. 
        """
        try:
            compare(pdf1, pdf2, output_file, config)
            return f"PDFs compared successfully and saved to {output_file}"
        except Exception as e:
            return str(f"Failed.Encounter error: {e}")

async def compress_pdf(input_file: str, output_file: str, compression_level: str) -> str:
        """
        Compress a PDF file to reduce its size using the Foxit Cloud API.
        The compression level determines the trade-off between file size and quality.

        Args:
            input_file (str): Path to the input PDF file, e.g., '/path/to/input.pdf'.
            output_file (str): Path to save the compressed PDF file, e.g., '/path/to/output.pdf'.
            compression_level (str): Compression level. Options:
                * 'HIGH': High compression (smallest size, potential quality loss).
                * 'MEDIUM': Medium compression (balanced size and quality).
                * 'LOW': Low compression (larger size, better quality).

        Returns:
            str: A success message (e.g., 'PDF compressed successfully...') or an error message.

        Example:
            compress_pdf('/input.pdf', '/output.pdf', 'HIGH')  # Compress PDF with high compression

        Limitations:
            - File size should not exceed 100MB.
        """
        try:
            compress(input_file, output_file, compression_level)
            return f"PDF compressed successfully and saved to {output_file}"
        except Exception as e:
            return str(f"Failed.Encounter error: {e}")

async def extract_pdf(input_file: str, output_dir: str, password:str = "",extract_type: str = "TEXT", page_range: str = "all") -> str:
        """
        Extract content (text, images) from a PDF file using the Foxit Cloud API.
        The extracted content is saved in the specified output directory.
        Note: 
        Args:
            input_file (str): Path to the input PDF file, e.g., '/path/to/input.pdf'.
            output_dir (str): Directory or full path to save the split PDF files.
                - If a directory is provided (e.g., '/path/to/output/'), the split files will be saved in that directory.
                - If a full path with a filename is provided (e.g., '/path/to/output.zip'), the split files will be saved as a single ZIP file with the specified name.
                - Note: If a full path is provided, the file extension must be `.zip`.
            password (str, optional): Password for the PDF if it is protected. If the PDF is not password-protected, this can be left empty.
            extract_type (str, optional): Type of content to extract. Options:
                * 'TEXT' (default): Extract text content without preserving the original layout or formatting.
                * 'IMAGE': Extract images as separate files without preserving their position or size in the PDF.
                * 'PAGE': Extract specified pages as separate PDF files, but without preserving the original document's interactive elements or formatting.
            page_range (str, optional): Page range to extract, e.g., '1-5', 'all' (default).

        Returns:
            str: A success message (e.g., 'PDF content extracted successfully...') or an error message.

        Example:
            extract_pdf('/input.pdf', '/output/', extract_type='TEXT', page_range='1-3')  # Extract text from pages 1 to 3

        Limitations:
            - File size should not exceed 100MB.
        """
        try:
            extract(input_file, output_dir, password,extract_type, page_range)
            return f"PDF content extracted successfully and saved to {output_dir}"
        except Exception as e:
            return str(f"Failed.Encounter error: {e}")

async def flatten_pdf(input_file: str, output_file: str,password:str = "") -> str:
        """
        Flatten a PDF file to remove interactive elements (e.g., forms, annotations) using the Foxit Cloud API.
        The output is a static PDF with all interactive elements rendered as part of the content.

        Args:
            input_file (str): Path to the input PDF file, e.g., '/path/to/input.pdf'.
            output_file (str): Path to save the flattened PDF file, e.g., '/path/to/output.pdf'.
            password (str): Optical. Password for the PDF file if it is encrypted. If the PDF is not password-protected, this can be left empty.

        Returns:
            str: A success message (e.g., 'PDF flattened successfully...') or an error message.

        Example:
            flatten_pdf('/input.pdf', '/output.pdf')  # Flatten the PDF to remove interactive elements

        Limitations:
            - File size should not exceed 100MB.
            - Flattening may alter the appearance of some elements, such as form fields.
        """
        try:
            flatten(input_file, output_file,password)
            return f"PDF flattened successfully and saved to {output_file}"
        except Exception as e:
            return str(f"Failed.Encounter error: {e}")

async def linearize_pdf(input_file: str, output_file: str) -> str:
        """
        Linearize a PDF file for fast web viewing using the Foxit Cloud API.
        Linearization optimizes the PDF for progressive loading, making it suitable for online viewing.

        Args:
            input_file (str): Path to the input PDF file, e.g., '/path/to/input.pdf'.
            output_file (str): Path to save the linearized PDF file, e.g., '/path/to/output.pdf'.

        Returns:
            str: A success message (e.g., 'PDF linearized successfully...') or an error message.

        Example:
            linearize_pdf('/input.pdf', '/output.pdf')  # Linearize the PDF for fast web viewing

        Limitations:
            - File size should not exceed 100MB.
            - Linearization may not significantly improve performance for small PDFs.
        """
        try:
            linearize(input_file, output_file)
            return f"PDF linearized successfully and saved to {output_file}"
        except Exception as e:
            return str(f"Failed.Encounter error: {e}")

async def remove_pdf_password(input_file: str, output_file: str, password: str) -> str:
        """
        Remove password protection from a PDF file using the Foxit Cloud API.
        This requires the owner password to unlock and remove the protection.

        Args:
            input_file (str): Path to the input PDF file, e.g., '/path/to/input.pdf'.
            output_file (str): Path to save the unprotected PDF file, e.g., '/path/to/output.pdf'.
            password (str): The owner password required to unlock the PDF file, It must be provide PDF owner passward.

        Returns:
            str: A success message (e.g., 'Password removed successfully...') or an error message.

        Example:
            remove_pdf_password('/input.pdf', '/output.pdf', 'owner_password')  # Remove password protection

        Limitations:
            - File size should not exceed 100MB.
            - This tool only removes password protection; it does not decrypt the content if the user password is required for viewing.
        """
        try:
            remove_password(input_file, output_file, password)
            return f"Password removed successfully and saved to {output_file}"
        except Exception as e:
            return str(f"Failed.Encounter error: {e}")

async def protect_pdf(input_file: str, output_file: str, password: str, owner_password: str, userPermissions: list = None, cipher: str = None, encryptMetadata: str = None) -> str:
        """
        Protect a PDF file with password encryption using the Foxit Cloud API.
        This tool applies password protection to secure the PDF, requiring a user password to open and an owner password to change security settings.

        Args:
            input_file (str): Path to the input PDF file, e.g., '/path/to/input.pdf'.
            output_file (str): Path to save the protected PDF file, e.g., '/path/to/output.pdf'.
            password (str): User password required to open the PDF file.
            owner_password (str): Owner password required to change security settings.
            userPermissions (list, optional): List of allowed operations for users, e.g., ['PRINT_NORMAL_QUALITY','EDIT_CONTENT'].
                Available Permissions:
                    - PRINT_NORMAL_QUALITY: Basic printing capabilities.
                    - PRINT_HIGH_QUALITY: High-resolution printing.
                    - EDIT_CONTENT: Modify document content.
                    - EDIT_FILL_AND_SIGN_FORM_FIELDS: Fill form fields and sign.
                    - EDIT_ANNOTATION: Add/modify annotations.
                    - EDIT_DOCUMENT_ASSEMBLY: Insert/delete/rotate pages.
                    - COPY_CONTENT: Copy text and graphics.
            cipher (str, optional): Encryption algorithm. Options: 'RC4', 'AES', 'AES_256' (default).
            encryptMetadata (str, optional): Whether to encrypt document metadata. Options: 'true', 'false' (default).

        Returns:
            str: A success message (e.g., 'PDF protected successfully...') or an error message.

        Example:
            protect_pdf('/input.pdf', '/output.pdf', 'user_pass', 'owner_pass', userPermissions=['PRINT_NORMAL_QUALITY','EDIT_CONTENT'], cipher='AES_256', encryptMetadata='true')

        Limitations:
            - File size should not exceed 100MB.
        """
        try:
            protect(input_file, output_file, password, owner_password, userPermissions, cipher, encryptMetadata)
            return f"PDF protected successfully and saved to {output_file}"
        except Exception as e:
            return str(f"Failed.Encounter error: {e}")

async def split_pdf(input_file: str, output_dir: str, split_by_pages: int) -> str:
        """
        Split a PDF file into multiple files based on the specified number of pages per file using the Foxit Cloud API.
        Each split file will contain the specified number of pages from the original PDF.

        Args:
            input_file (str): Path to the input PDF file, e.g., '/path/to/input.pdf'.
            output_dir (str): Directory or full path to save the split PDF files.
                - If a directory is provided (e.g., '/path/to/output/'), the split files will be saved in that directory.
                - If a full path with a filename is provided (e.g., '/path/to/output.zip'), the split files will be saved as a single ZIP file with the specified name.
                - Note: If a full path is provided, the file extension must be `.zip`.
            split_by_pages (int): Number of pages per split file, e.g., 2.

        Returns:
            str: A success message (e.g., 'PDF split successfully...') or an error message.

        Example:
            split_pdf('/input.pdf', '/output/', 2)  # Split the PDF into files with 2 pages each

        Limitations:
            - File size should not exceed 100MB.
        """
        try:
            split(input_file, output_dir, split_by_pages)
            return f"PDF split successfully and saved to {output_dir}"
        except Exception as e:
            return str(f"Failed.Encounter error: {e}")

async def manipulate_pdf(input_file: str, output_file: str, operations: list) -> str:
        """
        Perform various manipulations on a PDF file, such as moving, deleting, adding, or rotating pages, using the Foxit Cloud API.
        The operations are applied sequentially, and the output is a modified PDF saved at the specified path.

        Args:
            input_file (str): Path to the input PDF file, e.g., '/path/to/input.pdf'.
            output_file (str): Path to save the manipulated PDF file, e.g., '/path/to/output.pdf'.
            operations (list): List of operations to perform,it must be a JSON string. 
                Each operation is a dictionary with:
                - type (str): Operation type. Options:
                    * 'MOVE_PAGES'
                    * 'DELETE_PAGES'
                    * 'ADD_PAGES'
                    * 'ROTATE_PAGES'
                - pages (list, optional): Page numbers for the operation, e.g., [1, 2, 3]. 
                        Note:The pages parameter requires an array of integers. It does not support "all", "odd", "even", or mixed formats.
                - targetPosition (int, optional): Target position for moving pages.
                - pageCount (int, optional): Number of blank pages to add.
                - rotation (str, optional): Rotation angle for pages. Options:
                    * 'ROTATE_0'
                    * 'ROTATE_CLOCKWISE_90'
                    * 'ROTATE_180'
                    * 'ROTATE_COUNTERCLOCKWISE_90'

        Returns:
            str: A success message (e.g., 'PDF manipulated successfully...') or an error message.

        Example:
            operations = [
                {"type": "MOVE_PAGES", "pages": [1, 2, 3], "targetPosition": 5},
                {"type": "DELETE_PAGES", "pages": [4, 5]},
                {"type": "ADD_PAGES", "pageCount": 2},
                {"type": "ROTATE_PAGES", "pages": [1, 2], "rotation": "ROTATE_CLOCKWISE_90"}
            ]
            manipulate_pdf('/input.pdf', '/output.pdf', operations)

        Limitations:
            - File size should not exceed 100MB.
        """
        try:
            manipulate(input_file, output_file, operations)
            return f"PDF manipulated successfully and saved to {output_file}"
        except Exception as e:
            return str(f"Failed.Encounter error: {e}")

# Optimize start_mcp_server function

def start_mcp_server(transport='stdio'):
    if transport == "stdio":
        mcp = FastMCP("foxit_cloud_api")
    else:
        mcp = FastMCP(
            "foxit_cloud_api",
            streamable_http_path="/mcp",
            host="127.0.0.1",
            port=8080,
            debug=True
        )

    # Register tools dynamically
    mcp.tool()(convert_pdf_to_file)
    mcp.tool()(convert_file_to_pdf)
    mcp.tool()(convert_url_to_pdf)
    mcp.tool()(combine_pdfs)
    mcp.tool()(compare_pdfs)
    mcp.tool()(compress_pdf)
    mcp.tool()(extract_pdf)
    mcp.tool()(flatten_pdf)
    mcp.tool()(linearize_pdf)
    mcp.tool()(remove_pdf_password)
    mcp.tool()(protect_pdf)
    mcp.tool()(split_pdf)
    mcp.tool()(manipulate_pdf)

    print(f"MCP server started with transport: {transport}.")
    mcp.run(transport=transport)