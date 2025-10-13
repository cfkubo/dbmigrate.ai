import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import * as apiClient from './api_client';
import './MigrationPipelines.css';

// Helper component to display individual pipeline stages
const PipelineStage = ({ name, status, error }) => {
  let statusClass = 'stage-pending';
  if (status === 'processing') statusClass = 'stage-processing';
  if (status === 'success' || status === 'verified' || status === 'extracted') statusClass = 'stage-success';
  if (status === 'failed') statusClass = 'stage-failed';
  if (status === 'skipped') statusClass = 'stage-skipped'; // New status class for skipped

  return (
    <div className={`pipeline-stage ${statusClass}`}>
      <span>{name}</span>
      {error && <span className="stage-error-message"> ({error})</span>}
    </div>
  );
};

function MigrationPipelines() {
  const location = useLocation();
  const { migrationDetails } = location.state || {};

  const [migrationJobId, setMigrationJobId] = useState(null);
  const [pipelineStatus, setPipelineStatus] = useState({}); // Stores status for each object
  const [isMigrationRunning, setIsMigrationRunning] = useState(false);
  const [overallMigrationStatus, setOverallMigrationStatus] = useState('pending'); // overall status of the parent job
  const [overallErrorMessage, setOverallErrorMessage] = useState(null);

  useEffect(() => {
    if (!migrationDetails) {
      setOverallErrorMessage("No migration details found. Please go back and select objects.");
    }
  }, [migrationDetails]);

  useEffect(() => {
    let intervalId = null;
    if (isMigrationRunning && migrationJobId) {
      const pollStatus = async () => {
        await fetchMigrationStatus();
      };
      intervalId = setInterval(pollStatus, 3000);
    }

    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [isMigrationRunning, migrationJobId]);

  const fetchMigrationStatus = async () => {
    try {
      const statusResponse = await apiClient.getMigrationStatus(migrationJobId);
      console.log("Fetched migration status:", statusResponse);

      setOverallMigrationStatus(statusResponse.status);
      setOverallErrorMessage(statusResponse.error_message);

      const newPipelineStatus = {};
      // Assuming statusResponse.child_jobs is an array of child job statuses
      // Each child job should ideally contain its object_type, object_name, and stage statuses
      statusResponse.child_jobs.forEach(childJob => {
        const objectKey = `${childJob.object_type}_${childJob.object_name}`;
        newPipelineStatus[objectKey] = {
          overall: childJob.status,
          extraction: childJob.extraction_status || 'pending',
          conversion: childJob.conversion_status || 'pending',
          execution: childJob.execution_status || 'pending',
          data_migration: childJob.data_migration_status || 'pending',
          error: childJob.error_message || null,
          converted_ddl: childJob.converted_ddl || null,
        };
      });
      setPipelineStatus(newPipelineStatus);

      if (statusResponse.status === 'completed' || statusResponse.status === 'failed') {
        setIsMigrationRunning(false);
        // clearInterval(intervalId); // Stop polling - intervalId is not in this scope
      }

    } catch (error) {
      console.error("Error fetching migration status:", error);
      setOverallErrorMessage(`Failed to fetch migration status: ${error.message}`);
      setIsMigrationRunning(false);
    }
  };

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
        error: null,
        converted_ddl: null,
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
      <div className="objects-pipeline-view">
        {migrationDetails?.selected_objects.map((obj, index) => {
          const objectKey = `${obj.object_type}_${obj.object_name}`;
          const objStatus = pipelineStatus[objectKey] || {};
          return (
            <div key={index} className="object-pipeline-card">
              <h4>{obj.object_type}: {obj.object_name}</h4>
              <div className="pipeline-stages">
                <PipelineStage name="Extraction" status={objStatus.extraction} />
                <PipelineStage name="Conversion" status={objStatus.conversion} />
                {migrationDetails?.target_connection ? (
                  <PipelineStage name="Execution" status={objStatus.execution} />
                ) : (
                  <PipelineStage name="Execution" status="skipped" />
                )}
                {obj.object_type === 'TABLE' && migrationDetails.data_migration_enabled && (
                  <PipelineStage name="Data Migration" status={objStatus.data_migration} />
                )}
              </div>
              {objStatus.error && <p className="object-error">Error: {objStatus.error}</p>}
              {objStatus.converted_ddl && (
                <div className="converted-ddl-preview">
                  <h5>Converted DDL Preview:</h5>
                  <pre>{objStatus.converted_ddl.substring(0, 200)}...</pre>
                </div>
              )}
            </div>
          );
        })}
      </div>

      <button
        onClick={handleKickoffMigration}
        className="kickoff-button"
        disabled={isMigrationRunning || overallMigrationStatus === 'completed' || overallMigrationStatus === 'failed'}
      >
        {isMigrationRunning ? 'Migration in Progress...' : 'Kick off Migration'}
      </button>
    </div>
  );
}

export default MigrationPipelines;