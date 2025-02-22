import React, { useState } from 'react';

function CreateConsumerForm() {
  const [consumerName, setConsumerName] = useState('');
  const [broker, setBroker] = useState('');
  const [topic, setTopic] = useState('');
  const [filePath, setFilePath] = useState('');
  const [groupId, setGroupId] = useState('demo-consumer-group');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/create-consumer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: consumerName,
          broker,
          topic,
          file_path: filePath,
          group_id: groupId
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        alert(`Error creating consumer: ${errorData.detail}`);
      } else {
        const data = await response.json();
        alert(`Consumer created: ${data.consumer_name} (ID: ${data.consumer_id})`);
        setConsumerName('');
        setBroker('');
        setTopic('');
        setFilePath('');
        setGroupId('demo-consumer-group');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Failed to create consumer');
    }
  };

  return (
    <div>
      <h2>Create New Consumer</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Consumer Name:</label>
          <input
            type="text"
            value={consumerName}
            onChange={(e) => setConsumerName(e.target.value)}
            required
          />
        </div>
        <div>
          <label>Broker:</label>
          <input
            type="text"
            value={broker}
            onChange={(e) => setBroker(e.target.value)}
            placeholder="localhost:9092"
            required
          />
        </div>
        <div>
          <label>Topic:</label>
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            required
          />
        </div>
        <div>
          <label>File Path:</label>
          <input
            type="text"
            value={filePath}
            onChange={(e) => setFilePath(e.target.value)}
            placeholder="./outputA.txt"
            required
          />
        </div>
        <div>
          <label>Group ID:</label>
          <input
            type="text"
            value={groupId}
            onChange={(e) => setGroupId(e.target.value)}
          />
        </div>
        <button type="submit">Create Consumer</button>
      </form>
    </div>
  );
}

export default CreateConsumerForm;