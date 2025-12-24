# Unit Test Instructions

## How to Run `unit_pytest.py`

1. **Ensure Dependencies Are Installed**:
   Make sure you have all the required Python packages installed. You can install them using the following command:
   ```bash
   pip install -r ../requirements.txt
   ```

2. **Run the Unit Tests**:
   Execute the `unit_pytest.py` script using Python. Use the following command:
   ```bash
   python unit_pytest.py
   ```

3. **Interactive Menu**:
   The script provides an interactive menu to select specific test categories or run all tests. Follow the on-screen instructions to choose the desired option.

## How to View Test Results

1. **Console Output**:
   The test results will be displayed in the console with color-coded messages:
   - Green: Indicates a passed test.
   - Red: Indicates a failed test.

2. **Excel Report**:
   A detailed test report is saved in an Excel file located at:
   ```
   ./unit_test/output/test_results.xlsx
   ```
   Open this file to view the following details:
   - Timestamp: When the test was executed.
   - Test Name: The name of the test function.
   - Message: Additional information about the test result.
   - Status: Whether the test passed or failed.

## Notes
- Ensure the `output` directory exists before running the tests.
- If the `test_results.xlsx` file already exists, it will be overwritten with the latest results.