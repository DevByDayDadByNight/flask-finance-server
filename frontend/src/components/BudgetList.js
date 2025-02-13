import React, { useEffect, useState } from "react";
import { getTransactions, getBudgets, getLineItemsByBudgetId } from "../api";
import TransactionList from "./TransactionList"; // Reuse the TransactionList component
import BudgetTotals from "./BudgetTotals";
import TransactionFilter from "./TransactionFilter";
import "./BudgetList.css"; // Ensure this CSS file is included
import { Link } from "react-router-dom";
import { formatDate } from "../utils";

const BudgetList = () => {
  const [budgets, setBudgets] = useState([]);
  const [selectedBudget, setSelectedBudget] = useState(null); // Track selected budget
  const [lineItems, setLineItems] = useState({});
  const [loading, setLoading] = useState(true);
  const [transactions, setTransactions] = useState([]);
  const [error, setError] = useState("");
  const [selectedCategories, setSelectedCategories] = useState([]);

  const fetchTransactions = async (startDate, endDate, budget) => {
    try {
      const response = await getTransactions(startDate, endDate);
      setTransactions(response.data);
      setError("");
    } catch (err) {
      setError("Failed to fetch transactions");
    }
  };

  const txnUpdated = (txn) => {
    const newTxns = transactions.map((tx) =>
      tx.id === txn.id ? txn : tx
    )
    setTransactions(newTxns);
  }

  useEffect(() => {
    const fetchBudgets = async () => {
      console.log("Fetching budgets...");
      try {
        const budgetResponse = await getBudgets();
        setBudgets(budgetResponse.data);

        // Fetch line items for each budget
        const lineItemsMap = {};
        for (const budget of budgetResponse.data) {
          const lineItemResponse = await getLineItemsByBudgetId(budget.id);
          lineItemsMap[budget.id] = lineItemResponse.data;
        }
        setLineItems(lineItemsMap);
      } catch (error) {
        console.error("Error fetching budgets or line items:", error);
        alert("Failed to fetch budgets or line items. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchBudgets();
  }, []);

  if (loading) {
    return <p>Loading budgets...</p>;
  }

  if (budgets.length === 0) {
    return <p>No budgets found.</p>;
  }

  return (
    <div>
      <h1>Budgets</h1>
      <div className="budget-list">
        {budgets.map((budget) => (
          <div
            key={budget.id}
            className={`budget-container ${selectedBudget?.id === budget.id ? "selected" : ""
              }`}
            onClick={() => {
              setSelectedBudget(budget)
              fetchTransactions(formatDate(budget.start_date), formatDate(budget.end_date), budget)
            }
            }
          >
            <h2>{budget.name}</h2>
            <p>
              <strong>Start Date:</strong>{" "}
              {new Date(budget.start_date).toLocaleDateString()}
            </p>
            <p>
              <strong>End Date:</strong>{" "}
              {new Date(budget.end_date).toLocaleDateString()}
            </p>

            <Link to="/create-budget" state={{ budget }} className="edit-link">
              Edit Budget
            </Link>
          </div>
        ))}
      </div>

      {selectedBudget && (
        <div style={{ marginTop: "20px" }}>
          <h2>Selected Budget: {selectedBudget.name}</h2>

          <BudgetTotals
            txns = {transactions}
            lineItems = {lineItems[selectedBudget.id]}
            selectedBudget={selectedBudget}
            />

          <TransactionFilter
            transactions={transactions}
            selectedCategories={selectedCategories}
            onChange={(cats) => setSelectedCategories(cats)}
            />
          

          <TransactionList
            txns={transactions.filter(txn => selectedCategories.length === 0 || selectedCategories.includes(txn.category))}
            onUpdated={(txn) => txnUpdated(txn)}
          />

        </div>
      )}
    </div>
  );
};

export default BudgetList;
