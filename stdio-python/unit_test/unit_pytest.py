import asyncio
import os
import sys
import openpyxl
from openpyxl.styles import Font
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.mcp_server import (
    combine_pdfs,
    split_pdf,
    linearize_pdf,
    flatten_pdf,
    manipulate_pdf,
    compress_pdf,
    protect_pdf,
    remove_pdf_password,
    extract_pdf,
    convert_pdf_to_file,
    convert_file_to_pdf,
    convert_url_to_pdf,
    compare_pdfs,
)

os.environ["FOXIT_CLOUD_API_HOST"] = "https://na1.fusion.foxit.com/pdf-services/api"
os.environ["FOXIT_CLOUD_API_CLIENT_ID"] = "foxit_SKgZaSJPdc0ZyF1B"
os.environ["FOXIT_CLOUD_API_CLIENT_SECRET"] = "qU29BGcX9C139_F8ujg3x4iFtqP-YAcW"

# os.environ["FOXIT_CLOUD_API_HOST"] = "https://na1-qa.fusion.foxit.com/pdf-services/api"
# os.environ["FOXIT_CLOUD_API_CLIENT_ID"] = "97dfc9a70e32441e86d4690c18f9f29b"
# os.environ["FOXIT_CLOUD_API_CLIENT_SECRET"] = "c3eB7F8E3384439881ec3Ee79f8540dD"

# Initialize Excel workbook and sheet
excel_file = "./unit_test/output/test_results.xlsx"
workbook = openpyxl.Workbook()
sheet = workbook.active
sheet.title = "Test Results"
sheet.append(["Timestamp", "Test Name", "Message", "Status"])  # Add headers
header_font = Font(bold=True)
for cell in sheet[1]:
    cell.font = header_font

