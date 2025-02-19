import React, { useEffect, useState } from "react";
import { getCategories, updateTransaction, deleteTransaction } from "../api";
import "./TransactionList.css";

const TransactionList = ({ txns, onUpdated }) => {
  const [transactions, setTransactions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [error, setError] = useState("");


  useEffect(() => {
    console.log(txns);
    // Sort transactions by postDate (ascending) and then by description (alphabetically)
    const sortedTxns = [...txns].sort((a, b) => {
      // Compare postDate first
      const dateA = new Date(a.postDate);
      const dateB = new Date(b.postDate);

      if (dateA < dateB) return -1;
      if (dateA > dateB) return 1;

      // If postDate is the same, compare description (case-insensitive)
      return a.description.localeCompare(b.description, undefined, { sensitivity: "base" });
    });

    setTransactions(sortedTxns);
  }, [txns]);


  // Fetch categories for the dropdown
  const fetchCategoriesList = async () => {
    try {
      const response = await getCategories();
      setCategories(response.data);
    } catch (err) {
      console.error("Failed to fetch categories:", err);
    }
  };

  // Handle category change
  const handleCategoryChange = async (transactionId, newCategory) => {
    try {
      await updateTransaction(transactionId, { category: newCategory });

      const txn = transactions.find(item => item.id === transactionId);
      const newTxn = { ...txn, category: newCategory }
      onUpdated(newTxn)
    } catch (err) {
      console.error("Failed to update transaction category:", err);
    }
  };

  // Handle transaction deletion
  const handleDeleteTransaction = async (transactionId) => {
    try {
      await deleteTransaction(transactionId);
      setTransactions((prev) => prev.filter((txn) => txn.id !== transactionId));
    } catch (err) {
      console.error("Failed to delete transaction:", err);
    }
  };

  // Fetch transactions and categories on mount or when date range changes
  useEffect(() => {
    fetchCategoriesList();
  }, []);

  return (
    <div>
      <h2>Transactions</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}

      <table className="transaction-table">
        <thead>
          <tr>
            <th>Post Date</th>
            <th>Description</th>
            <th>Amount</th>
            <th>Category</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((txn, index) => (
            <tr key={txn.id}>
              <td>{txn.postDate}</td>
              <td>{txn.description}</td>
              <td>${txn.amount.toFixed(2)}</td>
              <td>
                <select
                  value={txn.category || ""}
                  onChange={(e) => handleCategoryChange(txn.id, e.target.value)}
                >
                  <option value="" disabled>
                    Select a category
                  </option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.name}>
                      {cat.name}
                    </option>
                  ))}
                </select>
              </td>
              <td>
                <button onClick={() => handleDeleteTransaction(txn.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

    </div>
  );
};

export default TransactionList;
