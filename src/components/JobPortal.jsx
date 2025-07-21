import React, { useState, useEffect } from 'react';
import axios from 'axios';

const JobPortal = ({ userInterests }) => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        // LinkedIn Jobs API call
        const linkedInJobs = await axios.get(`/api/linkedin/jobs`, {
          params: {
            keywords: userInterests.join(','),
            location: 'worldwide'
          }
        });

        // Glassdoor Jobs API call
        const glassdoorJobs = await axios.get(`/api/glassdoor/jobs`, {
          params: {
            keywords: userInterests.join(','),
            location: 'worldwide'
          }
        });

        // Combine and sort jobs from both sources
        const combinedJobs = [...linkedInJobs.data, ...glassdoorJobs.data]
          .sort((a, b) => new Date(b.posted) - new Date(a.posted));

        setJobs(combinedJobs);
      } catch (error) {
        console.error('Error fetching jobs:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchJobs();
  }, [userInterests]);

  return (
    <div className="job-portal">
      <h2>Recommended Jobs</h2>
      {loading ? (
        <div>Loading jobs...</div>
      ) : (
        <div className="jobs-grid">
          {jobs.map((job) => (
            <div key={job.id} className="job-card">
              <h3>{job.title}</h3>
              <p>{job.company}</p>
              <p>{job.location}</p>
              <p>{job.description}</p>
              <a href={job.url} target="_blank" rel="noopener noreferrer">
                Apply Now
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default JobPortal;