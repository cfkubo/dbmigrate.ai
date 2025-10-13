import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom'; // Import useNavigate
import * as apiClient from './api_client';
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
      }
      setConnectionStatus(`Connected! ${response.message || 'Successfully connected.'}`);
      
      // Navigate to the migration workflow, passing connection details as state
      navigate('/migrate', { state: { sourceDbType: dbType, sourceConnectionDetails: currentConnectionDetails } });

    } catch (error) {
      setConnectionStatus(`Error: ${error.message}`);
    }
  };

  return (
    <div className="connection-details-container">
      <h2>{dbType.charAt(0).toUpperCase() + dbType.slice(1)} Connection Details</h2>
      <div className="form-group">
        <label>Host:</label>
        <input type="text" value={host} onChange={(e) => setHost(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Port:</label>
        <input type="number" value={port} onChange={(e) => setPort(e.target.value)} />
      </div>
      <div className="form-group">
        <label>User:</label>
        <input type="text" value={user} onChange={(e) => setUser(e.target.value)} />
      </div>
      <div className="form-group">
        <label>Password:</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      </div>

      {dbType === 'oracle' && (
        <div className="form-group">
          <label>Connection Type:</label>
          <select value={connectionType} onChange={(e) => setConnectionType(e.target.value)}>
            <option value="Service Name">Service Name</option>
            <option value="SID">SID</option>
          </select>
          <label>{connectionType}:</label>
          <input type="text" value={serviceOrSid} onChange={(e) => setServiceOrSid(e.target.value)} />
        </div>
      )}

      {dbType === 'postgresql' && (
        <div className="form-group">
          <label>Database Name:</label>
          <input type="text" value={dbName} onChange={(e) => setDbName(e.target.value)} />
        </div>
      )}

      <button onClick={handleConnect}>Connect</button>
      <p className="connection-status">{connectionStatus}</p>
    </div>
  );
}

export default ConnectionDetails;