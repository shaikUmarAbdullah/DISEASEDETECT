// ImageUpload.js
import React, { useState } from 'react';
import axios from 'axios';
import './css/styles.css'

const ImageUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [predictionResult, setPredictionResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post('http://localhost:8000/predict', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setPredictionResult(response.data);
      setError(null);
    } catch (error) {
      console.error('Error uploading image:', error);
      setError('Error predicting image. Please try again.');
      setPredictionResult(null);
      console.log('Error response:', error.response);
    }
  };

  return (
    <div className="container">
      <input type="file" onChange={handleFileChange} style={{ marginBottom: '10px' }} />
      <button onClick={handleUpload} className="uploadButton">
        Upload
      </button>

      {predictionResult && (
        <div className="resultContainer">
          <h2>Prediction Result:</h2>
          <p><strong>Class:</strong> {predictionResult.class}</p>
          <p><strong>Confidence:</strong> {predictionResult.confidence}</p>
          {predictionResult.disease_info && (
            <div>
              <h3>Disease Information:</h3>
              <p>
                <strong>Crop Type: </strong>{predictionResult.disease_info.CropType}
              </p>
              <p>
                <strong>Symptoms:</strong>{predictionResult.disease_info.symptoms}
                
              </p>
              <p><strong>Treatment:</strong> {predictionResult.disease_info.info}</p>
            </div>
          )}
        </div>
      )}

      {error && <p className="errorText">{error}</p>}
    </div>
  );
};

export default ImageUpload;
