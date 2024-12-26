import React, { useState } from "react";
import { updateTransaction } from "../api";

const UpdateTransaction = ({ transaction, setTransactionToEdit }) => {
  const [description, setDescription] = useState(transaction.description);
  const [amount, setAmount] = useState(transaction.amount);
  const [category, setCategory] = useState(transaction.category || "");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await updateTransaction(transaction.id, { description, amount, category });
      setMessage("Transaction updated successfully");
      setTransactionToEdit(null);
    } catch (err) {
      setMessage("Failed to update transaction");
    }
  };

  return (
    <div>
      <h2>Edit Transaction</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
        <input
          type="number"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />
        <input
          type="text"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        />
        <button type="submit">Save</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default UpdateTransaction;
