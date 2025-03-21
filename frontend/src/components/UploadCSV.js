import React, { useState } from "react";
import { Link } from "react-router-dom";
import { uploadCSV } from "../api";

const UploadCSV = () => {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState("");

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await uploadCSV(file);
      setMessage(response.data.message);
    } catch (err) {
      setMessage("Failed to upload CSV");
    }
  };

  return (
    <div>
      <h2>Upload CSV</h2>
      <form onSubmit={handleSubmit}>
        <input type="file" accept=".csv" onChange={handleFileChange} />
        <button type="submit">Upload</button>
      </form>
      {message && <p>{message}</p>}


      <h4><Link to="/create-transaction">Create Transaction</Link></h4>
    </div>
  );
};

export default UploadCSV;
