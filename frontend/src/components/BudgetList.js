import React, { useEffect, useState } from "react";
import { getTransactions, getBudgets, getLineItemsByBudgetId } from "../api";
import TransactionList from "./TransactionList"; // Reuse the TransactionList component
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
  const [totals, setTotals] = useState({});

  const fetchTransactions = async (startDate, endDate, budget) => {
    try {
      const response = await getTransactions(startDate, endDate);
      setTransactions(response.data);
      calculateTotals(response.data, lineItems[budget.id]);
      setError("");
    } catch (err) {
      setError("Failed to fetch transactions");
    }
  };

  const calculateTotals = (transactions, lineItems) => {
    console.log("hereeee")
    const varActMap = calculateTotalForAType("Variable", transactions, lineItems);
    console.log("done")
    console.log(varActMap)
    const varActTotal = Object.values(varActMap).reduce((sum, value) => sum + value, 0);
    console.log("varActTotal", varActTotal)
    const notRecordedMap = calculateTotalForAType("NotCounted", transactions, lineItems);
    console.log("notRecordedMap", notRecordedMap)
    const incomeTotal = lineItems.filter((x) => x.type === "Income").reduce((sum, item) => sum + item.amount, 0);
    console.log("incomeTotal", incomeTotal)
    const fixedTotal = lineItems.filter((x) => x.type === "Fixed").reduce((sum, item) => sum + item.amount, 0);
    const varTotal = lineItems.filter((x) => x.type === "Variable").reduce((sum, item) => sum + item.amount, 0);
    const budTot = incomeTotal - fixedTotal - varTotal

    const budAct = incomeTotal - fixedTotal - (varActTotal * -1)


    console.log(`income: ${incomeTotal}`)
    console.log(`fixed: ${fixedTotal}`)
    console.log(`budT: ${budTot}`)
    console.log(`budAct: ${budAct}`)

    setTotals({
      budgetTotal: budTot,
      budgetActual: budAct,
      catTotal: varActMap
    })

  };

  const txnUpdated = (txn) => {
    const newTxns = transactions.map((tx) =>
      tx.id === txn.id ? txn : tx
    )
    setTransactions(newTxns);
    calculateTotals(newTxns, lineItems[selectedBudget.id])
  }

  function calculateTotalForAType(type, transactions, lineItems) {
    try {

      // Step 1: Filter line items by the specified type and create a map of category mappings
      const categoryMap = lineItems
        .filter((item) => item.type === type)
        .reduce((acc, item) => {
          acc[item.name.toLowerCase()] = item.related_categories.map((cat) =>
            cat.toLowerCase()
          );
          return acc;
        }, {});

      // Step 2: Flatten the list of all related categories
      const allCategories = Object.values(categoryMap).flat();

      // Step 3: Group transactions by category and calculate sums
      const totalsNotCombined = transactions.reduce((acc, txn) => {
        const lowerCategory = txn.category.toLowerCase();
        if (allCategories.includes(lowerCategory)) {
          acc[lowerCategory] = (acc[lowerCategory] || 0) + txn.amount;
        }
        return acc;
      }, {});

      // Step 4: Map line items to their calculated totals
      return Object.entries(categoryMap).reduce((acc, [key, relatedCategories]) => {
        acc[key] = relatedCategories.reduce(
          (sum, cat) => sum + (totalsNotCombined[cat] || 0),
          0
        );
        return acc;
      }, {});
    } catch (error) {
      console.error("Error calculating totals for a type:", error);
      return {};
    }

  }


  useEffect(() => {
    const fetchBudgets = async () => {
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


          <table className="line-item-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Budgeted</th>
                <th></th>
                <th>Actual</th>
              </tr>
            </thead>
            <tbody>
              {lineItems[selectedBudget.id].map((item) => (
                <tr>
                  <td>{item.name}</td>
                  <td>{item.amount}</td>
                  <td></td>
                  <td>{

                    totals.catTotal[item.name] ? totals.catTotal[item.name] : item.amount

                  }</td>
                  
                </tr>
              ))}
              <tr>
                <td>Budgeted</td>
                <td>{totals.budgetTotal}</td>
                <td>Actual</td>
                <td>{totals.budgetActual}</td>
              </tr>
            </tbody>
          </table>

          <TransactionList
            txns={transactions}
            onUpdated={(txn) => txnUpdated(txn)}
          />

        </div>
      )}
    </div>
  );
};

export default BudgetList;
