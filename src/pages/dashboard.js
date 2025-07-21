import React from 'react';
import JobPortal from '../components/JobPortal';
import styles from '../styles/Dashboard.module.css';

const Dashboard = () => {
  // You can later fetch these interests from user profile/settings
  const userInterests = ['web development', 'javascript', 'react'];

  return (
    <div className={styles.dashboard}>
      <header className={styles.header}>
        <h1>Dashboard</h1>
      </header>
      
      <main className={styles.main}>
        <section className={styles.jobSection}>
          <JobPortal userInterests={userInterests} />
        </section>
      </main>
    </div>
  );
};

export default Dashboard;