# Automated Conversion Tests

This folder contains an automated test script to verify the stored procedure and DDL conversion functionality of the application.

## Test Script: `test_conversion.py`

The `test_conversion.py` script is a Python script that uses the `requests` library to make API calls to the conversion endpoints and verify the results.

### Test Cases

The script includes the following test cases:

1.  **`test_spf_conversion_from_text()`**: Tests the conversion of a stored procedure from a text string. It reads the content of `sql-assests/sample.sql` and sends it to the `/convert` endpoint.

2.  **`test_ddl_conversion_from_text()`**: Tests the conversion of a DDL from a text string. It uses a simple `CREATE TABLE` statement and sends it to the `/convert-ddl` endpoint.

3.  **`test_spf_conversion_from_file()`**: Tests the conversion of a stored procedure from a file. It uploads the `sql-assests/sample.sql` file to the `/convert-file` endpoint.

4.  **`test_ddl_conversion_from_file()`**: Tests the conversion of a DDL from a file. It creates a temporary file with a `CREATE TABLE` statement and uploads it to the `/convert-ddl-file` endpoint.

### How to Run the Tests

To run the tests, make sure the application is running (you can use the `gini.sh` script for this). Then, execute the following command from the root directory of the project:

```bash
python testscript/test_conversion.py
```

### How to Validate the Results

The test script will print the results of each test case to the console. Here's what to look for:

*   **`Test PASSED`**: This indicates that the test case completed successfully. The conversion job was created, and it finished with a "verified" or "success" status (for text-based conversions) or a "completed" status (for file-based conversions).

*   **`Test FAILED`**: This indicates that the test case failed. The script will print additional information about the failure, such as the job status, error message, or the HTTP error that occurred.

By reviewing the output of the test script, you can quickly determine if the conversion functionality is working as expected.

### Extending the Tests

To make the test suite more comprehensive, you can:

*   Add more complex Oracle stored procedures and DDLs to the `sql-assests` folder.
*   Create new test functions in `test_conversion.py` to test these new files.
*   Modify the existing test functions to include more assertions, such as comparing the converted SQL with a known-correct output.
