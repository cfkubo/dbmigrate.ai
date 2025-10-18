import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import * as apiClient from './api_client';
import {
  Box,
  TextField,
  Button,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  Paper
} from '@mui/material';
import './ConnectionDetails.css';

function ConnectionDetails() {
  const { dbType } = useParams(); // 'oracle' or 'postgresql'
  const navigate = useNavigate(); // Initialize navigate
  const [host, setHost] = useState('');
  const [port, setPort] = useState('');
  const [user, setUser] = useState('');
  const [password, setPassword] = useState('');
  const [serviceOrSid, setServiceOrSid] = useState(''); // For Oracle
  const [connectionType, setConnectionType] = useState('Service Name'); // For Oracle
  const [dbName, setDbName] = useState(''); // For PostgreSQL
  const [database, setDatabase] = useState(''); // For DB2
  const [hostname, setHostname] = useState(''); // For DB2
  const [protocol, setProtocol] = useState('TCPIP'); // For DB2
  const [uid, setUid] = useState(''); // For DB2
  const [pwd, setPwd] = useState(''); // For DB2
  const [connectionStatus, setConnectionStatus] = useState('');

  useEffect(() => {
    // Fetch default connection details based on dbType
    const fetchDefaultDetails = async () => {
      try {
        const defaults = await apiClient.getDefaultConnectionDetails(dbType);
        setHost(defaults.host || '');
        setPort(defaults.port || '');
        setUser(defaults.user || '');
        setPassword(defaults.password || '');
        if (dbType === 'oracle') {
          setServiceOrSid(defaults.service_name || defaults.sid || '');
          setConnectionType(defaults.service_name ? 'Service Name' : 'SID');
        } else if (dbType === 'postgresql') {
          setDbName(defaults.dbname || '');
        } else if (dbType === 'mysql') {
          setDbName(defaults.database || '');
        } else if (dbType === 'sqlserver') {
          setDbName(defaults.database || '');
        } else if (dbType === 'teradata') {
          setHost(defaults.host || '');
          setUser(defaults.user || '');
          setPassword(defaults.password || '');
        } else if (dbType === 'db2') {
          setDatabase(defaults.database || '');
          setHostname(defaults.hostname || '');
          setPort(defaults.port || '');
          setProtocol(defaults.protocol || '');
          setUid(defaults.uid || '');
          setPwd(defaults.pwd || '');
        }
      } catch (error) {
        console.error("Error fetching default connection details:", error);
        setConnectionStatus(`Error loading defaults: ${error.message}`);
      }
    };
    fetchDefaultDetails();
  }, [dbType]);

  const handleConnect = async () => {
    setConnectionStatus('Connecting...');
    try {
      let response;
      let currentConnectionDetails;

      if (dbType === 'oracle') {
        currentConnectionDetails = {
          host,
          port: parseInt(port),
          user,
          password,
        };
        if (connectionType === 'Service Name') {
          currentConnectionDetails.service_name = serviceOrSid;
        } else {
          currentConnectionDetails.sid = serviceOrSid;
        }
        response = await apiClient.connectToOracle(currentConnectionDetails);
      } else if (dbType === 'postgresql') {
        currentConnectionDetails = {
          host,
          port: parseInt(port),
          user,
          password,
          dbname: dbName,
        };
        response = await apiClient.testPostgresConnection(currentConnectionDetails);
      } else if (dbType === 'mysql') {
        currentConnectionDetails = {
          host,
          port: parseInt(port),
          user,
          password,
          database: dbName,
        };
        response = await apiClient.connectToMySql(currentConnectionDetails);
      } else if (dbType === 'sqlserver') {
        currentConnectionDetails = {
          host,
          port: parseInt(port),
          user,
          password,
          database: dbName,
        };
        response = await apiClient.connectToSqlServer(currentConnectionDetails);
      } else if (dbType === 'teradata') {
        currentConnectionDetails = {
          host,
          user,
          password,
        };
        response = await apiClient.connectToTeradata(currentConnectionDetails);
      } else if (dbType === 'db2') {
        currentConnectionDetails = {
          database,
          hostname,
          port: parseInt(port),
          protocol,
          uid,
          pwd,
        };
        response = await apiClient.connectToDb2(currentConnectionDetails);
      }
      setConnectionStatus(`Connected! ${response.message || 'Successfully connected.'}`);
      
      // Navigate to the migration workflow, passing connection details as state
      navigate('/migrate', { state: { sourceDbType: dbType, sourceConnectionDetails: currentConnectionDetails } });

    } catch (error) {
      setConnectionStatus(`Error: ${error.message}`);
    }
  };

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
      <Paper elevation={3} sx={{ maxWidth: 600, width: '100%', p: 4 }}>
        <Typography variant="h4" gutterBottom>
          {dbType.charAt(0).toUpperCase() + dbType.slice(1)} Connection Details
        </Typography>

        <Box component="form" sx={{ '& .MuiTextField-root': { my: 1 } }}>
          {dbType !== 'db2' && (
            <>
              <TextField
                fullWidth
                label="Host"
                value={host}
                onChange={(e) => setHost(e.target.value)}
                margin="normal"
              />

              {dbType !== 'teradata' && (
                <TextField
                  fullWidth
                  label="Port"
                  type="number"
                  value={port}
                  onChange={(e) => setPort(e.target.value)}
                  margin="normal"
                />
              )}

              <TextField
                fullWidth
                label="User"
                value={user}
                onChange={(e) => setUser(e.target.value)}
                margin="normal"
              />

              <TextField
                fullWidth
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                margin="normal"
              />
            </>
          )}

          {dbType === 'oracle' && (
            <>
              <FormControl fullWidth margin="normal">
                <InputLabel>Connection Type</InputLabel>
                <Select
                  value={connectionType}
                  onChange={(e) => setConnectionType(e.target.value)}
                  label="Connection Type"
                >
                  <MenuItem value="Service Name">Service Name</MenuItem>
                  <MenuItem value="SID">SID</MenuItem>
                </Select>
              </FormControl>

              <TextField
                fullWidth
                label={connectionType}
                value={serviceOrSid}
                onChange={(e) => setServiceOrSid(e.target.value)}
                margin="normal"
              />
            </>
          )}

          {(dbType === 'postgresql' || dbType === 'mysql' || dbType === 'sqlserver') && dbType !== 'teradata' && (
            <TextField
              fullWidth
              label="Database Name"
              value={dbName}
              onChange={(e) => setDbName(e.target.value)}
              margin="normal"
            />
          )}

          {dbType === 'db2' && (
            <>
              <TextField
                fullWidth
                label="Database"
                value={database}
                onChange={(e) => setDatabase(e.target.value)}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Hostname"
                value={hostname}
                onChange={(e) => setHostname(e.target.value)}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Port"
                type="number"
                value={port}
                onChange={(e) => setPort(e.target.value)}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Protocol"
                value={protocol}
                onChange={(e) => setProtocol(e.target.value)}
                margin="normal"
              />
              <TextField
                fullWidth
                label="User ID"
                value={uid}
                onChange={(e) => setUid(e.target.value)}
                margin="normal"
              />
              <TextField
                fullWidth
                label="Password"
                type="password"
                value={pwd}
                onChange={(e) => setPwd(e.target.value)}
                margin="normal"
              />
            </>
          )}

          <Box sx={{ mt: 3 }}>
            <Button
              variant="contained"
              color="primary"
              onClick={handleConnect}
              fullWidth
              disabled={connectionStatus === 'Connecting...'}
            >
              {connectionStatus === 'Connecting...' ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                'Connect'
              )}
            </Button>
          </Box>

          {connectionStatus && (
            <Box sx={{ mt: 2 }}>
              <Alert 
                severity={connectionStatus.includes('Error') ? 'error' : 
                         connectionStatus === 'Connecting...' ? 'info' : 'success'}
              >
                {connectionStatus}
              </Alert>
            </Box>
          )}
        </Box>
      </Paper>
    </Box>
  );
}

export default ConnectionDetails;