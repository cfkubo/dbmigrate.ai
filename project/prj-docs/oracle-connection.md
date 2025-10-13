# Connecting to Your Oracle Database Container

This guide provides detailed instructions on how to connect to the Oracle database running in your Docker container.

### 1. Running the Database Container

First, ensure the container is running. You can start it with the following command:

```bash
docker run -d --name=oracle-free -p 1521:1521 -e ORACLE_PASSWORD=password gvenzl/oracle-xe
```

*   `--name=oracle-free`: Gives the container the name `oracle-free`.
*   `-p 1521:1521`: Maps port 1521 on your host to port 1521 in the container.
*   `-e ORACLE_PASSWORD=password`: Sets the password for the `SYS` and `SYSTEM` users to `password`.

### 2. Finding Your Service Name

The Service Name is a key part of the connection string. You can find the available service names by checking the listener status inside the container.

*   **Command:**
    ```bash
    docker exec oracle-free lsnrctl status
    ```
*   **Example Output:**
    ```
    Services Summary...
    Service "XE" has 1 instance(s).
    Service "freepdb1" has 1 instance(s).
    ```

Based on this output, you can use either `XE` or `freepdb1` as your service name.

### 3. Connecting via Command Line (CLI)

You can connect to the database using the `sqlplus` command-line tool, which is included in the Docker image.

*   **Connecting as SYSTEM:**
    ```bash
    docker exec -it oracle-free sqlplus system/password@//<hostname>:1521/XE
    ```
*   **Connecting as SYS (Super-Administrator):**
    If you have trouble connecting as `SYSTEM`, you can connect as `SYS`. This requires the `as sysdba` clause.
    ```bash
    docker exec -it oracle-free sqlplus sys/password@//<hostname>:1521/XE as sysdba
    ```

### 4. Connecting with SQL Developer

*   **Connection Name:** A descriptive name, like "Oracle XE Docker".
*   **Username:** `system` (or `sys`)
*   **Password:** `password` (the one you set).
*   **Role:** If connecting as `sys`, change the role to `SYSDBA`.
*   **Connection Type:** `Basic`
*   **Hostname:** `localhost` (or the IP from `colima` if you are on a Mac with Apple Silicon).
*   **Port:** `1521`
*   **Service Name:** `XE`

### 5. Creating a New User

Once you are connected as `SYS`, you can create new users.

1.  **Connect as SYS:**
    ```bash
    docker exec -it oracle-free sqlplus sys/password as sysdba
    ```
2.  **Create the new user:**
    Replace `newuser` and `password` with your desired username and password.
    ```sql
    CREATE USER newuser IDENTIFIED BY password;
    ```
3.  **Grant privileges to the new user:**
    The `DBA` role grants full privileges.
    ```sql
    GRANT DBA TO newuser;
    ```

### 6. Troubleshooting

#### ORA-01017: invalid username/password; logon denied

This error means the credentials are incorrect.

*   **Password Mismatch:** The `ORACLE_PASSWORD` is only set when the container is **first created**.
*   **Connecting as SYS:** When connecting as `sys`, you **must** use the `as sysdba` clause.

#### If You Still Can't Connect: Reset the Database

If you are completely locked out, you can reset the database by recreating the container. **This will delete all data.**

1.  **Stop and remove the container and volume:**
    ```bash
    docker stop oracle-free
    docker rm oracle-free
    docker volume rm oracle-volume
    ```
2.  **Start a new container:**
    ```bash
    docker run -d --name=oracle-free -p 1521:1521 -e ORACLE_PASSWORD=password -v oracle-volume:/opt/oracle/oradata gvenzl/oracle-xe
    ```

### Important Notes:

*   **Mac with Apple Silicon (M1/M2/M3):** If you are using a Mac with an Apple Silicon chip, the **Hostname** will not be `localhost`, but the IP address of the `colima` VM.