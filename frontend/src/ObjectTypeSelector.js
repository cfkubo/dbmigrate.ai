import React from 'react';
import { 
  Grid, 
  Card, 
  CardContent, 
  CardActionArea, 
  Typography, 
  Box,
  styled 
} from '@mui/material';
import {
  TableChart,
  Code,
  Functions,
  ViewQuilt,
  Inventory,
  FormatListNumbered,
  Bolt
} from '@mui/icons-material';
import './ObjectTypeSelector.css';

const StyledCard = styled(Card)(({ theme }) => ({
  height: '100%',
  transition: 'transform 0.2s ease-in-out',
  '&:hover': {
    transform: 'scale(1.02)',
  },
}));

const iconMap = {
  'TABLE': TableChart,
  'PROCEDURE': Code,
  'FUNCTION': Functions,
  'VIEW': ViewQuilt,
  'PACKAGE': Inventory,
  'INDEX': FormatListNumbered,
  'TRIGGER': Bolt,
};

const iconColors = {
  'TABLE': '#2196f3', // Blue
  'PROCEDURE': '#4caf50', // Green
  'FUNCTION': '#ff9800', // Orange
  'VIEW': '#9c27b0', // Purple
  'PACKAGE': '#f44336', // Red
  'INDEX': '#795548', // Brown
  'TRIGGER': '#607d8b', // Blue Grey
};

function ObjectTypeSelector({ objectTypes, selectedObjectType, onSelectObjectType }) {
  return (
    <Grid container spacing={2}>
      {objectTypes.map((type) => {
        const IconComponent = iconMap[type];
        
        return (
          <Grid item xs={6} sm={4} md={3} key={type}>
            <StyledCard 
              raised={selectedObjectType === type}
              sx={{
                bgcolor: selectedObjectType === type ? 'action.selected' : 'background.paper',
              }}
            >
              <CardActionArea onClick={() => onSelectObjectType(type)}>
                <CardContent>
                  <Box
                    sx={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      gap: 1,
                    }}
                  >
                    <Box
                      sx={{
                        backgroundColor: `${iconColors[type]}15`,
                        borderRadius: '50%',
                        p: 2,
                        mb: 1,
                      }}
                    >
                      <IconComponent 
                        sx={{ 
                          fontSize: 40,
                          color: iconColors[type],
                        }} 
                      />
                    </Box>
                    <Typography
                      variant="subtitle1"
                      align="center"
                      sx={{
                        fontWeight: selectedObjectType === type ? 600 : 400,
                      }}
                    >
                      {type.charAt(0) + type.slice(1).toLowerCase()}
                    </Typography>
                  </Box>
                </CardContent>
              </CardActionArea>
            </StyledCard>
          </Grid>
        );
      })}
    </Grid>
  );
}

export default ObjectTypeSelector;
