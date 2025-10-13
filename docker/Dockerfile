# Use the native ARM64-compatible Oracle Database Free image (23c) as the base.
# 'gvenzl/oracle-free:latest' is a multi-platform image that pulls the ARM64 version.
FROM gvenzl/oracle-free:latest

# Set the desired Oracle password. 
# ⚠️ Make sure to use a strong password (8+ chars, mixed case, number, special char).
ENV ORACLE_PASSWORD=your_secure_password

# Copy SQL scripts to be executed during container initialization.
# COPY create-schema.sql /container-initdb.d/

# Expose the default Oracle listener port
EXPOSE 1521