 To ensure a robust fix, perform a very clean restart:
   1. Stop FastAPI.
   2. Stop Gradio UI (`app.py`).
   3. Verify both are stopped (check http://127.0.0.1:8000/health and Gradio UI URL).
   4. Clear Python bytecode caches: find . -name "__pycache__" -exec rm -rf {} + and find . -name "*.pyc" -exec rm -f {} +.
   5. Restart FastAPI: uvicorn api.main:app --reload. Verify http://127.0.0.1:8000/health returns {"status": "ok"}.
   6. Restart Gradio UI: python app.py.

  Then, test in this order:
   1. "All Jobs" tab: Check dropdown population.
   2. Single DDL text conversion.
   3. Single Stored Proc text conversion.
   4. Bulk DDL file upload.
   5. Bulk Stored Proc file upload.
