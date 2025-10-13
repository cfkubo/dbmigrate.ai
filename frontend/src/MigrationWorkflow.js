import React, { useState, useEffect, useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router-dom'; // Import useLocation and useNavigate
// import './DatabaseSelection.css'; // This CSS will be removed or refactored
import * as apiClient from './api_client';
import ObjectSelection from './ObjectSelection';
import ObjectTypeSelector from './ObjectTypeSelector'; // Import the new component
import './MigrationWorkflow.css';

function MigrationWorkflow() {
  const location = useLocation();
  const navigate = useNavigate(); // Initialize useNavigate
  const { sourceDbType, sourceConnectionDetails } = location.state || {};

  // For now, target is hardcoded to PostgreSQL. In a full flow, this would be selected.
  const targetDbType = 'postgresql';
  // Placeholder for target connection details, which would come from a previous step
  const targetConnectionDetails = useMemo(() => ({
    host: process.env.REACT_APP_POSTGRES_DB_HOST || 'localhost',
    port: parseInt(process.env.REACT_APP_POSTGRES_DB_PORT || '5432'),
    user: process.env.REACT_APP_POSTGRES_DB_USER || 'postgres',
    password: process.env.REACT_APP_POSTGRES_DB_PASSWORD || 'postgres',
    dbname: process.env.REACT_APP_POSTGRES_DB_NAME || 'postgres',
  }), []); // Empty dependency array as env variables are static

  // State for source database (now received via props/context)
  const [sourceSchemas, setSourceSchemas] = useState([]);
  const [selectedSourceSchema, setSelectedSourceSchema] = useState('');
  const [sourceObjectTypes] = useState(['TABLE', 'PROCEDURE', 'FUNCTION', 'VIEW', 'PACKAGE', 'INDEX', 'TRIGGER']); // Removed setSourceObjectTypes
  const [selectedObjectType, setSelectedObjectType] = useState('TABLE');
  const [oracleObjects, setOracleObjects] = useState([]);
  const [objectListingStatus, setObjectListingStatus] = useState('');
  const [selectedObjectsForMigration, setSelectedObjectsForMigration] = useState([]);

  // State for target database (now received via props/context)
  const [targetConnectionStatus, setTargetConnectionStatus] = useState('');

  useEffect(() => {
    if (!sourceDbType || !sourceConnectionDetails) {
      // Handle case where state is not available (e.g., direct access to /migrate)
      // You might want to redirect to home or show an error
      console.error("Source database type or connection details not found in state.");
      return;
    }

    if (sourceConnectionDetails && sourceDbType === 'oracle') {
      const fetchSchemas = async () => {
        try {
          const response = await apiClient.connectToOracle(sourceConnectionDetails);
          setSourceSchemas(response.schemas);
          // Removed automatic selection of the first schema. The dropdown will default to the first option, but user selection will be respected.
        } catch (error) {
          console.error("Error fetching schemas:", error);
        }
      };
      fetchSchemas();
    }

    if (targetConnectionDetails && targetDbType === 'postgresql') {
      const testTarget = async () => {
        try {
          const response = await apiClient.testPostgresConnection(targetConnectionDetails);
          setTargetConnectionStatus(`Connected! ${response.message}`);
        } catch (error) {
          setTargetConnectionStatus(`Error: ${error.message}`);
        }
      };
      testTarget();
    }
  }, [sourceConnectionDetails, sourceDbType, targetConnectionDetails, targetDbType]);

  const handleListOracleObjects = async () => {
    setObjectListingStatus('Listing objects...');
    try {
      const response = await apiClient.listOracleObjects(sourceConnectionDetails, selectedSourceSchema, selectedObjectType);
      setOracleObjects(response.objects);
      setObjectListingStatus(`Found ${response.objects.length} ${selectedObjectType}(s) in ${selectedSourceSchema}.`);
    } catch (error) {
      setObjectListingStatus(`Error listing objects: ${error.message}`);
    }
  };

  const handleObjectSelection = (selected) => {
    setSelectedObjectsForMigration(selected);
  };

  const handleBuildPipelines = () => {
    if (!selectedSourceSchema || selectedObjectsForMigration.length === 0) {
      alert('Please select a schema, list objects, and select at least one object for migration.');
      return;
    }
    if (!targetConnectionStatus.startsWith('Connected')) {
      alert('Please ensure PostgreSQL connection is successful.');
      return;
    }

    const migrationDetails = {
      source_db_type: sourceDbType,
      target_db_type: targetDbType,
      source_connection: sourceConnectionDetails,
      target_connection: targetConnectionDetails,
      source_schema: selectedSourceSchema,
      target_schema: targetConnectionDetails.dbname, // Assuming target schema is the same as target dbname for now
      selected_objects: selectedObjectsForMigration.map(objName => ({ object_type: selectedObjectType, object_name: objName })),
      data_migration_enabled: false, // Set to false as per user request
    };

    navigate('/migration-pipelines', { state: { migrationDetails } });
  };

  const isButtonDisabled = !selectedSourceSchema || objectListingStatus.startsWith('Error') || !targetConnectionStatus.startsWith('Connected') || oracleObjects.length === 0 || selectedObjectsForMigration.length === 0;

  return (
    <div className="migration-workflow-container">
      <h2>Migration Workflow</h2>

      {/* Source Database Details (Oracle) - Simplified */}
      <div className="selection-group">
        <label>Source Database: {sourceDbType ? sourceDbType.charAt(0).toUpperCase() + sourceDbType.slice(1) : 'N/A'}</label>
        {sourceConnectionDetails && <p>Connected to {sourceConnectionDetails.host}:{sourceConnectionDetails.port}</p>}
      </div>

      {sourceSchemas.length > 0 && (
        <div className="selection-group">
          <label htmlFor="source-schema">Select Schema:</label>
          <select id="source-schema" value={selectedSourceSchema} onChange={(e) => setSelectedSourceSchema(e.target.value)}>
            {sourceSchemas.map((schema) => (
              <option key={schema} value={schema}>{schema}</option>
            ))}
          </select>
        </div>
      )}
      {selectedSourceSchema && (
        <div className="selection-group">
          <label>Object Type:</label>
          <ObjectTypeSelector
            objectTypes={sourceObjectTypes}
            selectedObjectType={selectedObjectType}
            onSelectObjectType={setSelectedObjectType}
          />
          <button onClick={handleListOracleObjects}>List Objects</button>
          <p className="connection-status">{objectListingStatus}</p>
        </div>
      )}

      {/* Target Database Details (PostgreSQL) - Simplified */}
      <div className="selection-group">
        <label>Target Database: {targetDbType.charAt(0).toUpperCase() + targetDbType.slice(1)}</label>
        {targetConnectionDetails && <p>Connected to {targetConnectionDetails.host}:{targetConnectionDetails.port}</p>}
        <p className="connection-status">Target Status: {targetConnectionStatus}</p>
      </div>

      {oracleObjects.length > 0 && (
        <ObjectSelection
          objects={oracleObjects}
          selectedObjectType={selectedObjectType}
          onObjectSelect={handleObjectSelection}
        />
      )}

      <button onClick={handleBuildPipelines} disabled={isButtonDisabled}>
        Build Pipelines for Migration
      </button>
    </div>
  );
}

export default MigrationWorkflow;
