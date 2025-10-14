import React, { createContext, useState, useEffect, useContext, useCallback } from 'react';
import * as apiClient from './api_client';

const MigrationContext = createContext();

export const useMigration = () => {
  return useContext(MigrationContext);
};

export const MigrationProvider = ({ children }) => {
  const [migrationJobId, setMigrationJobId] = useState(null);
  const [pipelineStatus, setPipelineStatus] = useState({});
  const [isMigrationRunning, setIsMigrationRunning] = useState(false);
  const [overallMigrationStatus, setOverallMigrationStatus] = useState('pending');
  const [overallErrorMessage, setOverallErrorMessage] = useState(null);
  const [migrationDetails, setMigrationDetails] = useState(null); // To store initial details

  const fetchMigrationStatus = useCallback(async () => {
    if (!migrationJobId) return;
    try {
      const statusResponse = await apiClient.getMigrationStatus(migrationJobId);
      console.log("Fetched migration status from context:", statusResponse);
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
          job_id: childJob.job_id,
        };
      });
      setPipelineStatus(newPipelineStatus);

      if (statusResponse.status === 'completed' || statusResponse.status === 'failed') {
        setIsMigrationRunning(false);
      }
    } catch (error) {
      console.error("Error fetching migration status from context:", error);
      setOverallErrorMessage(`Failed to fetch migration status: ${error.message}`);
      setIsMigrationRunning(false);
    }
  }, [migrationJobId]);

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
  }, [isMigrationRunning, migrationJobId, fetchMigrationStatus]);

  const startNewMigration = async (details) => {
    if (!details) return;
    setMigrationDetails(details);
    setIsMigrationRunning(true);
    setOverallMigrationStatus('processing');
    setOverallErrorMessage(null);
    setPipelineStatus({}); // Clear previous pipeline status

    try {
      const response = await apiClient.startMigration(details);
      setMigrationJobId(response.job_id);
      alert(`Migration initiated! Job ID: ${response.job_id}`);
      // Initial fetch after job ID is set
      // fetchMigrationStatus(); // This will be triggered by useEffect
    } catch (error) {
      console.error("Error initiating migration from context:", error);
      setOverallErrorMessage(`Failed to initiate migration: ${error.message}`);
      setIsMigrationRunning(false);
      setOverallMigrationStatus('failed');
    }
  };

  const value = {
    migrationJobId,
    pipelineStatus,
    isMigrationRunning,
    overallMigrationStatus,
    overallErrorMessage,
    migrationDetails,
    setMigrationJobId,
    setPipelineStatus,
    setIsMigrationRunning,
    setOverallMigrationStatus,
    setOverallErrorMessage,
    setMigrationDetails,
    startNewMigration,
    fetchMigrationStatus,
  };

  return (
    <MigrationContext.Provider value={value}>
      {children}
    </MigrationContext.Provider>
  );
};
