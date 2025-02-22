import React from 'react';
import CreateConsumerForm from './components/CreateConsumerForm';
import ConsumersList from './components/ConsumersList';

function App() {
  return (
    <div className="app-container">
      <h1>Kafka Consumer Manager</h1>
      <CreateConsumerForm />
      <hr />
      <ConsumersList />
    </div>
  );
}

export default App;