def save_to_excel(test_name, message, status):
    """Log test results into an Excel file."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append([timestamp, test_name, message, status])
    workbook.save(excel_file)

def print_colored(message, color, test_name=None, status=None):
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "reset": "\033[0m"
    }
    print(f"{colors.get(color, colors['reset'])}{message}{colors['reset']}")

    # Log to Excel if test_name and status are provided
    if test_name and status:
        save_to_excel(test_name, message, status)



# def print_colored(message, color):
#     colors = {
#         "red": "\033[91m",
#         "green": "\033[92m",
#         "yellow": "\033[93m",
#         "blue": "\033[94m",
#         "reset": "\033[0m"
#     }
#     print(f"{colors.get(color, colors['reset'])}{message}{colors['reset']}")


def clear_output_directory():
    output_dir = "./unit_test/output/"
    for file in os.listdir(output_dir):
        file_path = os.path.join(output_dir, file)
        if os.path.isfile(file_path):
            os.remove(file_path)


# UnitTest for the Foxit Cloud API functions
async def test_combine_pdfs():
    try:
        result = await combine_pdfs([
            "./unit_test/input/OnlyImage.pdf",
            "./unit_test/input/images_file.pdf",
        ], "./unit_test/output/combined.pdf")
        if "Failed" in result:
            print_colored(f"combine_pdfs failed: {result}", "red", test_name="test_combine_pdfs", status="Failed")
        else:
            print_colored("combine_pdfs passed", "green", test_name="test_combine_pdfs", status="Pass")
    except Exception as e:
        print_colored(f"combine_pdfs failed: {e}", "red", test_name="test_combine_pdfs", status="Failed")

async def test_combine_pdfs_with_bookmarks():
    try:
        result = await combine_pdfs([
            "./unit_test/input/new.pdf",
            "./unit_test/input/old.pdf",
        ], "./unit_test/output/combined_with_bookmarks.pdf", config={"addBookmark": True})
        if "Failed" in result:
            print_colored(f"test_combine_pdfs_with_bookmarks failed: {result}", "red", test_name="test_combine_pdfs_with_bookmarks", status="Failed")
        else:
            print_colored("test_combine_pdfs_with_bookmarks passed", "green", test_name="test_combine_pdfs_with_bookmarks", status="Pass")
    except Exception as e:
        print_colored(f"test_combine_pdfs_with_bookmarks failed: {e}", "red", test_name="test_combine_pdfs_with_bookmarks", status="Failed")

async def check_file_exists(file_path):
    if os.path.exists(file_path):
        print(f"File {file_path} exists.")
    else:
        raise FileNotFoundError(f"File {file_path} does not exist.")

async def test_combine_pdfs_with_toc():
    try:
        result = await combine_pdfs([
            "./unit_test/input/new.pdf",
            "./unit_test/input/old.pdf",
        ], "./unit_test/output/combined_with_toc.pdf", config={"addTOC": True})
        if "Failed" in result:
            print_colored(f"test_combine_pdfs_with_toc failed: {result}", "red", test_name="test_combine_pdfs_with_toc", status="Failed")
        else:
            print_colored("test_combine_pdfs_with_toc passed", "green", test_name="test_combine_pdfs_with_toc", status="Pass")
    except Exception as e:
        print_colored(f"test_combine_pdfs_with_toc failed: {e}", "red", test_name="test_combine_pdfs_with_toc", status="Failed")

async def test_combine_pdfs_with_custom_toc():
    try:
        result = await combine_pdfs([
            "./unit_test/input/new.pdf",
            "./unit_test/input/old.pdf",
        ], "./unit_test/output/combined_with_custom_toc.pdf", config={"addTOC": True, "tocBookmarkLevels": "1-3", "tocTitle": "Custom TOC"})
        if "Failed" in result:
            print_colored(f"test_combine_pdfs_with_custom_toc failed: {result}", "red", test_name="test_combine_pdfs_with_custom_toc", status="Failed")
        else:
            print_colored("test_combine_pdfs_with_custom_toc passed", "green", test_name="test_combine_pdfs_with_custom_toc", status="Pass")
    except Exception as e:
        print_colored(f"test_combine_pdfs_with_custom_toc failed: {e}", "red", test_name="test_combine_pdfs_with_custom_toc", status="Failed")

async def test_combine_pdfs_with_invalid_path():
    try:
        result = await combine_pdfs([
            "./unit_test/input/nonexistent.pdf",
            "./unit_test/input/old.pdf",
        ], "./unit_test/output/combined_invalid_path.pdf")
        if "Failed" in result:
            print_colored(f"test_combine_pdfs_with_invalid_path failed: {result}", "red", test_name="test_combine_pdfs_with_invalid_path", status="Failed")
        else:
            print_colored("test_combine_pdfs_with_invalid_path passed", "green", test_name="test_combine_pdfs_with_invalid_path", status="Pass")
    except Exception as e:
        print_colored(f"test_combine_pdfs_with_invalid_path failed: {e}", "red", test_name="test_combine_pdfs_with_invalid_path", status="Failed")

async def test_split_pdf():
    try:
        result = await split_pdf("./unit_test/input/whitebook.pdf", "./unit_test/output/result.zip", 5)
        if "Failed" in result:
            print_colored(f"split_pdf failed: {result}", "red", test_name="test_split_pdf", status="Failed")
        else:
            print_colored("split_pdf passed", "green", test_name="test_split_pdf", status="Pass")
    except Exception as e:
        print_colored(f"split_pdf failed: {e}", "red", test_name="test_split_pdf", status="Failed")

async def test_split_pdf_with_two_pages():
    try:
        result = await split_pdf("./unit_test/input/whitebook.pdf", "./unit_test/output/result_with_2_page.zip", 2)
        if "Failed" in result:
            print_colored(f"test_split_pdf_with_two_pages failed: {result}", "red", test_name="test_split_pdf_with_two_pages", status="Failed")
        else:
            print_colored("test_split_pdf_with_two_pages passed", "green", test_name="test_split_pdf_with_two_pages", status="Pass")
    except Exception as e:
        print_colored(f"test_split_pdf_with_two_pages failed: {e}", "red", test_name="test_split_pdf_with_two_pages", status="Failed")

async def test_split_pdf_with_ten_pages():
    try:
        result = await split_pdf("./unit_test/input/whitebook.pdf", "./unit_test/output/result_with_10_pages.zip", 10)
        if "Failed" in result:
            print_colored(f"test_split_pdf_with_ten_pages failed: {result}", "red", test_name="test_split_pdf_with_ten_pages", status="Failed")
        else:
            print_colored("test_split_pdf_with_ten_pages passed", "green", test_name="test_split_pdf_with_ten_pages", status="Pass")
    except Exception as e:
        print_colored(f"test_split_pdf_with_ten_pages failed: {e}", "red", test_name="test_split_pdf_with_ten_pages", status="Failed")

async def test_split_single_page_pdf():
    try:
        result = await split_pdf("./unit_test/input/whitebook.pdf", "./unit_test/output/result_single_page.zip", 5)
        if "Failed" in result:
            print_colored(f"test_split_single_page_pdf failed: {result}", "red", test_name="test_split_single_page_pdf", status="Failed")
        else:
            print_colored("test_split_single_page_pdf passed", "green", test_name="test_split_single_page_pdf", status="Pass")
    except Exception as e:
        print_colored(f"test_split_single_page_pdf failed: {e}", "red", test_name="test_split_single_page_pdf", status="Failed")

async def test_split_pdf_with_fewer_pages_than_split_count():
    try:
        result = await split_pdf("./unit_test/input/whitebook.pdf", "./unit_test/output/result_fewer_page.zip", 10)
        if "Failed" in result:
            print_colored(f"test_split_pdf_with_fewer_pages_than_split_count failed: {result}", "red", test_name="test_split_pdf_with_fewer_pages_than_split_count", status="Failed")
        else:
            print_colored("test_split_pdf_with_fewer_pages_than_split_count passed", "green", test_name="test_split_pdf_with_fewer_pages_than_split_count", status="Pass")
    except Exception as e:
        print_colored(f"test_split_pdf_with_fewer_pages_than_split_count failed: {e}", "red", test_name="test_split_pdf_with_fewer_pages_than_split_count", status="Failed")

async def test_split_pdf_with_invalid_file():
    try:
        result = await split_pdf("./unit_test/input/nonexistent.pdf", "./unit_test/output/", 5)
        if "Failed" in result:
            print_colored(f"test_split_pdf_with_invalid_file Passed", "green", test_name="test_split_pdf_with_invalid_file", status="Pass")
        else:
            print_colored("test_split_pdf_with_invalid_file Failed", "red", test_name="test_split_pdf_with_invalid_file", status="Failed")
    except Exception as e:
        print_colored(f"test_split_pdf_with_invalid_file failed: {e}", "red", test_name="test_split_pdf_with_invalid_file", status="Failed")

async def test_linearize_pdf():
    try:
        result = await linearize_pdf("./unit_test/input/whitebook.pdf", "./unit_test/output/withebook_linearized.pdf")
        if "Failed" in result:
            print_colored(f"linearize_pdf failed: {result}", "red", test_name="test_linearize_pdf", status="Failed")
        else:
            print_colored("linearize_pdf passed", "green", test_name="test_linearize_pdf", status="Pass")
    except Exception as e:
        print_colored(f"linearize_pdf failed: {e}", "red", test_name="test_linearize_pdf", status="Failed")

async def test_linearize_pdf_with_invalid_input_file():
    """Test linearize_pdf with non-existent input file"""
    try:
        result = await linearize_pdf("./unit_test/input/nonexistent.pdf", "./unit_test/output/linearized_invalid_input.pdf")
        if "Failed" in result:
            print_colored(f"test_linearize_pdf_with_invalid_input_file passed (correctly failed):{result}", "green", test_name="test_linearize_pdf_with_invalid_input_file", status="Pass")
        else:
            print_colored(f"test_linearize_pdf_with_invalid_input_file failed (should have failed):{result}", "red", test_name="test_linearize_pdf_with_invalid_input_file", status="Failed")
    except Exception as e:
        print_colored(f"test_linearize_pdf_with_invalid_input_file passed (exception caught): {e}", "green", test_name="test_linearize_pdf_with_invalid_input_file", status="Pass")

async def test_linearize_pdf_overwrite_existing_file():
    """Test linearize_pdf by overwriting an existing output file"""
    try:
        # First create a file
        await linearize_pdf("./unit_test/input/whitebook.pdf", "./unit_test/output/overwrite_test.pdf")
        # Then overwrite it
        result = await linearize_pdf("./unit_test/input/whitebook.pdf", "./unit_test/output/overwrite_test.pdf")
        if "Failed" in result:
            print_colored(f"test_linearize_pdf_overwrite_existing_file failed: {result}", "red", test_name="test_linearize_pdf_overwrite_existing_file", status="Failed")
        else:
            print_colored("test_linearize_pdf_overwrite_existing_file passed", "green", test_name="test_linearize_pdf_overwrite_existing_file", status="Pass")
    except Exception as e:
        print_colored(f"test_linearize_pdf_overwrite_existing_file failed: {e}", "red", test_name="test_linearize_pdf_overwrite_existing_file", status="Failed")

async def test_linearize_pdf_with_invalid_output_path():
    """Test linearize_pdf with invalid output directory"""
    try:
        result = await linearize_pdf("./unit_test/input/whitebook.pdf", "./unit_test/nonexistent_dir/linearized.pdf")
        if "Failed" in result:
            print_colored(f"test_linearize_pdf_with_invalid_output_path passed (correctly failed):{result}", "green", test_name="test_linearize_pdf_with_invalid_output_path", status="Pass")
        else:
            print_colored(f"test_linearize_pdf_with_invalid_output_path failed (should have failed):{result}", "red", test_name="test_linearize_pdf_with_invalid_output_path", status="Failed")
    except Exception as e:
        print_colored(f"test_linearize_pdf_with_invalid_output_path passed (exception caught): {e}", "green", test_name="test_linearize_pdf_with_invalid_output_path", status="Pass")

async def test_linearize_pdf_with_empty_input_path():
    """Test linearize_pdf with empty input file path"""
    try:
        result = await linearize_pdf("", "./unit_test/output/linearized_empty_input.pdf")
        if "Failed" in result:
            print_colored(f"test_linearize_pdf_with_empty_input_path passed (correctly failed):{result}", "green", test_name="test_linearize_pdf_with_empty_input_path", status="Pass")
        else:
            print_colored(f"test_linearize_pdf_with_empty_input_path failed (should have failed):{result}", "red", test_name="test_linearize_pdf_with_empty_input_path", status="Failed")
    except Exception as e:
        print_colored(f"test_linearize_pdf_with_empty_input_path passed (exception caught): {e}", "green", test_name="test_linearize_pdf_with_empty_input_path", status="Pass")

async def test_flatten_pdf():
    try:
        result = await flatten_pdf("./unit_test/input/whitebook.pdf", "./unit_test/output/withebook_flatten.pdf")
        if "Failed" in result:
            print_colored(f"flatten_pdf failed: {result}", "red", test_name="test_flatten_pdf", status="Failed")
        else:
            print_colored("flatten_pdf passed", "green", test_name="test_flatten_pdf", status="Pass")
    except Exception as e:
        print_colored(f"flatten_pdf failed: {e}", "red", test_name="test_flatten_pdf", status="Failed")

async def test_flatten_pdf_with_password():
    try:
        result = await flatten_pdf("./unit_test/input/doc_password_user123_owner456.pdf", "./unit_test/output/flatten_with_password.pdf", password="user123")
        if "Failed" in result:
            print_colored(f"flatten_pdf with password failed: {result}", "red", test_name="test_flatten_pdf_with_password", status="Failed")
        else:
            print_colored("flatten_pdf with password passed", "green", test_name="test_flatten_pdf_with_password", status="Pass")
    except Exception as e:
        print_colored(f"flatten_pdf with password failed: {e}", "red", test_name="test_flatten_pdf_with_password", status="Failed")

async def test_flatten_pdf_with_invalid_input_file():
    """Test flatten_pdf with non-existent input file"""
    try:
        result = await flatten_pdf("./unit_test/input/nonexistent.pdf", "./unit_test/output/flattened_invalid_input.pdf")
        if "Failed" in result:
            print_colored("test_flatten_pdf_with_invalid_input_file passed (correctly failed)", "green", test_name="test_flatten_pdf_with_invalid_input_file", status="Pass")
        else:
            print_colored("test_flatten_pdf_with_invalid_input_file failed (should have failed)", "red", test_name="test_flatten_pdf_with_invalid_input_file", status="Failed")
    except Exception as e:
        print_colored(f"test_flatten_pdf_with_invalid_input_file passed (exception caught): {e}", "green", test_name="test_flatten_pdf_with_invalid_input_file", status="Pass")

async def test_flatten_pdf_with_invalid_output_path():
    """Test flatten_pdf with invalid output directory"""
    try:
        result = await flatten_pdf("./unit_test/input/whitebook.pdf", "./unit_test/nonexistent_dir/flattened.pdf")
        if "Failed" in result:
            print_colored("test_flatten_pdf_with_invalid_output_path passed (correctly failed)", "green", test_name="test_flatten_pdf_with_invalid_output_path", status="Pass")
        else:
            print_colored("test_flatten_pdf_with_invalid_output_path failed (should have failed)", "red", test_name="test_flatten_pdf_with_invalid_output_path", status="Failed")
    except Exception as e:
        print_colored(f"test_flatten_pdf_with_invalid_output_path passed (exception caught): {e}", "green", test_name="test_flatten_pdf_with_invalid_output_path", status="Pass")

async def test_flatten_pdf_with_empty_input_path():
    """Test flatten_pdf with empty input file path"""
    try:
        result = await flatten_pdf("", "./unit_test/output/flattened_empty_input.pdf")
        if "Failed" in result:
            print_colored("test_flatten_pdf_with_empty_input_path passed (correctly failed)", "green", test_name="test_flatten_pdf_with_empty_input_path", status="Pass")
        else:
            print_colored("test_flatten_pdf_with_empty_input_path failed (should have failed)", "red", test_name="test_flatten_pdf_with_empty_input_path", status="Failed")
    except Exception as e:
        print_colored(f"test_flatten_pdf_with_empty_input_path passed (exception caught): {e}", "green", test_name="test_flatten_pdf_with_empty_input_path", status="Pass")

async def test_flatten_pdf_with_empty_output_path():
    """Test flatten_pdf with empty output file path"""
    try:
        result = await flatten_pdf("./unit_test/input/whitebook.pdf", "")
        if "Failed" in result:
            print_colored("test_flatten_pdf_with_empty_output_path passed (correctly failed)", "green", test_name="test_flatten_pdf_with_empty_output_path", status="Pass")
        else:
            print_colored("test_flatten_pdf_with_empty_output_path failed (should have failed)", "red", test_name="test_flatten_pdf_with_empty_output_path", status="Failed")
    except Exception as e:
        print_colored(f"test_flatten_pdf_with_empty_output_path passed (exception caught): {e}", "green", test_name="test_flatten_pdf_with_empty_output_path", status="Pass")

async def test_flatten_pdf_with_non_pdf_file():
    """Test flatten_pdf with a non-PDF file"""
    try:
        result = await flatten_pdf("./unit_test/input/input_doc.docx", "./unit_test/output/flattened_non_pdf.pdf")
        if "Failed" in result:
            print_colored("test_flatten_pdf_with_non_pdf_file passed (correctly failed)", "green", test_name="test_flatten_pdf_with_non_pdf_file", status="Pass")
        else:
            print_colored("test_flatten_pdf_with_non_pdf_file failed (should have failed)", "red", test_name="test_flatten_pdf_with_non_pdf_file", status="Failed")
    except Exception as e:
        print_colored(f"test_flatten_pdf_with_non_pdf_file passed (exception caught): {e}", "green", test_name="test_flatten_pdf_with_non_pdf_file", status="Pass")

async def test_manipulate_pdf():
    try:
        result = await manipulate_pdf("./unit_test/input/whitebook.pdf", "./unit_test/output/withebook_matip.pdf", [
            {"type": "MOVE_PAGES", "pages": [1, 2, 3], "targetPosition": 5},
            {"type": "DELETE_PAGES", "pages": [4, 5]},
            {"type": "ADD_PAGES", "pageCount": 2},
            {"type": "ROTATE_PAGES", "pages": [1, 2], "rotation": "ROTATE_CLOCKWISE_90"},
        ])
        if "Failed" in result:
            print_colored(f"manipulate_pdf failed: {result}", "red", test_name="test_manipulate_pdf", status="Failed")
        else:
            print_colored("manipulate_pdf passed", "green", test_name="test_manipulate_pdf", status="Pass")
    except Exception as e:
        print_colored(f"manipulate_pdf failed: {e}", "red", test_name="test_manipulate_pdf", status="Failed")

# async def test_manipulate_pdf_all_pages():
#     try:
#         result = await manipulate_pdf("./unit_test/input/whitebook.pdf", "./unit_test/output/withebook_matip_all.pdf", [
#             {"type": "ADD_PAGES", "pageCount": 2},
#             {"type": "ROTATE_PAGES", "rotation": "ROTATE_CLOCKWISE_90"},
#         ])
#         if "Failed" in result:
#             print_colored(f"manipulate_pdf failed: {result}", "red", test_name="test_manipulate_pdf_all_pages", status="Failed")
#         else:
#             print_colored("manipulate_pdf passed", "green", test_name="test_manipulate_pdf_all_pages", status="Pass")
#     except Exception as e:
#         print_colored(f"manipulate_pdf failed: {e}", "red", test_name="test_manipulate_pdf_all_pages", status="Failed")

async def test_manipulate_pdf_with_invalid_input_file():
    """Test manipulate_pdf with non-existent input file"""
    try:
        result = await manipulate_pdf("./unit_test/input/nonexistent.pdf", "./unit_test/output/invalid_input.pdf", [
            {"type": "ADD_PAGES", "pageCount": 1}
        ])
        if "Failed" in result:
            print_colored("test_manipulate_pdf_with_invalid_input_file passed (correctly failed)", "green", test_name="test_manipulate_pdf_with_invalid_input_file", status="Pass")
        else:
            print_colored("test_manipulate_pdf_with_invalid_input_file failed (should have failed)", "red", test_name="test_manipulate_pdf_with_invalid_input_file", status="Failed")
    except Exception as e:
        print_colored(f"test_manipulate_pdf_with_invalid_input_file passed (exception caught): {e}", "green", test_name="test_manipulate_pdf_with_invalid_input_file", status="Pass")

async def test_manipulate_pdf_with_invalid_output_path():
    """Test manipulate_pdf with invalid output directory"""
    try:
        result = await manipulate_pdf("./unit_test/input/whitebook.pdf", "./unit_test/nonexistent_dir/output.pdf", [
            {"type": "ADD_PAGES", "pageCount": 1}
        ])
        if "Failed" in result:
            print_colored("test_manipulate_pdf_with_invalid_output_path passed (correctly failed)", "green", test_name="test_manipulate_pdf_with_invalid_output_path", status="Pass")
        else:
            print_colored("test_manipulate_pdf_with_invalid_output_path failed (should have failed)", "red", test_name="test_manipulate_pdf_with_invalid_output_path", status="Failed")
    except Exception as e:
        print_colored(f"test_manipulate_pdf_with_invalid_output_path passed (exception caught): {e}", "green", test_name="test_manipulate_pdf_with_invalid_output_path", status="Pass")

async def test_manipulate_pdf_with_empty_operations():
    """Test manipulate_pdf with empty operations list"""
    try:
        result = await manipulate_pdf("./unit_test/input/whitebook.pdf", "./unit_test/output/empty_ops.pdf", [])
        if "Failed" in result:
            print_colored("test_manipulate_pdf_with_empty_operations passed (correctly failed)", "green", test_name="test_manipulate_pdf_with_empty_operations", status="Pass")
        else:
            print_colored("test_manipulate_pdf_with_empty_operations failed (should have failed)", "red", test_name="test_manipulate_pdf_with_empty_operations", status="Failed")
    except Exception as e:
        print_colored(f"test_manipulate_pdf_with_empty_operations passed (exception caught): {e}", "green", test_name="test_manipulate_pdf_with_empty_operations", status="Pass")

async def test_manipulate_pdf_with_invalid_operation_type():
    """Test manipulate_pdf with invalid operation type"""
    try:
        result = await manipulate_pdf("./unit_test/input/whitebook.pdf", "./unit_test/output/invalid_op.pdf", [
            {"type": "INVALID_OPERATION", "pages": [1]}
        ])
        if "Failed" in result:
            print_colored("test_manipulate_pdf_with_invalid_operation_type passed (correctly failed)", "green", test_name="test_manipulate_pdf_with_invalid_operation_type", status="Pass")
        else:
            print_colored("test_manipulate_pdf_with_invalid_operation_type failed (should have failed)", "red", test_name="test_manipulate_pdf_with_invalid_operation_type", status="Failed")
    except Exception as e:
        print_colored(f"test_manipulate_pdf_with_invalid_operation_type passed (exception caught): {e}", "green", test_name="test_manipulate_pdf_with_invalid_operation_type", status="Pass")

async def test_compress_pdf():
    try:
        result = await compress_pdf("./unit_test/input/whitebook.pdf", "./unit_test/output/withebook_compress.pdf", "HIGH")
        if "Failed" in result:
            print_colored(f"compress_pdf failed: {result}", "red", test_name="test_compress_pdf", status="Failed")
        else:
            print_colored("compress_pdf passed", "green", test_name="test_compress_pdf", status="Pass")
    except Exception as e:
        print_colored(f"compress_pdf failed: {e}", "red", test_name="test_compress_pdf", status="Failed")

async def test_compress_pdf_high_level():
    """Test compress_pdf with HIGH compression level"""
    try:
        result = await compress_pdf("./unit_test/input/whitebook.pdf", "./unit_test/output/compress_high.pdf", "HIGH")
        if "Failed" in result:
            print_colored(f"test_compress_pdf_high_level failed: {result}", "red", test_name="test_compress_pdf_high_level", status="Failed")
        else:
            print_colored("test_compress_pdf_high_level passed", "green", test_name="test_compress_pdf_high_level", status="Pass")
    except Exception as e:
        print_colored(f"test_compress_pdf_high_level failed: {e}", "red", test_name="test_compress_pdf_high_level", status="Failed")

async def test_compress_pdf_medium_level():
    """Test compress_pdf with MEDIUM compression level"""
    try:
        result = await compress_pdf("./unit_test/input/whitebook.pdf", "./unit_test/output/compress_medium.pdf", "MEDIUM")
        if "Failed" in result:
            print_colored(f"test_compress_pdf_medium_level failed: {result}", "red", test_name="test_compress_pdf_medium_level", status="Failed")
        else:
            print_colored("test_compress_pdf_medium_level passed", "green", test_name="test_compress_pdf_medium_level", status="Pass")
    except Exception as e:
        print_colored(f"test_compress_pdf_medium_level failed: {e}", "red", test_name="test_compress_pdf_medium_level", status="Failed")

async def test_compress_pdf_low_level():
    """Test compress_pdf with LOW compression level"""
    try:
        result = await compress_pdf("./unit_test/input/whitebook.pdf", "./unit_test/output/compress_low.pdf", "LOW")
        if "Failed" in result:
            print_colored(f"test_compress_pdf_low_level failed: {result}", "red", test_name="test_compress_pdf_low_level", status="Failed")
        else:
            print_colored("test_compress_pdf_low_level passed", "green", test_name="test_compress_pdf_low_level", status="Pass")
    except Exception as e:
        print_colored(f"test_compress_pdf_low_level failed: {e}", "red", test_name="test_compress_pdf_low_level", status="Failed")

async def test_compress_pdf_with_invalid_input_file():
    """Test compress_pdf with non-existent input file"""
    try:
        result = await compress_pdf("./unit_test/input/nonexistent.pdf", "./unit_test/output/compress_invalid_input.pdf", "HIGH")
        if "Failed" in result:
            print_colored(f"test_compress_pdf_with_invalid_input_file passed (correctly failed): {result}", "green", test_name="test_compress_pdf_with_invalid_input_file", status="Pass")
        else:
            print_colored("test_compress_pdf_with_invalid_input_file failed (should have failed)", "red", test_name="test_compress_pdf_with_invalid_input_file", status="Failed")
    except Exception as e:
        print_colored(f"test_compress_pdf_with_invalid_input_file passed (exception caught): {e}", "green", test_name="test_compress_pdf_with_invalid_input_file", status="Pass")

async def test_compress_pdf_with_invalid_output_path():
    """Test compress_pdf with invalid output directory"""
    try:
        result = await compress_pdf("./unit_test/input/whitebook.pdf", "./unit_test/nonexistent_dir/compress.pdf", "HIGH")
        if "Failed" in result:
            print_colored(f"test_compress_pdf_with_invalid_output_path passed (correctly failed): {result}", "green", test_name="test_compress_pdf_with_invalid_output_path", status="Pass")
        else:
            print_colored("test_compress_pdf_with_invalid_output_path failed (should have failed)", "red", test_name="test_compress_pdf_with_invalid_output_path", status="Failed")
    except Exception as e:
        print_colored(f"test_compress_pdf_with_invalid_output_path passed (exception caught): {e}", "green", test_name="test_compress_pdf_with_invalid_output_path", status="Pass")

async def test_compress_pdf_with_invalid_compression_level():
    """Test compress_pdf with invalid compression level"""
    try:
        result = await compress_pdf("./unit_test/input/whitebook.pdf", "./unit_test/output/compress_invalid_level.pdf", "INVALID")
        if "Failed" in result:
            print_colored(f"test_compress_pdf_with_invalid_compression_level passed (correctly failed): {result}", "green", test_name="test_compress_pdf_with_invalid_compression_level", status="Pass")
        else:
            print_colored("test_compress_pdf_with_invalid_compression_level failed (should have failed)", "red", test_name="test_compress_pdf_with_invalid_compression_level", status="Failed")
    except Exception as e:
        print_colored(f"test_compress_pdf_with_invalid_compression_level passed (exception caught): {e}", "green", test_name="test_compress_pdf_with_invalid_compression_level", status="Pass")

async def test_compress_pdf_with_empty_input_path():
    """Test compress_pdf with empty input file path"""
    try:
        result = await compress_pdf("", "./unit_test/output/compress_empty_input.pdf", "HIGH")
        if "Failed" in result:
            print_colored(f"test_compress_pdf_with_empty_input_path passed (correctly failed): {result}", "green", test_name="test_compress_pdf_with_empty_input_path", status="Pass")
        else:
            print_colored("test_compress_pdf_with_empty_input_path failed (should have failed)", "red", test_name="test_compress_pdf_with_empty_input_path", status="Failed")
    except Exception as e:
        print_colored(f"test_compress_pdf_with_empty_input_path passed (exception caught): {e}", "green", test_name="test_compress_pdf_with_empty_input_path", status="Pass")

async def test_compress_pdf_with_empty_output_path():
    """Test compress_pdf with empty output file path"""
    try:
        result = await compress_pdf("./unit_test/input/whitebook.pdf", "", "HIGH")
        if "Failed" in result:
            print_colored(f"test_compress_pdf_with_empty_output_path passed (correctly failed): {result}", "green", test_name="test_compress_pdf_with_empty_output_path", status="Pass")
        else:
            print_colored("test_compress_pdf_with_empty_output_path failed (should have failed)", "red", test_name="test_compress_pdf_with_empty_output_path", status="Failed")
    except Exception as e:
        print_colored(f"test_compress_pdf_with_empty_output_path passed (exception caught): {e}", "green", test_name="test_compress_pdf_with_empty_output_path", status="Pass")


async def test_protect_pdf():
    """Test protect_pdf with specific user permissions"""
    try:
        result = await protect_pdf(
            "./unit_test/input/whitebook.pdf", 
            "./unit_test/output/protected_whitebook.pdf", 
            "user123", 
            "owner456",
            userPermissions=['PRINT_NORMAL_QUALITY','EDIT_CONTENT']
        )
        if "Failed" in result:
            print_colored(f"test_protect_pdf_with_user_permissions failed: {result}", "red", test_name="test_protect_pdf_with_user_permissions", status="Failed")
        else:
            print_colored("test_protect_pdf_with_user_permissions passed", "green", test_name="test_protect_pdf_with_user_permissions", status="Pass")
    except Exception as e:
        print_colored(f"test_protect_pdf_with_user_permissions failed: {e}", "red", test_name="test_protect_pdf_with_user_permissions", status="Failed")

async def test_protect_pdf_with_invaid_permissions():
    try:
        result = await protect_pdf(
        "./unit_test/input/whitebook.pdf", 
        "./unit_test/output/protected_whitebook.pdf", 
        "user123", 
        "owner456",
        userPermissions="PRINT_NORMAL_QUALITY"
    )
        if "Failed" in result:
            print_colored(f"test_protect_pdf_with_user_permissions failed: {result}", "green", test_name="test_protect_pdf_with_invaid_permissions", status="Pass")
        else:
            print_colored("test_protect_pdf_with_user_permissions passed (should fail)", "red", test_name="test_protect_pdf_with_invaid_permissions", status="Faild")
    except Exception as e:
        print_colored(f"test_protect_pdf_with_user_permissions failed: {e}", "red", test_name="test_protect_pdf_with_user_permissions", status="Failed")

async def test_protect_pdf_with_all_options():
    """Test protect_pdf with all options specified"""
    try:
        result = await protect_pdf(
            "./unit_test/input/whitebook.pdf", 
            "./unit_test/output/protected_full_options.pdf", 
            "user123", 
            "owner456",
            userPermissions=['PRINT_HIGH_QUALITY','EDIT_CONTENT','COPY_CONTENT'],
            cipher="AES_256",
            encryptMetadata="true"
        )
        if "Failed" in result:
            print_colored(f"test_protect_pdf_with_all_options failed: {result}", "red", test_name="test_protect_pdf_with_all_options", status="Failed")
        else:
            print_colored("test_protect_pdf_with_all_options passed", "green", test_name="test_protect_pdf_with_all_options", status="Pass")
    except Exception as e:
        print_colored(f"test_protect_pdf_with_all_options failed: {e}", "red", test_name="test_protect_pdf_with_all_options", status="Failed")

async def test_protect_pdf_with_same_passwords():
    """Test protect_pdf with same user and owner passwords (should fail)"""
    try:
        result = await protect_pdf(
            "./unit_test/input/whitebook.pdf", 
            "./unit_test/output/protected_same_passwords.pdf", 
            "same123", 
            "same123"
        )
        if "Failed" in result:
            print_colored(f"test_protect_pdf_with_same_passwords passed (correctly failed): {result}", "green", test_name="test_protect_pdf_with_same_passwords", status="Pass")
        else:
            print_colored("test_protect_pdf_with_same_passwords failed (should have failed)", "red", test_name="test_protect_pdf_with_same_passwords", status="Failed")
    except Exception as e:
        print_colored(f"test_protect_pdf_with_same_passwords passed (exception caught): {e}", "green", test_name="test_protect_pdf_with_same_passwords", status="Pass")


async def test_protect_pdf_with_invalid_input_file():
    """Test protect_pdf with non-existent input file"""
    try:
        result = await protect_pdf(
            "./unit_test/input/nonexistent.pdf", 
            "./unit_test/output/protected_invalid_input.pdf", 
            "user123", 
            "owner456"
        )
        if "Failed" in result:
            print_colored(f"test_protect_pdf_with_invalid_input_file passed (correctly failed): {result}", "green", test_name="test_protect_pdf_with_invalid_input_file", status="Pass")
        else:
            print_colored("test_protect_pdf_with_invalid_input_file failed (should have failed)", "red", test_name="test_protect_pdf_with_invalid_input_file", status="Failed")
    except Exception as e:
        print_colored(f"test_protect_pdf_with_invalid_input_file passed (exception caught): {e}", "green", test_name="test_protect_pdf_with_invalid_input_file", status="Pass")

async def test_protect_pdf_with_invalid_output_path():
    """Test protect_pdf with invalid output directory"""
    try:
        result = await protect_pdf(
            "./unit_test/input/whitebook.pdf", 
            "./unit_test/nonexistent_dir/protected.pdf", 
            "user123", 
            "owner456"
        )
        if "Failed" in result:
            print_colored(f"test_protect_pdf_with_invalid_output_path passed (correctly failed): {result}", "green", test_name="test_protect_pdf_with_invalid_output_path", status="Pass")
        else:
            print_colored("test_protect_pdf_with_invalid_output_path failed (should have failed)", "red", test_name="test_protect_pdf_with_invalid_output_path", status="Failed")
    except Exception as e:
        print_colored(f"test_protect_pdf_with_invalid_output_path passed (exception caught): {e}", "green", test_name="test_protect_pdf_with_invalid_output_path", status="Pass")

async def test_protect_pdf_with_empty_passwords():
    """Test protect_pdf with empty passwords"""
    try:
        result = await protect_pdf(
            "./unit_test/input/whitebook.pdf", 
            "./unit_test/output/protected_empty_passwords.pdf", 
            "", 
            ""
        )
        if "Failed" in result:
            print_colored(f"test_protect_pdf_with_empty_passwords passed (correctly failed): {result}", "green", test_name="test_protect_pdf_with_empty_passwords", status="Pass")
        else:
            print_colored("test_protect_pdf_with_empty_passwords failed (should have failed)", "red", test_name="test_protect_pdf_with_empty_passwords", status="Failed")
    except Exception as e:
        print_colored(f"test_protect_pdf_with_empty_passwords passed (exception caught): {e}", "green", test_name="test_protect_pdf_with_empty_passwords", status="Pass")

async def test_protect_pdf_with_invalid_cipher():
    """Test protect_pdf with invalid cipher type"""
    try:
        result = await protect_pdf(
            "./unit_test/input/whitebook.pdf", 
            "./unit_test/output/protected_invalid_cipher.pdf", 
            "user123", 
            "owner456",
            cipher="INVALID_CIPHER"
        )
        if "Failed" in result:
            print_colored(f"test_protect_pdf_with_invalid_cipher passed (correctly failed): {result}", "green", test_name="test_protect_pdf_with_invalid_cipher", status="Pass")
        else:
            print_colored("test_protect_pdf_with_invalid_cipher failed (should have failed)", "red", test_name="test_protect_pdf_with_invalid_cipher", status="Failed")
    except Exception as e:
        print_colored(f"test_protect_pdf_with_invalid_cipher passed (exception caught): {e}", "green", test_name="test_protect_pdf_with_invalid_cipher", status="Pass")

async def test_protect_pdf_with_invalid_permissions():
    """Test protect_pdf with invalid user permissions"""
    try:
        result = await protect_pdf(
            "./unit_test/input/whitebook.pdf", 
            "./unit_test/output/protected_invalid_permissions.pdf", 
            "user123", 
            "owner456",
            userPermissions="INVALID_PERMISSION,ANOTHER_INVALID"
        )
        if "Failed" in result:
            print_colored(f"test_protect_pdf_with_invalid_permissions passed (correctly failed): {result}", "green", test_name="test_protect_pdf_with_invalid_permissions", status="Pass")
        else:
            print_colored("test_protect_pdf_with_invalid_permissions failed (should have failed)", "red", test_name="test_protect_pdf_with_invalid_permissions", status="Failed")
    except Exception as e:
        print_colored(f"test_protect_pdf_with_invalid_permissions passed (exception caught): {e}", "green", test_name="test_protect_pdf_with_invalid_permissions", status="Pass")

async def test_remove_pdf_owner_password():
    try:
        result = await remove_pdf_password("./unit_test/input/doc_password_user123_owner456.pdf", "./unit_test/output/withebook_remove_password.pdf", "owner456")
        if "Failed" in result:
           print_colored(f"test_remove_pdf_owner_password Failed: {result}", "red", test_name="test_remove_pdf_owner_password", status="Failed") 
        else:    
            print_colored("test_remove_pdf_owner_password passed", "green", test_name="test_remove_pdf_owner_password", status="Pass")
    except Exception as e:
        print_colored(f"test_remove_pdf_owner_password failed: {e}", "red", test_name="test_remove_pdf_owner_password", status="Failed")

async def test_remove_pdf_user_password():
    try:
        result = await remove_pdf_password("./unit_test/input/doc_password_user123_owner456.pdf", "./unit_test/output/withebook_remove_password.pdf", "user123")
        if "Failed" in result:
           print_colored(f"test_remove_pdf_owner_password Passed(correctly failed): {result}", "green", test_name="test_remove_pdf_owner_password", status="Pass") 
        else:    
            print_colored("test_remove_pdf_owner_password Failed", "red", test_name="test_remove_pdf_owner_password", status="Failed")
    except Exception as e:
        print_colored(f"test_remove_pdf_owner_password failed: {e}", "red", test_name="test_remove_pdf_owner_password", status="Failed")

async def test_extract_pdf_text():
    """Test extract_pdf with TEXT extraction (default)"""
    try:
        result = await extract_pdf("./unit_test/input/new.pdf", "./unit_test/output/", extract_type="TEXT")
        if "Failed" in result:
            print_colored(f"test_extract_pdf_text failed: {result}", "red", test_name="test_extract_pdf_text", status="Failed")
        else:
            print_colored("test_extract_pdf_text passed", "green", test_name="test_extract_pdf_text", status="Pass")
    except Exception as e:
        print_colored(f"test_extract_pdf_text failed: {e}", "red", test_name="test_extract_pdf_text", status="Failed")

async def test_extract_pdf_image_output():
    """Test extract_pdf with IMAGE extraction and output file"""
    try:
        result = await extract_pdf("./unit_test/input/whitebook.pdf", "./unit_test/output/1.zip", extract_type="IMAGE")
        if "Failed" in result:
            print_colored(f"test_extract_pdf_image_output failed: {result}", "red", test_name="test_extract_pdf_image_output", status="Failed")
        else:
            print_colored("test_extract_pdf_image_output passed", "green", test_name="test_extract_pdf_image_output", status="Pass")
    except Exception as e:
        print_colored(f"test_extract_pdf_image_output failed: {e}", "red", test_name="test_extract_pdf_image_output", status="Failed")

async def test_extract_pdf_with_invalid_input_file():
    """Test extract_pdf with non-existent input file"""
    try:
        result = await extract_pdf("./unit_test/input/nonexistent.pdf", "./unit_test/output/")
        if "Failed" in result:
            print_colored("test_extract_pdf_with_invalid_input_file passed (correctly failed)", "green", test_name="test_extract_pdf_with_invalid_input_file", status="Pass")
        else:
            print_colored("test_extract_pdf_with_invalid_input_file failed (should have failed)", "red", test_name="test_extract_pdf_with_invalid_input_file", status="Failed")
    except Exception as e:
        print_colored(f"test_extract_pdf_with_invalid_input_file passed (exception caught): {e}", "green", test_name="test_extract_pdf_with_invalid_input_file", status="Pass")

async def test_extract_pdf_with_invalid_output_dir():
    """Test extract_pdf with invalid output directory"""
    try:
        result = await extract_pdf("./unit_test/input/whitebook.pdf", "./unit_test/nonexistent_dir/")
        if "Failed" in result:
            print_colored("test_extract_pdf_with_invalid_output_dir passed (correctly failed)", "green", test_name="test_extract_pdf_with_invalid_output_dir", status="Pass")
        else:
            print_colored("test_extract_pdf_with_invalid_output_dir failed (should have failed)", "red", test_name="test_extract_pdf_with_invalid_output_dir", status="Failed")
    except Exception as e:
        print_colored(f"test_extract_pdf_with_invalid_output_dir passed (exception caught): {e}", "green", test_name="test_extract_pdf_with_invalid_output_dir", status="Pass")

async def test_extract_pdf_with_invalid_extract_type():
    """Test extract_pdf with invalid extract type"""
    try:
        result = await extract_pdf("./unit_test/input/whitebook.pdf", "./unit_test/output/", extract_type="INVALID_TYPE")
        if "Failed" in result:
            print_colored("test_extract_pdf_with_invalid_extract_type passed (correctly failed)", "green", test_name="test_extract_pdf_with_invalid_extract_type", status="Pass")
        else:
            print_colored("test_extract_pdf_with_invalid_extract_type failed (should have failed)", "red", test_name="test_extract_pdf_with_invalid_extract_type", status="Failed")
    except Exception as e:
        print_colored(f"test_extract_pdf_with_invalid_extract_type passed (exception caught): {e}", "green", test_name="test_extract_pdf_with_invalid_extract_type", status="Pass")

async def test_extract_pdf_with_invalid_page_range():
    """Test extract_pdf with invalid page range"""
    try:
        result = await extract_pdf("./unit_test/input/whitebook.pdf", "./unit_test/output/", extract_type="TEXT", page_range="100-200")
        if "Failed" in result:
            print_colored(f"test_extract_pdf_with_invalid_page_range failed:{result}", "red", test_name="test_extract_pdf_with_invalid_page_range", status="Failed")
        else:
            print_colored("test_extract_pdf_with_invalid_page_range failed (should have failed)", "green", test_name="test_extract_pdf_with_invalid_page_range", status="Pass")
    except Exception as e:
        print_colored(f"test_extract_pdf_with_invalid_page_range passed (exception caught): {e}", "green", test_name="test_extract_pdf_with_invalid_page_range", status="Pass")

async def test_extract_pdf_with_empty_input_path():
    """Test extract_pdf with empty input file path"""
    try:
        result = await extract_pdf("", "./unit_test/output/")
        if "Failed" in result:
            print_colored("test_extract_pdf_with_empty_input_path passed (correctly failed)", "green", test_name="test_extract_pdf_with_empty_input_path", status="Pass")
        else:
            print_colored("test_extract_pdf_with_empty_input_path failed (should have failed)", "red", test_name="test_extract_pdf_with_empty_input_path", status="Failed")
    except Exception as e:
        print_colored(f"test_extract_pdf_with_empty_input_path passed (exception caught): {e}", "green", test_name="test_extract_pdf_with_empty_input_path", status="Pass")

async def test_extract_pdf_with_empty_output_dir():
    """Test extract_pdf with empty output directory"""
    try:
        result = await extract_pdf("./unit_test/input/whitebook.pdf", "")
        if "Failed" in result:
            print_colored("test_extract_pdf_with_empty_output_dir passed (correctly failed)", "green", test_name="test_extract_pdf_with_empty_output_dir", status="Pass")
        else:
            print_colored("test_extract_pdf_with_empty_output_dir failed (should have failed)", "red", test_name="test_extract_pdf_with_empty_output_dir", status="Failed")
    except Exception as e:
        print_colored(f"test_extract_pdf_with_empty_output_dir passed (exception caught): {e}", "green", test_name="test_extract_pdf_with_empty_output_dir", status="Pass")

async def test_extract_pdf_with_non_pdf_file():
    """Test extract_pdf with a non-PDF file"""
    try:
        result = await extract_pdf("./unit_test/input/input_doc.docx", "./unit_test/output/")
        if "Failed" in result:
            print_colored("test_extract_pdf_with_non_pdf_file passed (correctly failed)", "green", test_name="test_extract_pdf_with_non_pdf_file", status="Pass")
        else:
            print_colored("test_extract_pdf_with_non_pdf_file failed (should have failed)", "red", test_name="test_extract_pdf_with_non_pdf_file", status="Failed")
    except Exception as e:
        print_colored(f"test_extract_pdf_with_non_pdf_file passed (exception caught): {e}", "green", test_name="test_extract_pdf_with_non_pdf_file", status="Pass")

async def test_extract_pdf_text_from_protected_pdf():
    """Test extract_pdf with password-protected PDF (should fail without password)"""
    try:
        result = await extract_pdf("./unit_test/input/doc_password_user123_owner456.pdf", "./unit_test/output/",password = "user123",extract_type="TEXT", page_range="1")
        if "Failed" in result:
            print_colored(f"test_extract_pdf_text_from_protected_pdf failed:{result}", "red", test_name="test_extract_pdf_text_from_protected_pdf", status="Failed")
        else:
            print_colored("test_extract_pdf_text_from_protected_pdf Passed ", "green", test_name="test_extract_pdf_text_from_protected_pdf", status="Pass")
    except Exception as e:
        print_colored(f"test_extract_pdf_text_from_protected_pdf failed (exception caught): {e}", "red", test_name="test_extract_pdf_text_from_protected_pdf", status="Failed")

async def test_convert_pdf_to_file_docx():
    """Test convert_pdf_to_file to DOCX format"""
    try:
        result = await convert_pdf_to_file(
            "./unit_test/input/new.pdf",
            "./unit_test/output/converted.docx",
        )
        if "Failed" in result:
            print_colored(f"test_convert_pdf_to_file_docx failed: {result}", "red", test_name="test_convert_pdf_to_file_docx", status="Failed")
        else:
            print_colored("test_convert_pdf_to_file_docx passed", "green", test_name="test_convert_pdf_to_file_docx", status="Pass")
    except Exception as e:
        print_colored(f"test_convert_pdf_to_file_docx failed: {e}", "red", test_name="test_convert_pdf_to_file_docx", status="Failed")

async def test_convert_pdf_to_file_xlsx():
    """Test convert_pdf_to_file to XLSX format"""
    try:
        result = await convert_pdf_to_file(
            "./unit_test/input/new.pdf",
            "./unit_test/output/converted.xlsx", 
        )
        if "Failed" in result:
            print_colored(f"test_convert_pdf_to_file_xlsx failed: {result}", "red", test_name="test_convert_pdf_to_file_xlsx", status="Failed")
        else:
            print_colored("test_convert_pdf_to_file_xlsx passed", "green", test_name="test_convert_pdf_to_file_xlsx", status="Pass")
    except Exception as e:
        print_colored(f"test_convert_pdf_to_file_xlsx failed: {e}", "red", test_name="test_convert_pdf_to_file_xlsx", status="Failed")

async def test_convert_pdf_to_file_txt():
    """Test convert_pdf_to_file to TXT format"""
    try:
        result = await convert_pdf_to_file(
            "./unit_test/input/new.pdf",
            "./unit_test/output/converted.txt",
        )
        if "Failed" in result:
            print_colored(f"test_convert_pdf_to_file_txt failed: {result}", "red", test_name="test_convert_pdf_to_file_txt", status="Failed")
        else:
            print_colored("test_convert_pdf_to_file_txt passed", "green", test_name="test_convert_pdf_to_file_txt", status="Pass")
    except Exception as e:
        print_colored(f"test_convert_pdf_to_file_txt failed: {e}", "red", test_name="test_convert_pdf_to_file_txt", status="Failed")


async def test_convert_pdf_to_file_jpg():
    """Test convert_pdf_to_file to JPG format"""
    try:
        result = await convert_pdf_to_file(
            "./unit_test/input/new.pdf",
            "./unit_test/output/converted.jpg",
        )
        if "Failed" in result:
            print_colored(f"test_convert_pdf_to_file_jpg failed: {result}", "red", test_name="test_convert_pdf_to_file_jpg", status="Failed")
        else:
            print_colored("test_convert_pdf_to_file_jpg passed", "green", test_name="test_convert_pdf_to_file_jpg", status="Pass")
    except Exception as e:
        print_colored(f"test_convert_pdf_to_file_jpg failed: {e}", "red", test_name="test_convert_pdf_to_file_jpg", status="Failed")


async def test_convert_pdf_to_file_zip():
    """Test convert_pdf_to_file to JPG format output as ZIP"""
    try:
        result = await convert_pdf_to_file(
            "./unit_test/input/new.pdf",
            "./unit_test/output/converted.zip",
            config={"pageRange":"all"}
        )
        if "Failed" in result:
            print_colored(f"test_convert_pdf_to_file_zip failed: {result}", "red", test_name="test_convert_pdf_to_file_zip", status="Failed")
        else:
            print_colored("test_convert_pdf_to_file_zip passed", "green", test_name="test_convert_pdf_to_file_zip", status="Pass")
    except Exception as e:
        print_colored(f"test_convert_pdf_to_file_zip failed: {e}", "red", test_name="test_convert_pdf_to_file_zip", status="Failed")

async def test_convert_pdf_to_file_html():
    """Test convert_pdf_to_file to HTML format"""
    try:
        result = await convert_pdf_to_file(
            "./unit_test/input/new.pdf",
            "./unit_test/output/converted.html",
        )
        if "Failed" in result:
            print_colored(f"test_convert_pdf_to_file_html failed: {result}", "red", test_name="test_convert_pdf_to_file_html", status="Failed")
        else:
            print_colored("test_convert_pdf_to_file_html passed", "green", test_name="test_convert_pdf_to_file_html", status="Pass")
    except Exception as e:
        print_colored(f"test_convert_pdf_to_file_html failed: {e}", "red", test_name="test_convert_pdf_to_file_html", status="Failed")

async def test_convert_pdf_to_file_pptx():
    """Test convert_pdf_to_file to PPTX format"""
    try:
        result = await convert_pdf_to_file(
            "./unit_test/input/new.pdf",
            "./unit_test/output/converted.pptx",
        )
        if "Failed" in result:
            print_colored(f"test_convert_pdf_to_file_pptx failed: {result}", "red", test_name="test_convert_pdf_to_file_pptx", status="Failed")
        else:
            print_colored("test_convert_pdf_to_file_pptx passed", "green", test_name="test_convert_pdf_to_file_pptx", status="Pass")
    except Exception as e:
        print_colored(f"test_convert_pdf_to_file_pptx failed: {e}", "red", test_name="test_convert_pdf_to_file_pptx", status="Failed")

async def test_convert_pdf_to_file_with_page_range():
    """Test convert_pdf_to_file with specific page range"""
    try:
        result = await convert_pdf_to_file(
            "./unit_test/input/whitebook.pdf",
            "./unit_test/output/converted_pages_1_3.png",
            config={"pageRange": "1-3"}
        )
        if "Failed" in result:
            print_colored(f"test_convert_pdf_to_file_with_page_range failed: {result}", "red", test_name="test_convert_pdf_to_file_with_page_range", status="Failed")
        else:
            print_colored("test_convert_pdf_to_file_with_page_range passed", "green", test_name="test_convert_pdf_to_file_with_page_range", status="Pass")
    except Exception as e:
        print_colored(f"test_convert_pdf_to_file_with_page_range failed: {e}", "red", test_name="test_convert_pdf_to_file_with_page_range", status="Failed")

async def test_convert_pdf_to_file_with_specific_pages():
    """Test convert_pdf_to_file with specific page numbers"""
    try:
        result = await convert_pdf_to_file(
            "./unit_test/input/whitebook.pdf",
            "./unit_test/output/converted_pages_1_3_5.png",
            config={"pageRange": "1,3,5"}
        )
        if "Failed" in result:
            print_colored(f"test_convert_pdf_to_file_with_specific_pages failed: {result}", "red", test_name="test_convert_pdf_to_file_with_specific_pages", status="Failed")
        else:
            print_colored("test_convert_pdf_to_file_with_specific_pages passed", "green", test_name="test_convert_pdf_to_file_with_specific_pages", status="Pass")
    except Exception as e:
        print_colored(f"test_convert_pdf_to_file_with_specific_pages failed: {e}", "red", test_name="test_convert_pdf_to_file_with_specific_pages", status="Failed")

async def test_convert_pdf_to_file_with_password():
    """Test convert_pdf_to_file with password-protected PDF"""
    try:
        result = await convert_pdf_to_file(
            "./unit_test/input/doc_password_user123_owner456.pdf",
            "./unit_test/output/converted_password_protected.docx",
            config={"password": "user123"}
        )
        if "Failed" in result:
            print_colored(f"test_convert_pdf_to_file_with_password failed: {result}", "red", test_name="test_convert_pdf_to_file_with_password", status="Failed")
        else:
            print_colored("test_convert_pdf_to_file_with_password passed", "green", test_name="test_convert_pdf_to_file_with_password", status="Pass")
    except Exception as e:
        print_colored(f"test_convert_pdf_to_file_with_password failed: {e}", "red", test_name="test_convert_pdf_to_file_with_password", status="Failed")

async def test_convert_pdf_to_file_with_invalid_input():
    """Test convert_pdf_to_file with non-existent input file"""
    try:
        result = await convert_pdf_to_file(
            "./unit_test/input/nonexistent.pdf",
            "./unit_test/output/converted_invalid_input.docx",
        )
        if "Failed" in result:
            print_colored("test_convert_pdf_to_file_with_invalid_input passed (correctly failed)", "green", test_name="test_convert_pdf_to_file_with_invalid_input", status="Pass")
        else:
            print_colored("test_convert_pdf_to_file_with_invalid_input failed (should have failed)", "red", test_name="test_convert_pdf_to_file_with_invalid_input", status="Failed")
    except Exception as e:
        print_colored(f"test_convert_pdf_to_file_with_invalid_input passed (exception caught): {e}", "green", test_name="test_convert_pdf_to_file_with_invalid_input", status="Pass")

async def test_convert_pdf_to_file_with_invalid_output_path():
    """Test convert_pdf_to_file with invalid output directory"""
    try:
        result = await convert_pdf_to_file(
            "./unit_test/input/new.pdf",
            "./unit_test/nonexistent_dir/converted.docx",
        )
        if "Failed" in result:
            print_colored("test_convert_pdf_to_file_with_invalid_output_path passed (correctly failed)", "green", test_name="test_convert_pdf_to_file_with_invalid_output_path", status="Pass")
        else:
            print_colored("test_convert_pdf_to_file_with_invalid_output_path failed (should have failed)", "red", test_name="test_convert_pdf_to_file_with_invalid_output_path", status="Failed")
    except Exception as e:
        print_colored(f"test_convert_pdf_to_file_with_invalid_output_path passed (exception caught): {e}", "green", test_name="test_convert_pdf_to_file_with_invalid_output_path", status="Pass")

async def test_convert_pdf_to_file_with_empty_input_path():
    """Test convert_pdf_to_file with empty input file path"""
    try:
        result = await convert_pdf_to_file(
            "",
            "./unit_test/output/converted_empty_input.docx",
        )
        if "Failed" in result:
            print_colored("test_convert_pdf_to_file_with_empty_input_path passed (correctly failed)", "green", test_name="test_convert_pdf_to_file_with_empty_input_path", status="Pass")
        else:
            print_colored("test_convert_pdf_to_file_with_empty_input_path failed (should have failed)", "red", test_name="test_convert_pdf_to_file_with_empty_input_path", status="Failed")
    except Exception as e:
        print_colored(f"test_convert_pdf_to_file_with_empty_input_path passed (exception caught): {e}", "green", test_name="test_convert_pdf_to_file_with_empty_input_path", status="Pass")

async def test_convert_pdf_to_file_with_empty_output_path():
    """Test convert_pdf_to_file with empty output file path"""
    try:
        result = await convert_pdf_to_file(
            "./unit_test/input/new.pdf",
            "",
        )
        if "Failed" in result:
            print_colored("test_convert_pdf_to_file_with_empty_output_path passed (correctly failed)", "green", test_name="test_convert_pdf_to_file_with_empty_output_path", status="Pass")
        else:
            print_colored("test_convert_pdf_to_file_with_empty_output_path failed (should have failed)", "red", test_name="test_convert_pdf_to_file_with_empty_output_path", status="Failed")
    except Exception as e:
        print_colored(f"test_convert_pdf_to_file_with_empty_output_path passed (exception caught): {e}", "green", test_name="test_convert_pdf_to_file_with_empty_output_path", status="Pass")

async def test_convert_pdf_to_file_with_wrong_password():
    """Test convert_pdf_to_file with incorrect password"""
    try:
        result = await convert_pdf_to_file(
            "./unit_test/input/doc_password_user123_owner456.pdf",
            "./unit_test/output/converted_wrong_password.docx",
            config='{"password": "wrongpassword"}'
        )
        if "Failed" in result:
            print_colored("test_convert_pdf_to_file_with_wrong_password passed (correctly failed)", "green", test_name="test_convert_pdf_to_file_with_wrong_password", status="Pass")
        else:
            print_colored("test_convert_pdf_to_file_with_wrong_password failed (should have failed)", "red", test_name="test_convert_pdf_to_file_with_wrong_password", status="Failed")
    except Exception as e:
        print_colored(f"test_convert_pdf_to_file_with_wrong_password passed (exception caught): {e}", "green", test_name="test_convert_pdf_to_file_with_wrong_password", status="Pass")

async def test_convert_pdf_to_file_with_invalid_page_range():
    """Test convert_pdf_to_file with invalid page range"""
    try:
        result = await convert_pdf_to_file(
            "./unit_test/input/new.pdf",
            "./unit_test/output/converted_invalid_range.png",
            config='{"pageRange": "100-200"}'
        )
        if "Failed" in result:
            print_colored(f"test_convert_pdf_to_file_with_invalid_page_range passed (correctly failed): {result}", "green", test_name="test_convert_pdf_to_file_with_invalid_page_range", status="Pass")
        else:
            print_colored("test_convert_pdf_to_file_with_invalid_page_range failed (should have failed)", "red", test_name="test_convert_pdf_to_file_with_invalid_page_range", status="Failed")
    except Exception as e:
        print_colored(f"test_convert_pdf_to_file_with_invalid_page_range passed (exception caught): {e}", "green", test_name="test_convert_pdf_to_file_with_invalid_page_range", status="Pass")

async def test_convert_pdf_to_file_unsupported_format():
    """Test convert_pdf_to_file with unsupported output format"""
    try:
        result = await convert_pdf_to_file(
            "./unit_test/input/new.pdf",
            "./unit_test/output/converted.xyz",
        )
        if "Failed" in result:
            print_colored("test_convert_pdf_to_file_unsupported_format passed (correctly failed)", "green", test_name="test_convert_pdf_to_file_unsupported_format", status="Pass")
        else:
            print_colored("test_convert_pdf_to_file_unsupported_format failed (should have failed)", "red", test_name="test_convert_pdf_to_file_unsupported_format", status="Failed")
    except Exception as e:
        print_colored(f"test_convert_pdf_to_file_unsupported_format passed (exception caught): {e}", "green", test_name="test_convert_pdf_to_file_unsupported_format", status="Pass")

async def test_convert_file_to_pdf_docx():
    """Test convert_file_to_pdf with DOCX format"""
    try:
        result = await convert_file_to_pdf(
            "./unit_test/input/input_doc.docx",
            "./unit_test/output/"
        )
        if "Failed" in result:
            print_colored(f"test_convert_file_to_pdf_docx failed: {result}", "red", test_name="test_convert_file_to_pdf_docx", status="Failed")
        else:
            print_colored("test_convert_file_to_pdf_docx passed", "green", test_name="test_convert_file_to_pdf_docx", status="Pass")
    except Exception as e:
        print_colored(f"test_convert_file_to_pdf_docx failed: {e}", "red", test_name="test_convert_file_to_pdf_docx", status="Failed")

async def test_convert_file_to_pdf_doc():
    """Test convert_file_to_pdf with DOC format"""
    try:
        result = await convert_file_to_pdf(
            "./unit_test/input/input_doc.doc",
            "./unit_test/output/converted_from_doc.pdf"
        )
        if "Failed" in result:
            print_colored(f"test_convert_file_to_pdf_doc failed: {result}", "red", test_name="test_convert_file_to_pdf_doc", status="Failed")
        else:
            print_colored("test_convert_file_to_pdf_doc passed", "green", test_name="test_convert_file_to_pdf_doc", status="Pass")
    except Exception as e:
        print_colored(f"test_convert_file_to_pdf_doc failed: {e}", "red", test_name="test_convert_file_to_pdf_doc", status="Failed")

async def test_convert_file_to_pdf_pptx():
    """Test convert_file_to_pdf with PPTX format"""
    try:
        result = await convert_file_to_pdf(
            "./unit_test/input/input_presentation.pptx",
            "./unit_test/output/converted_from_pptx.pdf"
        )
        if "Failed" in result:
            print_colored(f"test_convert_file_to_pdf_pptx failed: {result}", "red", test_name="test_convert_file_to_pdf_pptx", status="Failed")
        else:
            print_colored("test_convert_file_to_pdf_pptx passed", "green", test_name="test_convert_file_to_pdf_pptx", status="Pass")
    except Exception as e:
        print_colored(f"test_convert_file_to_pdf_pptx failed: {e}", "red", test_name="test_convert_file_to_pdf_pptx", status="Failed")

async def test_convert_file_to_pdf_ppt():
    """Test convert_file_to_pdf with PPT format"""
    try:
        result = await convert_file_to_pdf(
            "./unit_test/input/input_presentation.ppt",
            "./unit_test/output/converted_from_ppt.pdf"
        )
        if "Failed" in result:
            print_colored(f"test_convert_file_to_pdf_ppt failed: {result}", "red", test_name="test_convert_file_to_pdf_ppt", status="Failed")
        else:
            print_colored("test_convert_file_to_pdf_ppt passed", "green", test_name="test_convert_file_to_pdf_ppt", status="Pass")
    except Exception as e:
        print_colored(f"test_convert_file_to_pdf_ppt failed: {e}", "red", test_name="test_convert_file_to_pdf_ppt", status="Failed")

async def test_convert_file_to_pdf_xlsx():
    """Test convert_file_to_pdf with XLSX format"""
    try:
        result = await convert_file_to_pdf(
            "./unit_test/input/input_spreadsheet.xlsx",
            "./unit_test/output/converted_from_xlsx.pdf"
        )
        if "Failed" in result:
            print_colored(f"test_convert_file_to_pdf_xlsx failed: {result}", "red", test_name="test_convert_file_to_pdf_xlsx", status="Failed")
        else:
            print_colored("test_convert_file_to_pdf_xlsx passed", "green", test_name="test_convert_file_to_pdf_xlsx", status="Pass")
    except Exception as e:
        print_colored(f"test_convert_file_to_pdf_xlsx failed: {e}", "red", test_name="test_convert_file_to_pdf_xlsx", status="Failed")

async def test_convert_file_to_pdf_xls():
    """Test convert_file_to_pdf with XLS format"""
    try:
        result = await convert_file_to_pdf(
            "./unit_test/input/input_spreadsheet.xls",
            "./unit_test/output/converted_from_xls.pdf"
        )
        if "Failed" in result:
            print_colored(f"test_convert_file_to_pdf_xls failed: {result}", "red", test_name="test_convert_file_to_pdf_xls", status="Failed")
        else:
            print_colored("test_convert_file_to_pdf_xls passed", "green", test_name="test_convert_file_to_pdf_xls", status="Pass")
    except Exception as e:
        print_colored(f"test_convert_file_to_pdf_xls failed: {e}", "red", test_name="test_convert_file_to_pdf_xls", status="Failed")

async def test_convert_file_to_pdf_txt():
    """Test convert_file_to_pdf with TXT format"""
    try:
        result = await convert_file_to_pdf(
            "./unit_test/input/input_text.txt",
            "./unit_test/output/converted_from_txt.pdf"
        )
        if "Failed" in result:
            print_colored(f"test_convert_file_to_pdf_txt failed: {result}", "red", test_name="test_convert_file_to_pdf_txt", status="Failed")
        else:
            print_colored("test_convert_file_to_pdf_txt passed", "green", test_name="test_convert_file_to_pdf_txt", status="Pass")
    except Exception as e:
        print_colored(f"test_convert_file_to_pdf_txt failed: {e}", "red", test_name="test_convert_file_to_pdf_txt", status="Failed")

async def test_convert_file_to_pdf_jpg():
    """Test convert_file_to_pdf with JPG format"""
    try:
        result = await convert_file_to_pdf(
            "./unit_test/input/input_image.jpg",
            "./unit_test/output/converted_from_jpg.zip"
        )
        if "Failed" in result:
            print_colored(f"test_convert_file_to_pdf_jpg failed: {result}", "red", test_name="test_convert_file_to_pdf_jpg", status="Failed")
        else:
            print_colored("test_convert_file_to_pdf_jpg passed", "green", test_name="test_convert_file_to_pdf_jpg", status="Pass")
    except Exception as e:
        print_colored(f"test_convert_file_to_pdf_jpg failed: {e}", "red", test_name="test_convert_file_to_pdf_jpg", status="Failed")

async def test_convert_file_to_pdf_png():
    """Test convert_file_to_pdf with PNG format"""
    try:
        result = await convert_file_to_pdf(
            "./unit_test/input/input_image.png",
            "./unit_test/output/converted_from_png.pdf"
        )
        if "Failed" in result:
            print_colored(f"test_convert_file_to_pdf_png failed: {result}", "red", test_name="test_convert_file_to_pdf_png", status="Failed")
        else:
            print_colored("test_convert_file_to_pdf_png passed", "green", test_name="test_convert_file_to_pdf_png", status="Pass")
    except Exception as e:
        print_colored(f"test_convert_file_to_pdf_png failed: {e}", "red", test_name="test_convert_file_to_pdf_png", status="Failed")

async def test_convert_file_to_pdf_gif():
    """Test convert_file_to_pdf with GIF format"""
    try:
        result = await convert_file_to_pdf(
            "./unit_test/input/input_image.gif",
            "./unit_test/output/converted_from_gif.pdf"
        )
        if "Failed" in result:
            print_colored(f"test_convert_file_to_pdf_gif failed: {result}", "red", test_name="test_convert_file_to_pdf_gif", status="Failed")
        else:
            print_colored("test_convert_file_to_pdf_gif passed", "green", test_name="test_convert_file_to_pdf_gif", status="Pass")
    except Exception as e:
        print_colored(f"test_convert_file_to_pdf_gif failed: {e}", "red", test_name="test_convert_file_to_pdf_gif", status="Failed")

async def test_convert_file_to_pdf_with_invalid_input():
    """Test convert_file_to_pdf with non-existent input file"""
    try:
        result = await convert_file_to_pdf(
            "./unit_test/input/nonexistent.docx",
            "./unit_test/output/converted_invalid_input.pdf"
        )
        if "Failed" in result:
            print_colored("test_convert_file_to_pdf_with_invalid_input passed (correctly failed)", "green", test_name="test_convert_file_to_pdf_with_invalid_input", status="Pass")
        else:
            print_colored("test_convert_file_to_pdf_with_invalid_input failed (should have failed)", "red", test_name="test_convert_file_to_pdf_with_invalid_input", status="Failed")
    except Exception as e:
        print_colored(f"test_convert_file_to_pdf_with_invalid_input passed (exception caught): {e}", "green", test_name="test_convert_file_to_pdf_with_invalid_input", status="Pass")

async def test_convert_file_to_pdf_with_invalid_output_path():
    """Test convert_file_to_pdf with invalid output directory"""
    try:
        result = await convert_file_to_pdf(
            "./unit_test/input/input_doc.docx",
            "./unit_test/nonexistent_dir/converted.pdf"
        )
        if "Failed" in result:
            print_colored("test_convert_file_to_pdf_with_invalid_output_path passed (correctly failed)", "green", test_name="test_convert_file_to_pdf_with_invalid_output_path", status="Pass")
        else:
            print_colored("test_convert_file_to_pdf_with_invalid_output_path failed (should have failed)", "red", test_name="test_convert_file_to_pdf_with_invalid_output_path", status="Failed")
    except Exception as e:
        print_colored(f"test_convert_file_to_pdf_with_invalid_output_path passed (exception caught): {e}", "green", test_name="test_convert_file_to_pdf_with_invalid_output_path", status="Pass")

async def test_convert_file_to_pdf_with_empty_input_path():
    """Test convert_file_to_pdf with empty input file path"""
    try:
        result = await convert_file_to_pdf(
            "",
            "./unit_test/output/converted_empty_input.pdf"
        )
        if "Failed" in result:
            print_colored("test_convert_file_to_pdf_with_empty_input_path passed (correctly failed)", "green", test_name="test_convert_file_to_pdf_with_empty_input_path", status="Pass")
        else:
            print_colored("test_convert_file_to_pdf_with_empty_input_path failed (should have failed)", "red", test_name="test_convert_file_to_pdf_with_empty_input_path", status="Failed")
    except Exception as e:
        print_colored(f"test_convert_file_to_pdf_with_empty_input_path passed (exception caught): {e}", "green", test_name="test_convert_file_to_pdf_with_empty_input_path", status="Pass")

async def test_convert_file_to_pdf_with_empty_output_path():
    """Test convert_file_to_pdf with empty output file path"""
    try:
        result = await convert_file_to_pdf(
            "./unit_test/input/input_doc.docx",
            ""
        )
        if "Failed" in result:
            print_colored("test_convert_file_to_pdf_with_empty_output_path passed (correctly failed)", "green", test_name="test_convert_file_to_pdf_with_empty_output_path", status="Pass")
        else:
            print_colored("test_convert_file_to_pdf_with_empty_output_path failed (should have failed)", "red", test_name="test_convert_file_to_pdf_with_empty_output_path", status="Failed")
    except Exception as e:
        print_colored(f"test_convert_file_to_pdf_with_empty_output_path passed (exception caught): {e}", "green", test_name="test_convert_file_to_pdf_with_empty_output_path", status="Pass")

async def test_convert_file_to_pdf_unsupported_format():
    """Test convert_file_to_pdf with unsupported file format"""
    try:
        result = await convert_file_to_pdf(
            "./unit_test/input/unsupported_file.xyz",
            "./unit_test/output/converted_unsupported.pdf"
        )
        if "Failed" in result:
            print_colored("test_convert_file_to_pdf_unsupported_format passed (correctly failed)", "green", test_name="test_convert_file_to_pdf_unsupported_format", status="Pass")
        else:
            print_colored("test_convert_file_to_pdf_unsupported_format failed (should have failed)", "red", test_name="test_convert_file_to_pdf_unsupported_format", status="Failed")
    except Exception as e:
        print_colored(f"test_convert_file_to_pdf_unsupported_format passed (exception caught): {e}", "green", test_name="test_convert_file_to_pdf_unsupported_format", status="Pass")

async def test_compare_pdfs_with_all_comparison():
    """Test compare_pdfs with ALL comparison type"""
    try:
        result = await compare_pdfs(
            "./unit_test/input/new.pdf",
            "./unit_test/input/old.pdf", 
            "./unit_test/output/compare_all.pdf",
            config={"compareType": "ALL", "resultType": "PDF"}
        )
        print_colored(f"✓ test_compare_pdfs_with_all_comparison: {result}", "green", "test_compare_pdfs_with_all_comparison", "PASS")
        await check_file_exists("./unit_test/output/compare_all.pdf")
    except Exception as e:
        print_colored(f"✗ test_compare_pdfs_with_all_comparison failed: {str(e)}", "red", "test_compare_pdfs_with_all_comparison", "FAIL")

async def test_compare_pdfs_with_json_result():
    """Test compare_pdfs with JSON result type"""
    try:
        result = await compare_pdfs(
            "./unit_test/input/new.pdf",
            "./unit_test/input/old.pdf", 
            "./unit_test/output/compare_result.json",
            config={"compareType": "TEXT", "resultType": "JSON"}
        )
        print_colored(f"✓ test_compare_pdfs_with_json_result: {result}", "green", "test_compare_pdfs_with_json_result", "PASS")
        await check_file_exists("./unit_test/output/compare_result.json")
    except Exception as e:
        print_colored(f"✗ test_compare_pdfs_with_json_result failed: {str(e)}", "red", "test_compare_pdfs_with_json_result", "FAIL")

async def test_compare_pdfs_with_invalid_first_file():
    """Test compare_pdfs with non-existent first PDF file"""
    try:
        result = await compare_pdfs(
            "./unit_test/input/nonexistent1.pdf",
            "./unit_test/input/old.pdf", 
            "./unit_test/output/compare_invalid1.pdf"
        )
        if "Failed" in result:
            print_colored(f"✓ test_compare_pdfs_with_invalid_first_file: Expected error - {result}", "green", "test_compare_pdfs_with_invalid_first_file", "PASS")
        else:
            print_colored(f"✗ test_compare_pdfs_with_invalid_first_file should have failed", "red", "test_compare_pdfs_with_invalid_first_file", "FAIL")
    except Exception as e:
        print_colored(f"✓ test_compare_pdfs_with_invalid_first_file: Expected error - {str(e)}", "green", "test_compare_pdfs_with_invalid_first_file", "PASS")

async def test_compare_pdfs_with_invalid_second_file():
    """Test compare_pdfs with non-existent second PDF file"""
    try:
        result = await compare_pdfs(
            "./unit_test/input/new.pdf",
            "./unit_test/input/nonexistent2.pdf", 
            "./unit_test/output/compare_invalid2.pdf"
        )
        if "Failed" in result:
            print_colored(f"✓ test_compare_pdfs_with_invalid_second_file: Expected error - {result}", "green", "test_compare_pdfs_with_invalid_second_file", "PASS")
        else:
            print_colored(f"✗ test_compare_pdfs_with_invalid_second_file should have failed", "red", "test_compare_pdfs_with_invalid_second_file", "FAIL")
    except Exception as e:
        print_colored(f"✓ test_compare_pdfs_with_invalid_second_file: Expected error - {str(e)}", "green", "test_compare_pdfs_with_invalid_second_file", "PASS")

async def test_compare_pdfs_with_invalid_output_path():
    """Test compare_pdfs with invalid output directory"""
    try:
        result = await compare_pdfs(
            "./unit_test/input/new.pdf",
            "./unit_test/input/old.pdf", 
            "./invalid_directory/compare_result.pdf"
        )
        if "Failed" in result:
            print_colored(f"✓ test_compare_pdfs_with_invalid_output_path: Expected error - {result}", "green", "test_compare_pdfs_with_invalid_output_path", "PASS")
        else:
            print_colored(f"✗ test_compare_pdfs_with_invalid_output_path should have failed", "red", "test_compare_pdfs_with_invalid_output_path", "FAIL")
    except Exception as e:
        print_colored(f"✓ test_compare_pdfs_with_invalid_output_path: Expected error - {str(e)}", "green", "test_compare_pdfs_with_invalid_output_path", "PASS")

async def test_compare_pdfs_with_empty_first_path():
    """Test compare_pdfs with empty first file path"""
    try:
        result = await compare_pdfs(
            "",
            "./unit_test/input/old.pdf", 
            "./unit_test/output/compare_empty1.pdf"
        )
        if "Failed" in result:
            print_colored(f"✓ test_compare_pdfs_with_empty_first_path: Expected error - {result}", "green", "test_compare_pdfs_with_empty_first_path", "PASS")
        else:
            print_colored(f"✗ test_compare_pdfs_with_empty_first_path should have failed", "red", "test_compare_pdfs_with_empty_first_path", "FAIL")
    except Exception as e:
        print_colored(f"✓ test_compare_pdfs_with_empty_first_path: Expected error - {str(e)}", "green", "test_compare_pdfs_with_empty_first_path", "PASS")

async def test_compare_pdfs_with_empty_second_path():
    """Test compare_pdfs with empty second file path"""
    try:
        result = await compare_pdfs(
            "./unit_test/input/new.pdf",
            "", 
            "./unit_test/output/compare_empty2.pdf"
        )
        if "Failed" in result:
            print_colored(f"✓ test_compare_pdfs_with_empty_second_path: Expected error - {result}", "green", "test_compare_pdfs_with_empty_second_path", "PASS")
        else:
            print_colored(f"✗ test_compare_pdfs_with_empty_second_path should have failed", "red", "test_compare_pdfs_with_empty_second_path", "FAIL")
    except Exception as e:
        print_colored(f"✓ test_compare_pdfs_with_empty_second_path: Expected error - {str(e)}", "green", "test_compare_pdfs_with_empty_second_path", "PASS")

async def test_compare_pdfs_with_empty_output_path():
    """Test compare_pdfs with empty output file path"""
    try:
        result = await compare_pdfs(
            "./unit_test/input/new.pdf",
            "./unit_test/input/old.pdf", 
            ""
        )
        if "Failed" in result:
            print_colored(f"✓ test_compare_pdfs_with_empty_output_path: Expected error - {result}", "green", "test_compare_pdfs_with_empty_output_path", "PASS")
        else:
            print_colored(f"✗ test_compare_pdfs_with_empty_output_path should have failed", "red", "test_compare_pdfs_with_empty_output_path", "FAIL")
    except Exception as e:
        print_colored(f"✓ test_compare_pdfs_with_empty_output_path: Expected error - {str(e)}", "green", "test_compare_pdfs_with_empty_output_path", "PASS")

async def test_compare_pdfs_with_invalid_compare_type():
    """Test compare_pdfs with invalid comparison type"""
    try:
        result = await compare_pdfs(
            "./unit_test/input/new.pdf",
            "./unit_test/input/old.pdf", 
            "./unit_test/output/compare_invalid_type.pdf",
            config={"compareType": "INVALID_TYPE", "resultType": "PDF"}
        )
        if "Failed" in result:
            print_colored(f"✓ test_compare_pdfs_with_invalid_compare_type: Expected error - {result}", "green", "test_compare_pdfs_with_invalid_compare_type", "PASS")
        else:
            print_colored(f"✗ test_compare_pdfs_with_invalid_compare_type should have failed", "red", "test_compare_pdfs_with_invalid_compare_type", "FAIL")
    except Exception as e:
        print_colored(f"✓ test_compare_pdfs_with_invalid_compare_type: Expected error - {str(e)}", "green", "test_compare_pdfs_with_invalid_compare_type", "PASS")

async def test_compare_pdfs_with_invalid_result_type():
    """Test compare_pdfs with invalid result type"""
    try:
        result = await compare_pdfs(
            "./unit_test/input/new.pdf",
            "./unit_test/input/old.pdf", 
            "./unit_test/output/compare_invalid_result.pdf",
            config={"compareType": "TEXT", "resultType": "INVALID_RESULT"}
        )
        if "Failed" in result:
            print_colored(f"✓ test_compare_pdfs_with_invalid_result_type: Expected error - {result}", "green", "test_compare_pdfs_with_invalid_result_type", "PASS")
        else:
            print_colored(f"✗ test_compare_pdfs_with_invalid_result_type should have failed", "red", "test_compare_pdfs_with_invalid_result_type", "FAIL")
    except Exception as e:
        print_colored(f"✓ test_compare_pdfs_with_invalid_result_type: Expected error - {str(e)}", "green", "test_compare_pdfs_with_invalid_result_type", "PASS")

async def test_compare_pdfs_with_non_pdf_first_file():
    """Test compare_pdfs with non-PDF first file"""
    try:
        result = await compare_pdfs(
            "./unit_test/input/sample.txt",
            "./unit_test/input/old.pdf", 
            "./unit_test/output/compare_non_pdf1.pdf"
        )
        if "Failed" in result:
            print_colored(f"✓ test_compare_pdfs_with_non_pdf_first_file: Expected error - {result}", "green", "test_compare_pdfs_with_non_pdf_first_file", "PASS")
        else:
            print_colored(f"✗ test_compare_pdfs_with_non_pdf_first_file should have failed", "red", "test_compare_pdfs_with_non_pdf_first_file", "FAIL")
    except Exception as e:
        print_colored(f"✓ test_compare_pdfs_with_non_pdf_first_file: Expected error - {str(e)}", "green", "test_compare_pdfs_with_non_pdf_first_file", "PASS")

async def test_compare_pdfs_with_non_pdf_second_file():
    """Test compare_pdfs with non-PDF second file"""
    try:
        result = await compare_pdfs(
            "./unit_test/input/new.pdf",
            "./unit_test/input/sample.txt", 
            "./unit_test/output/compare_non_pdf2.pdf"
        )
        if "Failed" in result:
            print_colored(f"✓ test_compare_pdfs_with_non_pdf_second_file: Expected error - {result}", "green", "test_compare_pdfs_with_non_pdf_second_file", "PASS")
        else:
            print_colored(f"✗ test_compare_pdfs_with_non_pdf_second_file should have failed", "red", "test_compare_pdfs_with_non_pdf_second_file", "FAIL")
    except Exception as e:
        print_colored(f"✓ test_compare_pdfs_with_non_pdf_second_file: Expected error - {str(e)}", "green", "test_compare_pdfs_with_non_pdf_second_file", "PASS")

async def test_compare_identical_pdfs():
    """Test compare_pdfs with identical PDF files"""
    try:
        result = await compare_pdfs(
            "./unit_test/input/new.pdf",
            "./unit_test/input/new.pdf", 
            "./unit_test/output/compare_identical.pdf",
            config={"compareType": "ALL", "resultType": "PDF"}
        )
        print_colored(f"✓ test_compare_identical_pdfs: {result}", "green", "test_compare_identical_pdfs", "PASS")
        await check_file_exists("./unit_test/output/compare_identical.pdf")
    except Exception as e:
        print_colored(f"✗ test_compare_identical_pdfs failed: {str(e)}", "red", "test_compare_identical_pdfs", "FAIL")

async def test_compare_pdfs_with_null_config():
    """Test compare_pdfs with None config"""
    try:
        result = await compare_pdfs(
            "./unit_test/input/new.pdf",
            "./unit_test/input/old.pdf", 
            "./unit_test/output/compare_null_config.pdf",
            config=None
        )
        print_colored(f"✓ test_compare_pdfs_with_null_config: {result}", "green", "test_compare_pdfs_with_null_config", "PASS")
        await check_file_exists("./unit_test/output/compare_null_config.pdf")
    except Exception as e:
        print_colored(f"✗ test_compare_pdfs_with_null_config failed: {str(e)}", "red", "test_compare_pdfs_with_null_config", "FAIL")

# Convert URL to PDF Tests
async def test_convert_url_to_pdf_valid_url():
    """Test convert_url_to_pdf with a valid URL"""
    try:
        result = await convert_url_to_pdf(
            "https://www.example.com",
            "./unit_test/output/converted_example_com.pdf"
        )
        if "Failed" in result:
            print_colored(f"test_convert_url_to_pdf_valid_url failed: {result}", "red", test_name="test_convert_url_to_pdf_valid_url", status="Failed")
        else:
            print_colored("test_convert_url_to_pdf_valid_url passed", "green", test_name="test_convert_url_to_pdf_valid_url", status="Pass")
    except Exception as e:
        print_colored(f"test_convert_url_to_pdf_valid_url failed: {e}", "red", test_name="test_convert_url_to_pdf_valid_url", status="Failed")

async def test_convert_url_to_pdf_invalid_url():
    """Test convert_url_to_pdf with an invalid URL"""
    try:
        result = await convert_url_to_pdf(
            "https://invalid-url-that-does-not-exist-12345.com",
            "./unit_test/output/converted_invalid_url.pdf"
        )
        if "Failed" in result:
            print_colored("test_convert_url_to_pdf_invalid_url passed (correctly failed)", "green", test_name="test_convert_url_to_pdf_invalid_url", status="Pass")
        else:
            print_colored("test_convert_url_to_pdf_invalid_url failed (should have failed)", "red", test_name="test_convert_url_to_pdf_invalid_url", status="Failed")
    except Exception as e:
        print_colored(f"test_convert_url_to_pdf_invalid_url passed (exception caught): {e}", "green", test_name="test_convert_url_to_pdf_invalid_url", status="Pass")

async def test_convert_url_to_pdf_empty_url():
    """Test convert_url_to_pdf with empty URL"""
    try:
        result = await convert_url_to_pdf(
            "",
            "./unit_test/output/converted_empty_url.pdf"
        )
        if "Failed" in result:
            print_colored("test_convert_url_to_pdf_empty_url passed (correctly failed)", "green", test_name="test_convert_url_to_pdf_empty_url", status="Pass")
        else:
            print_colored("test_convert_url_to_pdf_empty_url failed (should have failed)", "red", test_name="test_convert_url_to_pdf_empty_url", status="Failed")
    except Exception as e:
        print_colored(f"test_convert_url_to_pdf_empty_url passed (exception caught): {e}", "green", test_name="test_convert_url_to_pdf_empty_url", status="Pass")


async def run_combine_tests():
    """Run all combine PDF tests"""
    print_colored("Running Combine PDF Tests...", "blue")
    await test_combine_pdfs()
    # await test_combine_pdfs_with_bookmarks()
    # await test_combine_pdfs_with_toc()
    # await test_combine_pdfs_with_custom_toc()
    # await test_combine_pdfs_with_invalid_path()

async def run_split_tests():
    """Run all split PDF tests"""
    print_colored("Running Split PDF Tests...", "blue")
    await test_split_pdf()
    await test_split_pdf_with_two_pages()
    await test_split_pdf_with_ten_pages()
    await test_split_single_page_pdf()
    await test_split_pdf_with_fewer_pages_than_split_count()
    await test_split_pdf_with_invalid_file()

async def run_linearize_tests():
    """Run all linearize PDF tests"""
    print_colored("Running Linearize PDF Tests...", "blue")
    await test_linearize_pdf()
    await test_linearize_pdf_with_invalid_input_file()
    await test_linearize_pdf_with_invalid_output_path()
    await test_linearize_pdf_with_empty_input_path()
    await test_linearize_pdf_overwrite_existing_file()

async def run_flatten_tests():
    """Run all flatten PDF tests"""
    print_colored("Running Flatten PDF Tests...", "blue")
    await test_flatten_pdf()
    await test_flatten_pdf_with_password()
    await test_flatten_pdf_with_invalid_input_file()
    await test_flatten_pdf_with_invalid_output_path()
    await test_flatten_pdf_with_empty_input_path()
    await test_flatten_pdf_with_empty_output_path()
    await test_flatten_pdf_with_non_pdf_file()

async def run_manipulate_tests():
    """Run all manipulate PDF tests"""
    print_colored("Running Manipulate PDF Tests...", "blue")
    #await test_manipulate_pdf_all_pages()
    await test_manipulate_pdf()
    await test_manipulate_pdf_with_invalid_input_file()
    await test_manipulate_pdf_with_invalid_output_path()
    await test_manipulate_pdf_with_empty_operations()
    await test_manipulate_pdf_with_invalid_operation_type()

async def run_compress_tests():
    """Run all compress PDF tests"""
    print_colored("Running Compress PDF Tests...", "blue")
    await test_compress_pdf()
    await test_compress_pdf_high_level()
    await test_compress_pdf_medium_level()
    await test_compress_pdf_low_level()
    await test_compress_pdf_with_invalid_input_file()
    await test_compress_pdf_with_invalid_output_path()
    await test_compress_pdf_with_invalid_compression_level()
    await test_compress_pdf_with_empty_input_path()
    await test_compress_pdf_with_empty_output_path()

async def run_protect_tests():
    """Run all protect PDF tests"""
    print_colored("Running Protect PDF Tests...", "blue")
    await test_protect_pdf()
    await test_protect_pdf_with_invaid_permissions()
    await test_protect_pdf_with_all_options()
    await test_protect_pdf_with_same_passwords()
    await test_protect_pdf_with_invalid_input_file()
    await test_protect_pdf_with_invalid_output_path()
    await test_protect_pdf_with_empty_passwords()
    await test_protect_pdf_with_invalid_cipher()
    await test_protect_pdf_with_invalid_permissions()

async def run_password_tests():
    """Run all password removal tests"""
    print_colored("Running Password Removal Tests...", "blue")
    await test_remove_pdf_owner_password()
    await test_remove_pdf_user_password()

async def run_extract_tests():
    """Run all extract PDF tests"""
    print_colored("Running Extract PDF Tests...", "blue")
    await test_extract_pdf_text()
    await test_extract_pdf_image_output()
    await test_extract_pdf_with_invalid_input_file()
    await test_extract_pdf_with_invalid_output_dir()
    await test_extract_pdf_with_invalid_extract_type()
    await test_extract_pdf_with_invalid_page_range()
    await test_extract_pdf_with_empty_input_path()
    await test_extract_pdf_with_empty_output_dir()
    await test_extract_pdf_with_non_pdf_file()
    await test_extract_pdf_text_from_protected_pdf()

async def run_pdf_to_file_tests():
    """Run all PDF to file conversion tests"""
    print_colored("Running PDF to File Conversion Tests...", "blue")
    await test_convert_pdf_to_file_docx()
    await test_convert_pdf_to_file_xlsx()
    await test_convert_pdf_to_file_txt()
    await test_convert_pdf_to_file_jpg()
    await test_convert_pdf_to_file_zip()
    await test_convert_pdf_to_file_html()
    await test_convert_pdf_to_file_pptx()
    await test_convert_pdf_to_file_with_page_range()
    await test_convert_pdf_to_file_with_specific_pages()
    await test_convert_pdf_to_file_with_password()
    await test_convert_pdf_to_file_with_invalid_input()
    await test_convert_pdf_to_file_with_invalid_output_path()
    await test_convert_pdf_to_file_with_empty_input_path()
    await test_convert_pdf_to_file_with_empty_output_path()
    await test_convert_pdf_to_file_with_wrong_password()
    await test_convert_pdf_to_file_with_invalid_page_range()
    await test_convert_pdf_to_file_unsupported_format()

async def run_file_to_pdf_tests():
    """Run all file to PDF conversion tests"""
    print_colored("Running File to PDF Conversion Tests...", "blue")
    await test_convert_file_to_pdf_docx()
    await test_convert_file_to_pdf_doc()
    await test_convert_file_to_pdf_pptx()
    await test_convert_file_to_pdf_ppt()
    await test_convert_file_to_pdf_xlsx()
    await test_convert_file_to_pdf_xls()
    await test_convert_file_to_pdf_txt()
    await test_convert_file_to_pdf_jpg()
    await test_convert_file_to_pdf_png()
    await test_convert_file_to_pdf_gif()
    await test_convert_file_to_pdf_with_invalid_input()
    await test_convert_file_to_pdf_with_invalid_output_path()
    await test_convert_file_to_pdf_with_empty_input_path()
    await test_convert_file_to_pdf_with_empty_output_path()
    await test_convert_file_to_pdf_unsupported_format()
    await test_convert_url_to_pdf_valid_url()
    await test_convert_url_to_pdf_invalid_url()
    await test_convert_url_to_pdf_empty_url()

async def run_compare_tests():
    """Run all compare PDF tests"""
    print_colored("Running Compare PDF Tests...", "blue")
    await test_compare_pdfs_with_all_comparison()
    await test_compare_pdfs_with_json_result()
    await test_compare_pdfs_with_invalid_first_file()
    await test_compare_pdfs_with_invalid_second_file()
    await test_compare_pdfs_with_invalid_output_path()
    await test_compare_pdfs_with_empty_first_path()
    await test_compare_pdfs_with_empty_second_path()
    await test_compare_pdfs_with_empty_output_path()
    await test_compare_pdfs_with_invalid_compare_type()
    await test_compare_pdfs_with_invalid_result_type()
    await test_compare_pdfs_with_non_pdf_first_file()
    await test_compare_pdfs_with_non_pdf_second_file()
    await test_compare_identical_pdfs()
    await test_compare_pdfs_with_null_config()

def show_menu():
    """Display test menu options"""
    print_colored("\n=== PDF API Unit Test Menu ===", "yellow")
    print("1. Combine PDF Tests")
    print("2. Split PDF Tests")
    print("3. Linearize PDF Tests")
    print("4. Flatten PDF Tests")
    print("5. Manipulate PDF Tests")
    print("6. Compress PDF Tests")
    print("7. Protect PDF Tests")
    print("8. Password Removal Tests")
    print("9. Extract PDF Tests")
    print("10. PDF to File Conversion Tests")
    print("11. File to PDF Conversion Tests")
    print("12. Compare PDF Tests")
    print("13. Run All Tests")
    print("0. Exit")
    print_colored("=" * 35, "yellow")

async def run_selected_tests(choice):
    """Run tests based on user selection"""
    test_functions = {
        1: run_combine_tests,
        2: run_split_tests,
        3: run_linearize_tests,
        4: run_flatten_tests,
        5: run_manipulate_tests,
        6: run_compress_tests,
        7: run_protect_tests,
        8: run_password_tests,
        9: run_extract_tests,
        10: run_pdf_to_file_tests,
        11: run_file_to_pdf_tests,
        12: run_compare_tests,
    }
    
    if choice == 13:  # Run all tests
        print_colored("Running All Tests...", "yellow")
        for test_func in test_functions.values():
            await test_func()
            print()  # Add spacing between test groups
    elif choice in test_functions:
        await test_functions[choice]()
    else:
        print_colored("Invalid choice. Please select a valid option.", "red")

async def main():
    """Main function with interactive menu"""
    clear_output_directory()
    
    while True:
        show_menu()
        try:
            choice = int(input("Please select an option (0-13): "))
            
            if choice == 0:
                print_colored("Exiting test runner...", "yellow")
                break
            
            print_colored(f"\nStarting selected tests...\n", "green")
            await run_selected_tests(choice)
            print_colored(f"\nTests completed!\n", "green")
            
        except ValueError:
            print_colored("Invalid input. Please enter a number between 0-13.", "red")
        except KeyboardInterrupt:
            print_colored("\nTest execution interrupted by user.", "yellow")
            break

if __name__ == "__main__":
    asyncio.run(main())