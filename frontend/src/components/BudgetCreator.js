import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createBudget, updateBudget, createLineItem, updateLineItem, getLineItemsByBudgetId } from "../api"; // Import API functions
import { formatDate } from "../utils";


const BudgetCreator = ({ existingBudget }) => {
    const navigate = useNavigate();
    const [budget, setBudget] = useState({
      name: "",
      startDate: "",
      endDate: "",
    });
  
    const [lineItems, setLineItems] = useState([]);
  
    const lineItemTypes = ["Income", "Variable", "Fixed", "NotCounted"]; // Enum values
  
    // Populate fields if editing an existing budget
    useEffect(() => {
      if (existingBudget) {
        setBudget({
          name: existingBudget.name,
          startDate: existingBudget.start_date,
          endDate: existingBudget.end_date,
        });
  
        const fetchLineItems = async () => {
          try {
            const response = await getLineItemsByBudgetId(existingBudget.id);
            const moved = response.data
            const updatedMoved = moved.map(item => ({
              ...item, // Keep all other properties of the item
              related_categories: Array.isArray(item.related_categories)
                ? item.related_categories.join(", ")
                : item.related_categories // Ensure it's unchanged if not an array
            }));
            setLineItems(updatedMoved);
          } catch (error) {
            console.error("Error fetching line items:", error);
          }
        };
  
        fetchLineItems();
      }
    }, [existingBudget]);
  
    const handleLineItemChange = (index, field, value) => {
      const updatedLineItems = [...lineItems];
      updatedLineItems[index][field] = value;
      setLineItems(updatedLineItems);
    };
  
    const addLineItem = () => {
      setLineItems([
        ...lineItems,
        { id: null, name: "", amount: "", type: "Variable", related_categories: "" },
      ]);
    };
  
    const deleteLineItem = (index) => {
      setLineItems(lineItems.filter((_, i) => i !== index));
    };
  
    const saveBudget = async () => {
      try {
        let budgetId;
  
        if (existingBudget) {
          await updateBudget(existingBudget.id, {
            name: budget.name,
            start_date: budget.startDate,
            end_date: budget.endDate,
          });
          budgetId = existingBudget.id;
        } else {
          const budgetResponse = await createBudget({
            name: budget.name,
            start_date: budget.startDate,
            end_date: budget.endDate,
          });
          budgetId = budgetResponse.data.id;
        }
  
        for (const item of lineItems) {
          const cat = item.related_categories && typeof item.related_categories === "string"
          ? item.related_categories.split(",").map((c) => c.trim())
          : item.related_categories
          if (item.id) {
           
            await updateLineItem(item.id, {
              budget_id: budgetId,
              name: item.name,
              amount: parseFloat(item.amount),
              type: item.type,
              related_categories: cat,
            });
          } else {
            await createLineItem({
              budget_id: budgetId,
              name: item.name,
              amount: parseFloat(item.amount),
              type: item.type,
              related_categories: cat,
            });
          }
        }
  
        navigate("/budgets");
        if (!existingBudget) {
          setBudget({ name: "", startDate: "", endDate: "" });
          setLineItems([]);
        }
      } catch (error) {
        console.error("Error saving budget:", error);
        alert("Failed to save the budget and line items. Please try again.");
      }
    };
  
    return (
      <div>
        <h1>{existingBudget ? "Edit Budget" : "Create Budget"}</h1>
        <div>
          <label>
            Budget Name:
            <input
              type="text"
              name="name"
              value={budget.name}
              onChange={(e) => setBudget({ ...budget, name: e.target.value })}
            />
          </label>
        </div>
        <div>
          <label>
            Start Date:
            <input
              type="date"
              name="startDate"
              value={formatDate(budget.startDate)}
              onChange={(e) => setBudget({ ...budget, startDate: e.target.value })}
            />
          </label>
        </div>
        <div>
          <label>
            End Date:
            <input
              type="date"
              name="endDate"
              value={formatDate(budget.endDate)}
              onChange={(e) => setBudget({ ...budget, endDate: e.target.value })}
            />
          </label>
        </div>
  
        <h2>Line Items</h2>
        {lineItems.map((item, index) => (
          <div key={index} style={{ marginBottom: "10px" }}>
            <input
              type="text"
              placeholder="Name"
              value={item.name}
              onChange={(e) => handleLineItemChange(index, "name", e.target.value)}
            />
            <input
              type="number"
              placeholder="Amount"
              value={item.amount}
              onChange={(e) => handleLineItemChange(index, "amount", e.target.value)}
            />
            <select
              value={item.type}
              onChange={(e) => handleLineItemChange(index, "type", e.target.value)}
            >
              {lineItemTypes.map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
            <input
              type="text"
              placeholder="Related Categories (comma-separated)"
              value={item.related_categories || ""}
              onChange={(e) =>
                handleLineItemChange(index, "related_categories", e.target.value)
              }
            />
            <button onClick={() => deleteLineItem(index)}>Delete</button>
          </div>
        ))}
        <button onClick={addLineItem}>Add Line Item</button>
  
        <div style={{ marginTop: "20px" }}>
          <button onClick={saveBudget}>
            {existingBudget ? "Update Budget" : "Save Budget"}
          </button>
        </div>
      </div>
    );
  };
  
  export default BudgetCreator;
  