import React, { useState, useEffect, useMemo } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import * as apiClient from './api_client';
import ObjectSelection from './ObjectSelection';
import ObjectTypeSelector from './ObjectTypeSelector';
import {
  Box,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Alert,
  LinearProgress,
  Card,
  CardContent,
  Grid,
  Chip,
  Stepper,
  Step,
  StepLabel
} from '@mui/material';
import {
  CheckCircleOutline as CheckIcon,
  Error as ErrorIcon,
  Storage as StorageIcon
} from '@mui/icons-material';
import './MigrationWorkflow.css';
import { useMigration } from './MigrationContext';

function MigrationWorkflow() {
  const location = useLocation();
  const navigate = useNavigate(); // Initialize useNavigate
  const { sourceDbType, sourceConnectionDetails } = location.state || {};
  const { startNewMigration } = useMigration();

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

    startNewMigration(migrationDetails);
    navigate('/migration-pipelines');
  };

  const isButtonDisabled = !selectedSourceSchema || objectListingStatus.startsWith('Error') || !targetConnectionStatus.startsWith('Connected') || oracleObjects.length === 0 || selectedObjectsForMigration.length === 0;

  const steps = ['Connect Databases', 'Select Schema', 'Choose Objects', 'Build Pipeline'];
  const activeStep = useMemo(() => {
    if (!sourceDbType || !targetConnectionStatus.startsWith('Connected')) return 0;
    if (!selectedSourceSchema) return 1;
    if (selectedObjectsForMigration.length === 0) return 2;
    return 3;
  }, [sourceDbType, targetConnectionStatus, selectedSourceSchema, selectedObjectsForMigration]);

  return (
    <Box sx={{ maxWidth: 1200, margin: '0 auto', p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Migration Workflow
      </Typography>

      <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
        {steps.map((label) => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      <Grid container spacing={3}>
        {/* Source Database Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <StorageIcon sx={{ mr: 1 }} />
                Source Database ({sourceDbType ? sourceDbType.charAt(0).toUpperCase() + sourceDbType.slice(1) : 'N/A'})
              </Typography>
              
              {sourceConnectionDetails && (
                <Chip
                  icon={<CheckIcon />}
                  label={`Connected to ${sourceConnectionDetails.host}:${sourceConnectionDetails.port}`}
                  color="success"
                  variant="outlined"
                  sx={{ mb: 2 }}
                />
              )}

              {sourceSchemas.length > 0 && (
                <FormControl fullWidth sx={{ mb: 2 }}>
                  <InputLabel>Select Schema</InputLabel>
                  <Select
                    value={selectedSourceSchema}
                    onChange={(e) => setSelectedSourceSchema(e.target.value)}
                    label="Select Schema"
                  >
                    {sourceSchemas.map((schema) => (
                      <MenuItem key={schema} value={schema}>{schema}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}

              {selectedSourceSchema && (
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle1" gutterBottom>
                    Object Type
                  </Typography>
                  <ObjectTypeSelector
                    objectTypes={sourceObjectTypes}
                    selectedObjectType={selectedObjectType}
                    onSelectObjectType={setSelectedObjectType}
                  />
                  <Button
                    variant="contained"
                    onClick={handleListOracleObjects}
                    sx={{ mt: 2 }}
                    fullWidth
                  >
                    List Objects
                  </Button>
                  {objectListingStatus && (
                    <Alert 
                      severity={objectListingStatus.includes('Error') ? 'error' : 
                               objectListingStatus.includes('Listing') ? 'info' : 'success'}
                      sx={{ mt: 2 }}
                    >
                      {objectListingStatus}
                    </Alert>
                  )}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Target Database Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                <StorageIcon sx={{ mr: 1 }} />
                Target Database ({targetDbType.charAt(0).toUpperCase() + targetDbType.slice(1)})
              </Typography>

              {targetConnectionDetails && (
                <Chip
                  icon={targetConnectionStatus.startsWith('Connected') ? <CheckIcon /> : <ErrorIcon />}
                  label={`${targetConnectionDetails.host}:${targetConnectionDetails.port}`}
                  color={targetConnectionStatus.startsWith('Connected') ? 'success' : 'error'}
                  variant="outlined"
                  sx={{ mb: 2 }}
                />
              )}

              {targetConnectionStatus && (
                <Alert 
                  severity={targetConnectionStatus.startsWith('Connected') ? 'success' : 'error'}
                >
                  {targetConnectionStatus}
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Object Selection */}
        {oracleObjects.length > 0 && (
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Select Objects for Migration
              </Typography>
              <ObjectSelection
                objects={oracleObjects}
                selectedObjectType={selectedObjectType}
                onObjectSelect={handleObjectSelection}
              />
            </Paper>
          </Grid>
        )}
      </Grid>

      {/* Bottom Action Bar */}
      <Box sx={{ mt: 4, display: 'flex', justifyContent: 'center' }}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleBuildPipelines}
          disabled={isButtonDisabled}
          size="large"
        >
          Build Migration Pipeline
        </Button>
      </Box>

      {/* Progress Indicator */}
      {objectListingStatus.includes('Listing') && (
        <Box sx={{ width: '100%', mt: 2 }}>
          <LinearProgress />
        </Box>
      )}
    </Box>
  );
}

export default MigrationWorkflow;
