import React, { useState, useEffect } from 'react';
import {
  Box,
  Checkbox,
  FormControlLabel,
  Typography,
  Paper,
  Grid,
  Alert,
  Divider
} from '@mui/material';
import './ObjectSelection.css';

function ObjectSelection({ objects, selectedObjectType, onObjectSelect }) {
  const [selectedObjects, setSelectedObjects] = useState([]);
  const [selectAll, setSelectAll] = useState(false);

  useEffect(() => {
    // Reset selection when object type changes
    setSelectedObjects([]);
    setSelectAll(false);
  }, [selectedObjectType]);

  const handleSelectAll = (event) => {
    const checked = event.target.checked;
    setSelectAll(checked);
    const newSelected = checked ? objects : [];
    setSelectedObjects(newSelected);
    onObjectSelect(newSelected);
  };

  const handleCheckboxChange = (objectName) => {
    setSelectedObjects((prevSelected) => {
      const newSelected = prevSelected.includes(objectName)
        ? prevSelected.filter((name) => name !== objectName)
        : [...prevSelected, objectName];
      
      // Update selectAll state based on whether all items are selected
      setSelectAll(newSelected.length === objects.length);
      
      onObjectSelect(newSelected);
      return newSelected;
    });
  };

  if (!objects || objects.length === 0) {
    return (
      <Alert severity="info">
        No {selectedObjectType.toLowerCase()}s found.
      </Alert>
    );
  }

  return (
    <Box>
      <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h6">
          Select {selectedObjectType}s for Migration
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <FormControlLabel
            control={
              <Checkbox
                checked={selectAll}
                onChange={handleSelectAll}
                color="primary"
              />
            }
            label="Select All"
          />
          <Typography variant="body2" color="text.secondary" sx={{ ml: 2 }}>
            {selectedObjects.length} of {objects.length} selected
          </Typography>
        </Box>
      </Box>
      
      <Divider sx={{ mb: 2 }} />

      <Grid container spacing={2}>
        {objects.map((objectName) => (
          <Grid item xs={12} sm={6} md={4} key={objectName}>
            <Paper 
              variant="outlined"
              sx={{ 
                p: 1,
                bgcolor: selectedObjects.includes(objectName) ? 'action.selected' : 'background.paper'
              }}
            >
              <FormControlLabel
                control={
                  <Checkbox
                    checked={selectedObjects.includes(objectName)}
                    onChange={() => handleCheckboxChange(objectName)}
                    color="primary"
                  />
                }
                label={objectName}
                sx={{ width: '100%' }}
              />
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export default ObjectSelection;