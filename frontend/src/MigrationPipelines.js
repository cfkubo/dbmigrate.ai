import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  tableCellClasses,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Chip,
  useTheme,
  styled
} from '@mui/material';
import * as apiClient from './api_client';
import { useMigration } from './MigrationContext';

// Styled components for the table
const StyledTableCell = styled(TableCell)(({ theme }) => ({
  [`&.${tableCellClasses.head}`]: {
    backgroundColor: theme.palette.mode === 'dark' ? theme.palette.grey[900] : theme.palette.grey[100],
    color: theme.palette.mode === 'dark' ? theme.palette.grey[300] : theme.palette.grey[900],
    fontWeight: 600,
  },
  [`&.${tableCellClasses.body}`]: {
    fontSize: 14,
    color: theme.palette.mode === 'dark' ? theme.palette.grey[300] : theme.palette.grey[900],
  },
}));

const StyledTableRow = styled(TableRow)(({ theme }) => ({
  '&:nth-of-type(odd)': {
    backgroundColor: theme.palette.mode === 'dark' 
      ? theme.palette.grey[900] 
      : theme.palette.grey[50],
  },
  '&:nth-of-type(even)': {
    backgroundColor: theme.palette.mode === 'dark' 
      ? 'rgba(255, 255, 255, 0.05)' 
      : 'rgba(0, 0, 0, 0.02)',
  },
  '&:hover': {
    backgroundColor: theme.palette.mode === 'dark'
      ? 'rgba(255, 255, 255, 0.1)'
      : 'rgba(0, 0, 0, 0.04)',
  },
}));

