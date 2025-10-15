import React from 'react';
import { Box, Typography } from '@mui/material';
import oracleLogo from './assets/ora.png';
import migrationLogo from './assets/dbai.png';
import postgresLogo from './assets/pg.png';
import migrationLogo1 from './assets/logo1.png';

function DbMigrate() {
  return (
    <Box sx={{ textAlign: 'center', mt: 4 }}>
      <Typography variant="h4" gutterBottom>
        DbMigrate.AI
      </Typography>
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 2, mt: 4 }}>
        <img src={migrationLogo} alt="Migration Tool" style={{ height: 800 }} />
      </Box>
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 2, mt: 4 }}>
        <img src={migrationLogo1} alt="Migration Tool" style={{ height: 800 }} />
        
      </Box>
    </Box>
  );
}

export default DbMigrate;
