import React, { useState, useEffect } from "react";
import { getCategories, addCategory } from "../api"; // Import API functions

const CategoriesPage = () => {
  const [categories, setCategories] = useState([]);
  const [newCategory, setNewCategory] = useState("");
  const [error, setError] = useState("");

  // Fetch categories from the API
  useEffect(() => {
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await getCategories();
      setCategories(response.data);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch categories");
    }
  };

  const handleAddCategory = async () => {
    if (!newCategory.trim()) {
      setError("Category name is required");
      return;
    }

    try {
      const response = await addCategory(newCategory);
      setCategories((prev) => [...prev, response.data]);
      setNewCategory("");
      setError("");
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.error || "Failed to add category");
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>Categories</h1>

      {/* Display Existing Categories */}
      <ul>
        {categories.map((category) => (
          <li key={category.id}>{category.name}</li>
        ))}
      </ul>

      {/* Add New Category */}
      <div style={{ marginTop: "20px" }}>
        <h2>Add a New Category</h2>
        <input
          type="text"
          value={newCategory}
          onChange={(e) => setNewCategory(e.target.value)}
          placeholder="Enter category name"
          style={{ padding: "10px", width: "300px", marginRight: "10px" }}
        />
        <button onClick={handleAddCategory} style={{ padding: "10px" }}>
          Add
        </button>
        {error && <p style={{ color: "red" }}>{error}</p>}
      </div>
    </div>
  );
};

export default CategoriesPage;
