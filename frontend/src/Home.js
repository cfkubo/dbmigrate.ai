import React from 'react';
import { Link } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardActionArea,
  CardContent,
  Button,
  Paper,
  Stack,
  useTheme
} from '@mui/material';
import {
  CompareArrows as CompareArrowsIcon,
  Speed as SpeedIcon,
  AutoFixHigh as AIIcon,
  Security as SecurityIcon,
  Analytics as AnalyticsIcon,
  Transform as TransformIcon
} from '@mui/icons-material';

function FeatureCard({ icon, title, description }) {
  return (
    <Card sx={{ 
      width: '100%',
      height: '100%', 
      display: 'flex', 
      flexDirection: 'column',
      borderRadius: 2,
      bgcolor: 'background.paper',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
      transition: 'all 0.3s ease',
      overflow: 'hidden',
      position: 'relative',
      '&:hover': {
        transform: 'translateY(-8px)',
        boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        '& .feature-icon': {
          transform: 'scale(1.1)',
        }
      },
      '&::before': {
        content: '""',
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '4px',
        background: 'linear-gradient(120deg, #1976d2, #1a237e)',
        opacity: 0.8
      }
    }}>
      <CardContent sx={{ 
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        p: { xs: '6%', sm: '8%' },
        pt: { xs: '8%', sm: '10%' }
      }}>
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          mb: '8%',
          p: '10%',
          borderRadius: '50%',
          background: 'linear-gradient(145deg, rgba(25, 118, 210, 0.08), rgba(26, 35, 126, 0.08))',
          transition: 'all 0.3s ease',
          width: 'clamp(60px, 15%, 100px)',
          aspectRatio: '1/1'
        }} className="feature-icon">
          {React.cloneElement(icon, { 
            sx: { 
              fontSize: 'clamp(1.5rem, 3vw + 0.5rem, 2.5rem)',
              color: 'primary.main',
              width: '100%',
              height: '100%'
            } 
          })}
        </Box>
        <Typography 
          variant="h6" 
          component="div" 
          align="center"
          sx={{ 
            mb: 2.5,
            fontWeight: 600,
            color: 'text.primary'
          }}
        >
          {title}
        </Typography>
        <Typography 
          variant="body1" 
          color="text.secondary" 
          align="center"
          sx={{ 
            maxWidth: '300px',
            mx: 'auto',
            lineHeight: 1.6
          }}
        >
          {description}
        </Typography>
      </CardContent>
    </Card>
  );
}

function MigrationCard({ title, sourceDb, targetDb, sourceLogo, targetLogo, description, to }) {
  const theme = useTheme();
  
  return (
        <Card
      sx={{ 
        width: '100%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderRadius: 2,
        background: 'linear-gradient(145deg, #ffffff 0%, #f5f5f5 100%)',
        boxShadow: '0 4px 20px rgba(0, 0, 0, 0.08)',
        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '4px',
          background: 'linear-gradient(90deg, #64b5f6, #1976d2)',
          opacity: 0.8,
          borderRadius: '2px 2px 0 0'
        },
        '&:hover': {
          transform: 'translateY(-8px)',
          boxShadow: '0 20px 30px rgba(25, 118, 210, 0.15)',
          '&::before': {
            background: 'linear-gradient(90deg, #1976d2, #1a237e)',
            opacity: 1
          }
        }
      }}>
      <CardActionArea 
        component={Link} 
        to={to}
        sx={{ 
          height: '100%',
          display: 'flex', 
          flexDirection: 'column',
          p: { xs: '4%', sm: '6%', md: '8%' }
        }}
      >
        <Box sx={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'space-between',
          mb: 4,
          px: { xs: '4%', sm: '6%', md: '8%' },
          width: '100%',
          maxWidth: '600px',
          mx: 'auto'
        }}>
          <Box
            component="img"
            src={sourceLogo}
            alt={sourceDb}
            sx={{ 
              width: 'clamp(100px, 40%, 200px)',
              objectFit: 'contain',
              filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))',
              aspectRatio: '4/3'
            }}
            onError={(e) => {
              console.error(`Failed to load image: ${sourceLogo}`);
              e.target.src = '/assets/default-db.png';
            }}
          />
          <Box sx={{ 
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '20%'
          }}>
            <CompareArrowsIcon sx={{ 
              color: theme.palette.primary.main,
              fontSize: 'clamp(1.5rem, 2vw + 1rem, 2rem)'
            }} />
          </Box>
          <Box
            component="img"
            src={targetLogo}
            alt={targetDb}
            sx={{ 
              width: 'clamp(100px, 40%, 200px)',
              objectFit: 'contain',
              filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))',
              aspectRatio: '4/3'
            }}
            onError={(e) => {
              console.error(`Failed to load image: ${targetLogo}`);
              e.target.src = '/assets/default-db.png';
            }}
          />
        </Box>
        <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <Typography 
            variant="h6" 
            component="div" 
            align="center"
            sx={{ 
              mb: '0.5em',
              fontWeight: 600,
              fontSize: 'clamp(1.125rem, 2.5vw, 1.5rem)'
            }}
          >
            {title}
          </Typography>
          <Typography 
            variant="body2" 
            color="text.secondary" 
            align="center"
            sx={{
              fontSize: 'clamp(0.875rem, 2vw, 1rem)',
              lineHeight: 1.6,
              maxWidth: '90%',
              mx: 'auto'
            }}
          >
            {description}
          </Typography>
        </Box>
      </CardActionArea>
    </Card>
  );
} 



