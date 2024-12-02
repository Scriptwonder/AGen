import React, { useState } from 'react';
import axios from 'axios';
import GraphVisualizer from './GraphVisualizer';

function App() {
  const [concept, setConcept] = useState('');
  const [data, setData] = useState(null);
  const [analogies, setAnalogies] = useState(null); // State to hold analogy data
  const [similarityScores, setSimilarityScores] = useState([]); // State to hold similarity scores
  const [loading, setLoading] = useState(false);
  const [loadingAnalogy, setLoadingAnalogy] = useState(false); // State for analogy loading
  const [loadingSimilarity, setLoadingSimilarity] = useState(false); // State for similarity score loading
  const [error, setError] = useState(null);  // State to manage errors

  const handleSubmit = async () => {
    setLoading(true);
    setError(null);  // Reset error state before request
    try {
      const response = await axios.post('http://127.0.0.1:5000/generate-concept', { concept });
      setData(response.data);
    } catch (err) {
      if (err.response) {
        // The server responded with a status code that falls out of the range of 2xx
        console.error('Response error:', err.response);
        setError(`Server responded with error code ${err.response.status}: ${err.response.statusText}`);
      } else if (err.request) {
        // The request was made but no response was received
        console.error('No response received:', err.request);
        setError('No response received from the server. Please make sure the server is running.');
      } else {
        // Something happened in setting up the request that triggered an Error
        console.error('Axios setup error:', err.message);
        setError(`Error in request setup: ${err.message}`);
      }
    }
    setLoading(false);
  };

  // Function to handle analogy generation
  const handleGenerateAnalogy = async () => {
    if (!data) {
      setError('Please generate the concept first.');
      return;
    }
    
    setLoadingAnalogy(true);
    setError(null);
    try {
      const response = await axios.post('http://127.0.0.1:5000/generate-analogy', { concept: data.concept });
      const analogyData = response.data;
      //console.log('Analogy data:', analogyData);
      if (
        analogyData &&
        Array.isArray(analogyData.analogies_concepts) &&
        Array.isArray(analogyData.analogies_kgs) &&
        analogyData.analogies_concepts.length > 0 &&
        analogyData.analogies_kgs.length === analogyData.analogies_concepts.length
      ) {
        // Combine analogy concepts and their respective graphs into one array
        const combinedAnalogies = analogyData.analogies_concepts.map((concept, index) => ({
          summary: concept,
          explanation: analogyData.analogies_summaries[index],
          graph: analogyData.analogies_kgs[index],
          //score: analogyData.analogies_scores[index]
        }));
        setAnalogies(combinedAnalogies);
        setSimilarityScores([]); // Clear previous similarity scores
      } else {
        setError('Received empty or invalid data for analogies.');
      }
    } catch (err) {
      if (err.response) {
        console.error('Response error:', err.response);
        setError(`Server responded with error code ${err.response.status}: ${err.response.statusText}`);
      } else if (err.request) {
        console.error('No response received:', err.request);
        setError('No response received from the server. Please make sure the server is running.');
      } else {
        console.error('Axios setup error:', err.message);
        setError(`Error in request setup: ${err.message}`);
      }
    }
    setLoadingAnalogy(false);
  };

  // Function to handle similarity calculation
  const handleCalculateSimilarity = async (analogyIndex) => {
    if (!data || !analogies || !analogies[analogyIndex]) {
      setError('Please generate the concept and analogy first.');
      return;
    }
    setLoadingSimilarity(true);
    setError(null);
    try {
      const response = await axios.post('http://127.0.0.1:5000/calculate-similarity', {
        analogy_index: analogyIndex,
      });
      const similarityData = response.data;

      if (similarityData && typeof similarityData.similarity_score === 'number') {
        const newSimilarityScores = [...similarityScores];
        newSimilarityScores[analogyIndex] = similarityData.similarity_score;
        setSimilarityScores(newSimilarityScores);
      } else {
        setError('Received empty or invalid similarity score data.');
      }
    } catch (err) {
      if (err.response) {
        console.error('Response error:', err.response);
        setError(`Server responded with error code ${err.response.status}: ${err.response.statusText}`);
      } else if (err.request) {
        console.error('No response received:', err.request);
        setError('No response received from the server. Please make sure the server is running.');
      } else {
        console.error('Axios setup error:', err.message);
        setError(`Error in request setup: ${err.message}`);
      }
    }
    setLoadingSimilarity(false);
  };
  return (
    <div style={{textAlign: 'center'}}>
      <h1>Analogy Generator</h1>
      <input
        type="text"
        value={concept}
        onChange={(e) => setConcept(e.target.value)}
        placeholder="Enter your concept"
      />
      <button onClick={handleSubmit}>Generate Concept</button>

      {loading && <p>Generating... Please wait.</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      {data && (
        <div>
          <h1>{data.concept}</h1>
          <h2>Concept Summary</h2>
          <p>{data.summary}</p>
          <h3>Concept Graph</h3>
          <GraphVisualizer triplets= {data.knowledge_graph} />

          {/* Generate Analogy Button */}
          <button onClick={handleGenerateAnalogy}>Generate Analogy</button>
          {loadingAnalogy && <p>Generating analogy... Please wait.</p>}

          {/* {data.analogies.map((analogy, index) => (
            <div key={index}>
              <h2>Analogy {index + 1}</h2>
              <p>{analogy.summary}</p>
              <GraphVisualizer triplets={analogy.graph} />
            </div>
          ))} */}
        </div>
      )}

      {analogies && (
        <div style={{ display: 'flex', flexDirection: 'row', flexWrap: 'wrap', gap: '20px', justifyContent: 'space-between' }}>
          {analogies.map((analogy, index) => (
            <div key={index} style={{textAlign: 'center'}}>
              <h3>Analogy {index + 1}</h3>
              <p>{analogy.summary}</p>
              <p>{analogy.explanation}</p>
              {/* <p>Score: {analogy.score}</p> */}
              <GraphVisualizer triplets={analogy.graph} />
              <button onClick={() => handleCalculateSimilarity(index)}>Calculate Similarity Score</button>
              {loadingSimilarity && <p>Calculating similarity... Please wait.</p>}
              {similarityScores[index] !== undefined && (
                <p>Similarity Score: {similarityScores[index]}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
