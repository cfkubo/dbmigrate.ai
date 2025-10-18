const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

async function callApi(endpoint, method = 'GET', data = null) {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  };
  if (data) {
    options.body = JSON.stringify(data);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
  const responseData = await response.json();

  if (!response.ok) {
    throw new Error(responseData.detail || 'Something went wrong');
  }
  return responseData;
}

export const connectToOracle = async (connectionDetails) => {
  return callApi('/api/oracle/connect', 'POST', connectionDetails);
};

export const connectToMySql = async (connectionDetails) => {
  return callApi('/api/mysql/connect', 'POST', connectionDetails);
};

export const connectToSqlServer = async (connectionDetails) => {
  return callApi('/api/sqlserver/connect', 'POST', connectionDetails);
};

export const connectToTeradata = async (connectionDetails) => {
  return callApi('/api/teradata/connect', 'POST', connectionDetails);
};

export const connectToDb2 = async (connectionDetails) => {
  return callApi('/api/db2/connect', 'POST', connectionDetails);
};

export const listOracleObjects = async (connectionDetails, schema, objectType) => {
  return callApi('/api/oracle/list-objects', 'POST', { connection_details: connectionDetails, schema_name: schema, object_type: objectType });
};

export const testPostgresConnection = async (connectionDetails) => {
  return callApi('/api/test-postgres-connection', 'POST', connectionDetails);
};

export const startMigration = async (migrationDetails) => {
  return callApi('/api/migrate', 'POST', migrationDetails);
};

export const getDefaultConnectionDetails = async (dbType) => {
  return callApi(`/api/default-connection-details/${dbType}`);
};

export const getMigrationStatus = async (jobId) => {
  return callApi(`/api/migration/status/${jobId}`);
};
