# Connecting to Oracle XE with SQLDeveloper

This guide provides instructions on how to connect to the Oracle XE database running in a Docker container managed by Colima.

## Connection Parameters

Here are the parameters you need to connect to the Oracle database. These values are configured in your `.env` file.

*   **Hostname:** The IP address of your Colima instance. You can find this in your `.env` file as `ORACLE_HOST`.
*   **Port:** The port number for the Oracle listener. The default is `1521`. This is `ORACLE_PORT` in your `.env` file.
*   **Username:** The database username. The default admin user is `SYSTEM`. This is `ORACLE_USER` in your `.env` file.
*   **Password:** The password for the database user. This is `ORACLE_PASSWORD` in your `.env` file.
*   **Connection Type:** You can connect using either a **Service Name** or a **SID**. For the `gvenzl/oracle-xe` container, it is recommended to use **Service Name**.

### Using Service Name (Recommended)

*   **Service Name:** The service name for the pluggable database. For `gvenzl/oracle-xe`, the default is `FREEPDB1`. This is `ORACLE_SERVICE_NAME` in your `.env` file.

### Using SID

*   **SID:** The System ID for the database instance. For `gvenzl/oracle-xe`, the default is `XE`. This is `ORACLE_SID` in your `.env` file.

## SQLDeveloper Connection Steps

1.  **Open SQLDeveloper** and click the "New Connection" button (the green plus icon).
2.  **Enter a Connection Name:** Choose a descriptive name for your connection (e.g., "Oracle XE on Colima").
3.  **Enter the Username and Password:** Use the values from your `.env` file.
4.  **Choose the Connection Type:** Select "Basic".
5.  **Enter the Hostname and Port:** Use the values from your `.env` file.
6.  **Select either "Service Name" or "SID"** and enter the corresponding value from your `.env` file. It is recommended to use "Service Name".
7.  **Click "Test"** to verify the connection.
8.  **Click "Save"** to save the connection.
9.  **Click "Connect"** to open the connection.

## Troubleshooting

*   **Connection Refused:** This usually means the hostname or port is incorrect, or the Oracle container is not running. Double-check the IP address of your Colima instance and ensure the Oracle container is running.
*   **Invalid Username/Password:** Make sure you are using the correct username and password from your `.env` file.
*   **Listener Refuses Connection (ORA-12514):** This often means you are using the wrong Service Name or SID. For `gvenzl/oracle-xe`, the service name is `FREEPDB1` and the SID is `XE`.
