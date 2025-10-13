import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css'; // We'll create this CSS file next

function Home() {
  return (
    <div className="home-container">
      <h3>Please select your choice. To build your AI assisted metadata conversion pipelines </h3>
      <div className="database-options">
        <Link to="/connect/oracle" className="db-option-block">
          <img src="/ora.png" alt="Oracle To Postgres" />
          <span>Oracle</span>
        </Link>
        <Link to="/connect/postgresql" className="db-option-block">
          <img src="/pg.png" alt="Teradata to Greenplum" />
          <span>PostgreSQL</span>
        </Link>
        {/* Add more database options as needed */}
      </div>
    </div>
  );
}

export default Home;
