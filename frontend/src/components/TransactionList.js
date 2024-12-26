import React, { useEffect, useState } from "react";
import { getTransactions } from "../api";

const TransactionList = ({ setTransactionToEdit }) => {
  const [transactions, setTransactions] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        const response = await getTransactions();
        setTransactions(response.data);
      } catch (err) {
        setError("Failed to fetch transactions");
      }
    };
    fetchTransactions();
  }, []);

  return (
    <div>
      <h2>Transactions</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <ul>
        {transactions.map((txn) => (
          <li key={txn.id}>
            {txn.description} - ${txn.amount} - {txn.category || "Uncategorized"}
            <button onClick={() => setTransactionToEdit(txn)}>Edit</button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default TransactionList;