const CodeBlock = styled(Box)(({ theme }) => ({
  fontFamily: 'monospace',
  whiteSpace: 'pre-wrap',
  padding: theme.spacing(1.5),
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.mode === 'dark' 
    ? 'rgba(255, 255, 255, 0.05)' 
    : 'rgba(0, 0, 0, 0.04)',
  border: `1px solid ${theme.palette.mode === 'dark' 
    ? 'rgba(255, 255, 255, 0.1)' 
    : 'rgba(0, 0, 0, 0.1)'}`,
  maxHeight: '400px',
  overflow: 'auto',
  fontSize: '0.875rem',
  lineHeight: 1.5,
  color: theme.palette.mode === 'dark' 
    ? theme.palette.grey[300] 
    : theme.palette.grey[900],
}));
function MigrationPipelines() {
  const { 
    migrationJobId, 
    pipelineStatus, 
    isMigrationRunning, 
    overallMigrationStatus, 
    overallErrorMessage, 
    migrationDetails, 
    setIsMigrationRunning, 
    setOverallMigrationStatus, 
    setOverallErrorMessage, 
    setPipelineStatus, 
    startNewMigration, 
    fetchMigrationStatus,
    setMigrationDetails, // Added to allow setting migrationDetails from location.state
  } = useMigration();
  const location = useLocation();
  const locationMigrationDetails = location.state?.migrationDetails; // Get from location for initial kickoff

  const [expandedDdlJobId, setExpandedDdlJobId] = useState(null); // State to track expanded DDL

  // Effect to handle initial migration kickoff if details are passed via location state
  useEffect(() => {
    if (locationMigrationDetails && !migrationJobId && !isMigrationRunning) {
      setMigrationDetails(locationMigrationDetails); // Set details in context
      startNewMigration(locationMigrationDetails);
    }
  }, [locationMigrationDetails, migrationJobId, isMigrationRunning, startNewMigration, setMigrationDetails]);

  // Effect to set error message if no migration details are found (after initial load)
  useEffect(() => {
    if (!migrationDetails && !migrationJobId && !overallErrorMessage) {
      setOverallErrorMessage("No migration details found. Please go back and select objects.");
    }
  }, [migrationDetails, migrationJobId, overallErrorMessage, setOverallErrorMessage]);

  // Effect to fetch status if a job ID exists and is not running
  useEffect(() => {
    if (migrationJobId && !isMigrationRunning && overallMigrationStatus === 'pending') {
      fetchMigrationStatus();
    }
  }, [migrationJobId, isMigrationRunning, overallMigrationStatus, fetchMigrationStatus]);

  const handleKickoffMigration = async () => {
    if (!migrationDetails) return;
    startNewMigration(migrationDetails);
  };

  const theme = useTheme();

  const getStatusColor = (status) => {
    switch (status) {
      case 'processing':
        return 'primary';
      case 'success':
      case 'verified':
      case 'extracted':
        return 'success';
      case 'failed':
        return 'error';
      case 'skipped':
        return 'default';
      default:
        return 'default';
    }
  };
  const [expandedOriginalSqlJobId, setExpandedOriginalSqlJobId] = useState(null);
  const [expandedConvertedDdlJobId, setExpandedConvertedDdlJobId] = useState(null);

  const toggleExpansion = (jobId, type) => {
    if (type === 'original_sql') {
      setExpandedOriginalSqlJobId(expandedOriginalSqlJobId === jobId ? null : jobId);
      setExpandedConvertedDdlJobId(null); // Close other expansion
    } else if (type === 'converted_ddl') {
      setExpandedConvertedDdlJobId(expandedConvertedDdlJobId === jobId ? null : jobId);
      setExpandedOriginalSqlJobId(null); // Close other expansion
    }
  };
  if (!migrationDetails && !overallErrorMessage && !migrationJobId) {
    return (
      <Box p={3}>
        <Typography variant="h4">Loading Migration Details...</Typography>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Typography variant="h4" gutterBottom>Migration Pipelines Overview</Typography>
      
      {overallErrorMessage && (
        <Typography color="error" gutterBottom mb={3}>{overallErrorMessage}</Typography>
      )}

      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <Typography variant="h6">Overall Status:</Typography>
        <Chip
          label={overallMigrationStatus.toUpperCase()}
          color={getStatusColor(overallMigrationStatus)}
          sx={{ fontWeight: 600 }}
        />
      </Box>

      <Paper 
        elevation={2} 
        sx={{ 
          p: 3, 
          mb: 4,
          bgcolor: theme.palette.mode === 'dark' 
            ? 'rgba(255, 255, 255, 0.05)' 
            : 'background.paper'
        }}
      >
        <Typography variant="h6" gutterBottom>Migration Summary</Typography>
        <Typography variant="body1" gutterBottom>
          Source: {migrationDetails?.source_db_type} ({migrationDetails?.source_schema})
        </Typography>
        <Typography variant="body1" gutterBottom>
          Target: {migrationDetails?.target_db_type} ({migrationDetails?.target_schema})
        </Typography>
        <Typography variant="body1">
          Data Migration Enabled: {migrationDetails?.data_migration_enabled ? 'Yes' : 'No'}
        </Typography>
      </Paper>

      <Typography variant="h6" gutterBottom>Objects to Migrate</Typography>
      
      <TableContainer 
        component={Paper} 
        elevation={2}
        sx={{ 
          mb: 4,
          bgcolor: theme.palette.mode === 'dark' 
            ? 'rgba(255, 255, 255, 0.05)' 
            : 'background.paper'
        }}
      >
        <Table>
          <TableHead>
            <TableRow>
              <StyledTableCell>Object Type</StyledTableCell>
              <StyledTableCell>Object Name</StyledTableCell>
              <StyledTableCell>Original SQL</StyledTableCell>
              <StyledTableCell>Data Migration</StyledTableCell>
              <StyledTableCell>Overall Status</StyledTableCell>
              <StyledTableCell>Error</StyledTableCell>
              <StyledTableCell>Converted DDL</StyledTableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {migrationDetails?.selected_objects.map((obj, index) => {
              const objectKey = `${obj.object_type}_${obj.object_name}`;
              const objStatus = pipelineStatus[objectKey] || {};
              const isExpanded = expandedDdlJobId === objStatus.job_id;

              return (
                <React.Fragment key={index}>
                  <StyledTableRow>
                    <StyledTableCell>{obj.object_type}</StyledTableCell>
                    <StyledTableCell>{obj.object_name}</StyledTableCell>
                    <StyledTableCell>
                      {objStatus.original_sql ? (
                        <Box>
                          <CodeBlock>
                            {objStatus.original_sql.substring(0, 100)}...
                          </CodeBlock>
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => toggleExpansion(objStatus.job_id, 'original_sql')}
                            sx={{ mt: 1 }}
                          >
                            {expandedOriginalSqlJobId === objStatus.job_id ? 'Hide Original SQL' : 'View Original SQL'}
                          </Button>
                        </Box>
                      ) : '-'}
                    </StyledTableCell>
                    <StyledTableCell>
                      <Chip
                        label={obj.object_type === 'TABLE' && migrationDetails.data_migration_enabled 
                          ? (objStatus.data_migration || 'pending')
                          : 'skipped'}
                        color={getStatusColor(obj.object_type === 'TABLE' && migrationDetails.data_migration_enabled 
                          ? objStatus.data_migration 
                          : 'skipped')}
                        size="small"
                      />
                    </StyledTableCell>
                    <StyledTableCell>
                      <Chip
                        label={objStatus.overall || 'pending'}
                        color={getStatusColor(objStatus.overall)}
                        size="small"
                      />
                    </StyledTableCell>
                    <StyledTableCell>
                      <Typography color="error" variant="body2">
                        {objStatus.error_message || '-'}
                      </Typography>
                    </StyledTableCell>
                    <StyledTableCell>
                      {objStatus.converted_ddl ? (
                        <Box>
                          <CodeBlock>
                            {objStatus.converted_ddl.substring(0, 100)}...
                          </CodeBlock>
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => toggleExpansion(objStatus.job_id, 'converted_ddl')}
                            sx={{ mt: 1 }}
                          >
                            {expandedConvertedDdlJobId === objStatus.job_id ? 'Hide Converted DDL' : 'View Converted DDL'}
                          </Button>
                        </Box>
                      ) : '-'}
                    </StyledTableCell>
                  </StyledTableRow>
                  {expandedOriginalSqlJobId === objStatus.job_id && (
                    <StyledTableRow>
                      <StyledTableCell colSpan={7}>
                        <Box p={2}>
                          <Typography variant="h6" gutterBottom>
                            Full Original SQL for {obj.object_name}:
                          </Typography>
                          <CodeBlock>
                            {objStatus.original_sql}
                          </CodeBlock>
                        </Box>
                      </StyledTableCell>
                    </StyledTableRow>
                  )}
                  {expandedConvertedDdlJobId === objStatus.job_id && (
                    <StyledTableRow>
                      <StyledTableCell colSpan={7}>
                        <Box p={2}>
                          <Typography variant="h6" gutterBottom>
                            Full Converted DDL for {obj.object_name}:
                          </Typography>
                          <CodeBlock>
                            {objStatus.converted_ddl}
                          </CodeBlock>
                        </Box>
                      </StyledTableCell>
                    </StyledTableRow>
                  )}
                </React.Fragment>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>

      <Button
        variant="contained"
        onClick={handleKickoffMigration}
        disabled={isMigrationRunning || overallMigrationStatus === 'processing'}
        sx={{
          py: 1.5,
          px: 4,
          background: theme => theme.palette.mode === 'light'
            ? 'linear-gradient(120deg, #1976d2, #1a237e)'
            : 'linear-gradient(120deg, #2196f3, #1976d2)'
        }}
      >
        {isMigrationRunning || overallMigrationStatus === 'processing' 
          ? 'Migration In Progress...' 
          : 'Kickoff Migration'}
      </Button>
    </Box>
  );
}
export default MigrationPipelines;
