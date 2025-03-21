import React, { useState, useEffect } from "react";
import { updateTransaction, getCategories, createTransaction } from "../api";
import { formatDate } from "../utils";

const UpdateTransaction = ({ transaction, setTransactionToEdit }) => {
  const [description, setDescription] = useState(transaction ? transaction.description : "");
  const [amount, setAmount] = useState(transaction? transaction.amount : "");
  const [category, setCategory] = useState(transaction ? transaction.category : "");
  const [categories, setCategories] = useState([]);
  const [message, setMessage] = useState("");
  const [postDate, setPostDate] = useState(transaction ? transaction.post_date : "");

  useEffect(() => {
    // Fetch categories from the API
    const fetchCategories = async () => {
      try {
        const response = await getCategories();
        setCategories(response.data);
      } catch (err) {
        console.error("Failed to fetch categories:", err);
      }
    };

    fetchCategories();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if(transaction) {
        await updateTransaction(transaction.id, { description, amount, category });
      } else {
        await createTransaction({description, amount, category, post_date: postDate});
      }
      
      setMessage("Transaction updated successfully");
      setTransactionToEdit(null);
    } catch (err) {
      console.error("Failed to update transaction:", err);
      setMessage("Failed to update transaction");
    }
  };

  return (
    <div>
      <h2>Edit Transaction</h2>
      <form onSubmit={handleSubmit}>
      <div>
          <label htmlFor="date">Date</label>
         <input
            type="date"
            name="Post Date"
            value={postDate}
            onChange={(e) => { 
                const date = formatDate(e.target.value);
                setPostDate(date);
            }}
         />
        </div>
        <div>
          <label htmlFor="description">Description</label>
          <input
            id="description"
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="amount">Amount</label>
          <input
            id="amount"
            type="number"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
          />
        </div>
        <div>
          <label htmlFor="category">Category</label>
          <select
            id="category"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="">Select a category</option>
            {categories.map((cat) => (
              <option key={cat.id} value={cat.name}>
                {cat.name}
              </option>
            ))}
          </select>
        </div>
        <button type="submit">Save</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default UpdateTransaction;
