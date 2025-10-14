import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import * as apiClient from './api_client';
import './MigrationPipelines.css';
function MigrationPipelines() {
  const location = useLocation();
  const { migrationDetails } = location.state || {};
  const [migrationJobId, setMigrationJobId] = useState(null);
  const [pipelineStatus, setPipelineStatus] = useState({}); // Stores status for each object
  const [isMigrationRunning, setIsMigrationRunning] = useState(false);
  const [overallMigrationStatus, setOverallMigrationStatus] = useState('pending'); // overall status of the parent job
  const [overallErrorMessage, setOverallErrorMessage] = useState(null);
  const [expandedDdlJobId, setExpandedDdlJobId] = useState(null); // State to track expanded DDL
  useEffect(() => {
    if (!migrationDetails) {
      setOverallErrorMessage("No migration details found. Please go back and select objects.");
    }
  }, [migrationDetails]);
  useEffect(() => {
    let intervalId = null;
    const fetchMigrationStatus = async () => {
      try {
        const statusResponse = await apiClient.getMigrationStatus(migrationJobId);
        console.log("Fetched migration status:", statusResponse);
        setOverallMigrationStatus(statusResponse.status);
        setOverallErrorMessage(statusResponse.error_message);
        const newPipelineStatus = {};
        statusResponse.child_jobs.forEach(childJob => {
          const objectKey = `${childJob.object_type}_${childJob.object_name}`;
          newPipelineStatus[objectKey] = {
            overall: childJob.status,
            extraction: childJob.extraction_status || 'pending',
            conversion: childJob.conversion_status || 'pending',
            execution: childJob.execution_status || 'pending',
            data_migration: childJob.data_migration_status || 'pending',
            error_message: childJob.error_message || null,
            converted_ddl: childJob.converted_ddl || null,
            original_sql: childJob.original_sql || null,
            job_id: childJob.job_id, // Store job_id for expansion
          };
        });
        setPipelineStatus(newPipelineStatus);
        if (statusResponse.status === 'completed' || statusResponse.status === 'failed') {
          setIsMigrationRunning(false);
        }
      } catch (error) {
        console.error("Error fetching migration status:", error);
        setOverallErrorMessage(`Failed to fetch migration status: ${error.message}`);
        setIsMigrationRunning(false);
      }
    };
    if (isMigrationRunning && migrationJobId) {
      const pollStatus = async () => {
        await fetchMigrationStatus();
      };
      intervalId = setInterval(pollStatus, 3000);
    }
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [isMigrationRunning, migrationJobId, setIsMigrationRunning]);
  const handleKickoffMigration = async () => {
    if (!migrationDetails) return;
    setIsMigrationRunning(true);
    setOverallMigrationStatus('processing');
    setOverallErrorMessage(null);
    // Initialize pipeline status for display
    const initialPipelineStatus = {};
    migrationDetails.selected_objects.forEach(obj => {
      const objectKey = `${obj.object_type}_${obj.object_name}`;
      initialPipelineStatus[objectKey] = {
        overall: 'pending',
        extraction: 'pending',
        conversion: 'pending',
        execution: 'pending',
        data_migration: 'pending',
        error_message: null,
        converted_ddl: null,
        original_sql: null, // Will be updated once job is created
      };
    });
    setPipelineStatus(initialPipelineStatus);
    try {
      const response = await apiClient.startMigration(migrationDetails);
      setMigrationJobId(response.job_id);
      alert(`Migration initiated! Job ID: ${response.job_id}`);
      // Start polling immediately after getting job ID
      // fetchMigrationStatus(); // Initial fetch
    } catch (error) {
      console.error("Error initiating migration:", error);
      setOverallErrorMessage(`Failed to initiate migration: ${error.message}`);
      setIsMigrationRunning(false);
      setOverallMigrationStatus('failed');
    }
  };
  const getStatusClass = (status) => {
    if (status === 'processing') return 'status-processing';
    if (status === 'success' || status === 'verified' || status === 'extracted') return 'status-success';
    if (status === 'failed') return 'status-failed';
    if (status === 'skipped') return 'status-skipped';
    return 'status-pending';
  };
  const toggleDdlExpansion = (jobId) => {
    setExpandedDdlJobId(expandedDdlJobId === jobId ? null : jobId);
  };
  if (!migrationDetails && !overallErrorMessage) {
    return (
      <div className="migration-pipelines-container">
        <h2>Loading Migration Details...</h2>
      </div>
    );
  }
  return (
    <div className="migration-pipelines-container">
      <h2>Migration Pipelines Overview</h2>
      {overallErrorMessage && <p className="error-message">Error: {overallErrorMessage}</p>}
      <p>Overall Status: <span className={`overall-status ${overallMigrationStatus}`}>{overallMigrationStatus.toUpperCase()}</span></p>
      <div className="migration-summary">
        <h3>Source: {migrationDetails?.source_db_type} ({migrationDetails?.source_schema})</h3>
        <h3>Target: {migrationDetails?.target_db_type} ({migrationDetails?.target_schema})</h3>
        <p>Data Migration Enabled: {migrationDetails?.data_migration_enabled ? 'Yes' : 'No'}</p>
      </div>
      <h3>Objects to Migrate:</h3>
      <div className="migration-objects-table-container">
        <table className="migration-objects-table">
          <thead>
            <tr>
              <th>Object Type</th>
              <th>Object Name</th>
              <th>Original SQL</th>
              <th>Data Migration</th>
              <th>Overall Status</th>
              <th>Error</th>
              <th>Converted DDL</th>
            </tr>
          </thead>
          <tbody>
            {migrationDetails?.selected_objects.map((obj, index) => {
              const objectKey = `${obj.object_type}_${obj.object_name}`;
              const objStatus = pipelineStatus[objectKey] || {};
              const isExpanded = expandedDdlJobId === objStatus.job_id;
              return (
                <React.Fragment key={index}>
                  <tr>
                    <td>{obj.object_type}</td>
                    <td>{obj.object_name}</td>
                    <td>
                      {objStatus.original_sql ? (
                        <div className="ddl-preview-cell">
                          <pre>{objStatus.original_sql.substring(0, 100)}...</pre>
                          <button className="view-ddl-button" onClick={() => toggleDdlExpansion(objStatus.job_id)}>
                            {isExpanded ? 'Hide SQL' : 'View SQL'}
                          </button>
                        </div>
                      ) : '-'}
                    </td>
                    <td className={getStatusClass(obj.object_type === 'TABLE' && migrationDetails.data_migration_enabled ? objStatus.data_migration : 'skipped')}>
                      {obj.object_type === 'TABLE' && migrationDetails.data_migration_enabled ? (objStatus.data_migration || 'pending') : 'skipped'}
                    </td>
                    <td className={getStatusClass(objStatus.overall)}>{objStatus.overall || 'pending'}</td>
                    <td className="error-cell">{objStatus.error_message || '-'}
                    </td>
                    <td>
                      {objStatus.converted_ddl ? (
                        <div className="ddl-preview-cell">
                          <pre>{objStatus.converted_ddl.substring(0, 100)}...</pre>
                          <button className="view-ddl-button" onClick={() => toggleDdlExpansion(objStatus.job_id)}>
                            {isExpanded ? 'Hide DDL' : 'View DDL'}
                          </button>
                        </div>
                      ) : '-'}
                    </td>
                  </tr>
                  {isExpanded && (
                    <tr>
                      <td colSpan="7" className="expanded-ddl-content">
                        <h4>Full DDL for {obj.object_name}:</h4>
                        <pre>{objStatus.original_sql || objStatus.converted_ddl}</pre>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
      <button
        className="kickoff-migration-button"
        onClick={handleKickoffMigration}
        disabled={isMigrationRunning || overallMigrationStatus === 'processing'}
      >
        {isMigrationRunning || overallMigrationStatus === 'processing' ? 'Migration In Progress...' : 'Kickoff Migration'}
      </button>
    </div>
  );
}
export default MigrationPipelines;
