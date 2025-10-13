import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './App.css';
import Home from './Home';
import ConnectionDetails from './ConnectionDetails';
import MigrationWorkflow from './MigrationWorkflow'; // Import MigrationWorkflow
import MigrationPipelines from './MigrationPipelines'; // Import MigrationPipelines

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>DbMigrate.AI</h1>
          <p>Private AI-powered database migration assistant.</p>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/connect/:dbType" element={<ConnectionDetails />} />
            <Route path="/migrate" element={<MigrationWorkflow />} /> {/* New route for MigrationWorkflow */}
            <Route path="/migration-pipelines" element={<MigrationPipelines />} /> {/* New route for MigrationPipelines */}
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
