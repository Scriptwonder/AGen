import React, { useState } from 'react';
import axios from 'axios';
import GraphVisualizer from './GraphVisualizer';

function App() {
  const [concept, setConcept] = useState('');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);  // State to manage errors

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);  // Reset error state before request
    try {
      const response = await axios.post('http://127.0.0.1:5000/generate-concept', { concept });
      setData(response.data);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Error fetching data. Please try again.');
    }
    setLoading(false);
  };

  return (
    <div>
      <h1>Analogy Generator</h1>
      <input
        type="text"
        value={concept}
        onChange={(e) => setConcept(e.target.value)}
        placeholder="Enter your concept"
      />
      <button onClick={handleSubmit}>Generate</button>

      {loading && <p>Generating... Please wait.</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      {data && (
        <div>
          <h1>{data.concept}</h1>
          <h2>Concept Summary</h2>
          <p>{data.summary}</p>
          <h3>Concept Graph</h3>
          <GraphVisualizer triplets={data.knowledge_graph} />

          {data.analogies.map((analogy, index) => (
            <div key={index}>
              <h2>Analogy {index + 1}</h2>
              <p>{analogy.summary}</p>
              <GraphVisualizer triplets={analogy.graph} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
