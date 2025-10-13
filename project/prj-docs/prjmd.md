        ### Oracle to PostgreSQL Converter

        This tool is designed to facilitate the conversion of Oracle SQL syntax to PostgreSQL syntax, including support for stored procedures, functions, and DDL statements. It also includes a data migration feature to transfer data from Oracle to PostgreSQL databases.
        
        ## 1. Project Plan & Purpose

        **Primary Goal:** The main objective of this project is to provide a tool that can convert stored procedures and functions from an Oracle SQL dialect to a PostgreSQL compatible dialect.

        **Key Features:**
        1.  **Web UI:** A user-friendly web interface for converting SQL code by pasting it into a text box or uploading a file. It supports both Stored Procedures/Functions and DDL.
        2.  **Web API:** Provides a web-accessible endpoint to perform conversions, allowing integration with other applications or web frontends. It has separate endpoints for Stored Procedures/Functions and DDL.
        3.  **Asynchronous Conversion:** The conversion process is handled asynchronously, so users don't have to wait for the conversion to complete.
        4.  **Verification and Self-Correction:** The converted SQL is verified against a PostgreSQL database, and if it fails, the tool attempts to self-correct the SQL using the LLM.
        5.  **Job Management:** Users can view the status of their conversion jobs, including pending, processing, verified, and failed jobs.
        6.  **Data Migration:** A feature to migrate data from Oracle tables to PostgreSQL tables.
        7.  **Project Architecture Diagram:** A visual representation of the project's architecture, illustrating the flow of data and interactions between components. 
        8.  **DDL Extraction:** Connect to an Oracle database, extract DDL for selected schemas and object types, and convert the extracted DDL to PostgreSQL syntax.
        9.  **Job Tracking:** Store job information in a SQLite database and track migration status using Redis.
        10. **LLM Integration:** Use Ollama LLM for SQL conversion tasks.       

        **Target User:** Database administrators and developers who are migrating a database from Oracle to PostgreSQL.
        **Motivation:** The motivation behind this project is to simplify the often complex and error-prone process of migrating databases between different SQL dialects, specifically from Oracle to PostgreSQL. By leveraging AI and automation, the tool aims to reduce manual effort and increase accuracy in the conversion process.

        #### Technologies Used:
        - Gradio for the web interface.
        - FastAPI for the backend API.
        - RabbitMQ for job queueing.
        - Redis for status tracking. (not yet implemented)
        - oracledb and psycopg2 for database connections.

        #### Note:
        This project is experimental and may not cover all edge cases in SQL conversion. Please review converted SQL before use in production environments.
                    
        #### Future Improvements:
        - Enhance SQL conversion accuracy. (working: added sql verification)
        - Add support for more Oracle features. (in progress: supports ddl, sp, functions, tables, indexes, views, triggers, packages)
        - Improve user interface and experience. (mvp in place)
        - Implement authentication and security features. (not yet implemented)
        - Add more robust error handling and logging. (basic in place: need to improve)
        - Implement Redis for tracking migration status. (not yet implemented: should we use rabbitmq for this?)
        - Add support for more database systems. (Is it worth it?)
        - Containerize the application using Docker. (not yet implemented)
        - Deploy the application to a kubernetes cluster. (not yet implemented)
        - Add AI Query Optimizer for psql
        - Enable as MCP Server and MCP tools
        - Guidance on Data Migration from Oracle to Postgres -  This should be outsourced to ETL like tool.  

        For more information, visit the [GitHub Repository](https://github.com/akv-dev/spf-converter).

        ### Project Architecture Diagram
                    +---------------------+      +---------------------+
                    |    User (CLI)       |      |  User (API Client)  |
                    +-----------+---------+      +-----------+---------+
                                |                          |
                                |                          | HTTP Request (SQL String)
                                v                          v
                    ./gini.sh --[runs]--> +----------------------------+
                                |         |       api/main.py          |
                                v         | (Web Server/ASGI & Producer)|
                    +---------------------+ +----------------------------+
                    |     app.py          |             |
                    | (CLI Interface)     |             | 3. Creates/updates job status
                    +-----------+---------+             v
                                |             +----------------------------+
                                |             |   jobs.db (SQLite)         |
                                |             | (Persistent Job Tracking)  |
                                |             +-------------+--------------+
                                |                           |
                                +------------>--------------+  (Also via api/main.py)
                                |                           |
                                |                           v
                                |             +----------------------------+
                                |             |        RabbitMQ            |
                                |             |   (Message Broker)         |
                                +-----------> +-------------+--------------+
                                            |             |
                            2. Publishes jobs from api/main.py & app.py |
                                            |             | 4. Consumes jobs from
                                            |             v
                                            +----------------------------+
                                            |        Workers             |
                                            | (Multiple worker.py instances)|
                                            +-----------+----------------+
                                                        |
                                                        | 5. Converts SQL using
                                                        v
                                            +----------------------------+
                                            |         Ollama LLM         |
                                            |     (External Service)     |
                                            +-----------+----------------+
                                                        |
                                                        | 6. Verifies SQL against
                                                        v
                                            +----------------------------+
                                            |     PostgreSQL (Output)    |
                                            |   (for Verification)       |
                                            +-----------+----------------+
                                                        |
                                                        | 7. Publishes results back to
                                                        v
                                            +----------------------------+
                                            |        RabbitMQ            |
                                            |   (Message Broker)         |
                                            +-----------+----------------+
                                                        |
                            8. Consumes results from (Result Collector)  |
                                                        v
                                            +----------------------------+
                                            |    Result Collector        |
                                            | (Async Result Consumer)    |
                                            +-----------+----------------+
                                                        |
                                                        | 9. Updates final status in
                                                        v
                                            +----------------------------+
                                            |   jobs.db (SQLite)         |
                                            | (Persistent Job Tracking)  |
                                            +----------------------------+