function Home() {
  const migrationOptions = [
    {
      title: "Oracle to PostgreSQL",
      sourceDb: "Oracle",
      targetDb: "PostgreSQL",
      sourceLogo: "/assets/oracle.png",
      targetLogo: "/assets/postgres.png",
      description: "Migrate Oracle database objects to PostgreSQL with AI assistance",
      to: "/connect/oracle"
    },
    {
      title: "Teradata to Greenplum",
      sourceDb: "Teradata",
      targetDb: "Greenplum",
      sourceLogo: "/assets/teradata.png",
      targetLogo: "/assets/greenplum.png",
      description: "Convert Teradata workloads to Greenplum (Coming Soon)",
      to: "#"
    },
    {
      title: "SQL Server to PostgreSQL",
      sourceDb: "SQL Server",
      targetDb: "PostgreSQL",
      sourceLogo: "/assets/sqlserver.png",
      targetLogo: "/assets/postgres.png",
      description: "Migrate from SQL Server to PostgreSQL (Coming Soon)",
      to: "#"
    },
    {
      title: "DB2 to PostgreSQL",
      sourceDb: "DB2",
      targetDb: "PostgreSQL",
      sourceLogo: "/assets/db2.png",
      targetLogo: "/assets/postgres.png",
      description: "Transform DB2 database objects to PostgreSQL (Coming Soon)",
      to: "#"
    }
  ];

  const features = [
    {
      icon: <AIIcon sx={{ fontSize: 40, color: '#1976d2' }} />,
      title: "AI-Powered Conversion",
      description: "Intelligent schema and code conversion with advanced AI algorithms"
    },
    {
      icon: <SpeedIcon sx={{ fontSize: 40, color: '#00c853' }} />,
      title: "Fast Migration",
      description: "Accelerated migration process with automated conversion pipelines"
    },
    {
      icon: <SecurityIcon sx={{ fontSize: 40, color: '#5c6bc0' }} />,
      title: "Secure & Reliable",
      description: "Enterprise-grade security with data integrity validation"
    },
    {
      icon: <AnalyticsIcon sx={{ fontSize: 40, color: '#3949ab' }} />,
      title: "Smart Analytics",
      description: "Detailed analysis and validation of migration results"
    }
  ];

  return (
    <Box>
      {/* Hero Section */}
      <Paper 
        elevation={0}
        sx={{
          position: 'relative',
          backgroundColor: '#1a237e',
          color: '#fff',
          mb: '5vh',
          backgroundSize: 'cover',
          backgroundRepeat: 'no-repeat',
          backgroundPosition: 'center',
          backgroundImage: `linear-gradient(120deg, rgba(25, 118, 210, 0.95), rgba(26, 35, 126, 0.95)), url(/assets/arch.png)`,
          minHeight: '40vh',
          maxHeight: '50vh',
          height: 'auto',
          display: 'flex',
          alignItems: 'center',
          overflow: 'hidden'
        }}
      >
        <Box
          sx={{
            position: 'absolute',
            top: 0,
            bottom: 0,
            right: 0,
            left: 0,
            backgroundColor: 'rgba(0,0,0,.6)',
          }}
        />
        <Container maxWidth="lg" sx={{ position: 'relative', height: '100%' }}>
          <Grid
            container
            sx={{
              height: '100%',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Grid item md={8}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography
                  component="h1"
                  variant="h2"
                  color="inherit"
                  gutterBottom
                  sx={{
                    fontSize: 'clamp(2rem, 4vw, 3.75rem)',
                    lineHeight: 1.2
                  }}
                >
                  Private & Secure Database Migration
                </Typography>
                <Typography 
                  variant="h5" 
                  color="inherit" 
                  paragraph
                  sx={{
                    fontSize: 'clamp(1rem, 2vw, 1.25rem)',
                    maxWidth: '600px',
                    mx: 'auto',
                    opacity: 0.9
                  }}
                >
                  AI-powered assistant for secure database conversions
                </Typography>
                <Stack
                  direction="row"
                  spacing={2}
                  justifyContent="center"
                  sx={{ mt: 4 }}
                >
                  <Button
                    variant="contained"
                    size="large"
                    component={Link}
                    to="/connect/oracle"
                    startIcon={<TransformIcon />}
                  >
                    Start Migration
                  </Button>
                </Stack>
              </Box>
            </Grid>
          </Grid>
        </Container>
      </Paper>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ mb: '10vh' }}>
        <Box sx={{ 
          mb: '6vh', 
          textAlign: 'center',
          position: 'relative',
          '&::after': {
            content: '""',
            position: 'absolute',
            bottom: '-2vh',
            left: '50%',
            transform: 'translateX(-50%)',
            width: 'clamp(40px, 10%, 80px)',
            height: '0.3vh',
            backgroundColor: 'primary.main',
            borderRadius: '1vh'
          }
        }}>
          <Typography 
            variant="h3" 
            gutterBottom 
            sx={{ 
              fontWeight: 700,
              mb: 3,
              background: 'linear-gradient(45deg, primary.main, primary.light)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}
          >
            Why Choose DbMigrate.AI
          </Typography>
          <Typography 
            variant="h6" 
            color="text.secondary"
            sx={{ 
              maxWidth: '800px',
              mx: 'auto',
              fontWeight: 400,
              lineHeight: 1.6
            }}
          >
            Comprehensive database migration solution with advanced AI capabilities
          </Typography>
        </Box>
        <Grid 
          container 
          spacing={4} 
          alignItems="stretch"
          sx={{
            '.MuiGrid-item': {
              display: 'flex'
            }
          }}
        >
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={3} key={index}>
              <FeatureCard {...feature} />
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Migration Options Section */}
      <Container maxWidth="xl" sx={{ mb: '8vh' }}>
        <Box sx={{ 
          mb: '4vh', 
          textAlign: 'center',
          position: 'relative',
          '&::after': {
            content: '""',
            position: 'absolute',
            bottom: '-2vh',
            left: '50%',
            transform: 'translateX(-50%)',
            width: 'clamp(40px, 10%, 80px)',
            height: '0.3vh',
            backgroundColor: 'primary.main',
            borderRadius: '1vh'
          }
        }}>
          <Typography 
            variant="h3" 
            gutterBottom 
            sx={{ 
              fontWeight: 700,
              mb: 3,
              fontSize: 'clamp(2rem, 4vw, 3rem)',
              background: 'linear-gradient(45deg, primary.main, primary.light)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              textTransform: 'uppercase',
              letterSpacing: '0.5px'
            }}
          >
            Supported Migrations
          </Typography>
          <Typography 
            variant="h6" 
            color="text.secondary"
            sx={{ 
              maxWidth: '800px',
              mx: 'auto',
              fontSize: 'clamp(1rem, 2vw, 1.25rem)',
              fontWeight: 400,
              lineHeight: 1.6
            }}
          >
            Choose your source and target databases for migration
          </Typography>
        </Box>
        <Grid 
          container 
          spacing={{ xs: 2, sm: 4 }}
          alignItems="stretch"
          justifyContent="center"
          sx={{
            '.MuiGrid-item': {
              display: 'flex',
              width: { xs: '100%', sm: '50%' },
              maxWidth: { sm: '600px' }
            },
            mx: 'auto',
            width: '100%',
            maxWidth: '1400px'
          }}
        >
          {migrationOptions.map((option, index) => (
            <Grid item xs={12} sm={6} key={index}>
              <MigrationCard {...option} />
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Call to Action */}
      <Box       sx={{ 
        background: 'linear-gradient(120deg, #1976d2, #1a237e)', 
        color: 'white', 
        py: 8, 
        mt: 6,
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '4px',
          background: 'linear-gradient(90deg, #64b5f6, #1976d2)'
        }
      }}>
        <Container maxWidth="lg">
          <Typography variant="h4" align="center" gutterBottom>
            Ready to Modernize Your Database?
          </Typography>
          <Typography variant="subtitle1" align="center" paragraph sx={{ mb: 4 }}>
            Start your migration journey with our AI-powered assistant
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
            <Button
              variant="contained"
              size="large"
              component={Link}
              to="/connect/oracle"
              sx={{ 
                background: 'linear-gradient(120deg, #ffffff, #f5f5f5)',
                color: '#1976d2',
                boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)',
                '&:hover': {
                  background: 'linear-gradient(120deg, #f5f5f5, #ffffff)',
                  transform: 'translateY(-2px)',
                  boxShadow: '0 6px 20px rgba(25, 118, 210, 0.15)'
                }
              }}
            >
              Start Migration Now
            </Button>
          </Box>
        </Container>
      </Box>
    </Box>
  );
}

export default Home;
