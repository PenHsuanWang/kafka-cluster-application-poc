import React, { useEffect, useState } from 'react';

function ConsumersList() {
  const [consumers, setConsumers] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchConsumers = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/list-consumers');
      if (response.ok) {
        const data = await response.json();
        setConsumers(data);
      } else {
        console.error('Failed to fetch consumers');
      }
    } catch (error) {
      console.error('Error fetching consumers:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConsumers();
  }, []);

  const handleStart = async (consumerId) => {
    try {
      const response = await fetch('http://localhost:8000/start-consumer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ consumer_id: consumerId })
      });
      if (response.ok) {
        alert(`Consumer '${consumerId}' started/resumed.`);
        fetchConsumers();
      } else {
        const errorData = await response.json();
        alert(`Error starting consumer: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('Error starting consumer:', error);
    }
  };

  const handlePause = async (consumerId) => {
    try {
      const response = await fetch('http://localhost:8000/pause-consumer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ consumer_id: consumerId })
      });
      if (response.ok) {
        alert(`Consumer '${consumerId}' paused.`);
        fetchConsumers();
      } else {
        const errorData = await response.json();
        alert(`Error pausing consumer: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('Error pausing consumer:', error);
    }
  };

  const handleTerminate = async (consumerId) => {
    try {
      const response = await fetch('http://localhost:8000/terminate-consumer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ consumer_id: consumerId })
      });
      if (response.ok) {
        alert(`Consumer '${consumerId}' terminated.`);
        fetchConsumers();
      } else {
        const errorData = await response.json();
        alert(`Error terminating consumer: ${errorData.detail}`);
      }
    } catch (error) {
      console.error('Error terminating consumer:', error);
    }
  };

  if (loading) {
    return <p>Loading consumers...</p>;
  }

  return (
    <div>
      <h2>Current Consumers</h2>
      <button onClick={fetchConsumers}>Refresh List</button>
      <ul style={{ marginTop: '1rem' }}>
        {consumers.length === 0 ? (
          <p>No consumers found.</p>
        ) : (
          consumers.map((consumer) => {
            let actionButton;
            if (consumer.status === 'CREATED') {
              actionButton = (
                <button onClick={() => handleStart(consumer.consumer_id)}>
                  Start
                </button>
              );
            } else if (consumer.status === 'RUNNING') {
              actionButton = (
                <button onClick={() => handlePause(consumer.consumer_id)}>
                  Pause
                </button>
              );
            } else if (consumer.status === 'PAUSED') {
              actionButton = (
                <button onClick={() => handleStart(consumer.consumer_id)}>
                  Resume
                </button>
              );
            } else {
              // TERMINATED or unknown
              actionButton = null;
            }

            return (
              <li key={consumer.consumer_id} style={{ marginBottom: '1rem' }}>
                <strong>{consumer.consumer_name}</strong>
                <span> (ID: {consumer.consumer_id})</span>
                <div>
                  <span>
                    Broker: {consumer.broker}, Topic: {consumer.topic}, Status: {consumer.status}
                  </span>
                </div>
                <div style={{ marginTop: '0.5rem' }}>
                  {actionButton}
                  {consumer.status !== 'TERMINATED' && (
                    <button
                      onClick={() => handleTerminate(consumer.consumer_id)}
                      style={{ marginLeft: '1rem' }}
                    >
                      Terminate
                    </button>
                  )}
                </div>
              </li>
            );
          })
        )}
      </ul>
    </div>
  );
}

export default ConsumersList;