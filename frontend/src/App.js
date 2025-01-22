import React, { useState } from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import { useLocation } from "react-router-dom";
import Login from "./components/Login";
import TransactionList from "./components/TransactionList";
import UploadCSV from "./components/UploadCSV";
import UpdateTransaction from "./components/UpdateTransaction";
import LogoutButton from "./components/LogoutButton";
import CategoriesPage from "./components/CategoriesPage"; // Adjust the path as needed
import BudgetCreator from "./components/BudgetCreator"; // Import BudgetCreator
import BudgetList from "./components/BudgetList"; // Import BudgetList

const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem("token"));
  const [transactionToEdit, setTransactionToEdit] = useState(null);

  if (!isLoggedIn) {
    return <Login setIsLoggedIn={setIsLoggedIn} />;
  }

  return (
    <Router>
      <div>
        <h1>React-Flask App</h1>
        <LogoutButton setIsLoggedIn={setIsLoggedIn} />
        <nav>
          <ul>
            <li>
              <Link to="/">Upload Transactions</Link>
            </li>
            <li>
              <Link to="/categories">Categories</Link>
            </li>
            <li>
              <Link to="/budgets">Budgets</Link>
            </li>
            <li>
              <Link to="/create-budget">Create Budget</Link>
            </li>
          </ul>
        </nav>
        <Routes>
          {/* Default route for transactions */}
          <Route
            path="/"
            element={
                  <UploadCSV />
            }
          />
          {/* Route for categories */}
          <Route path="/categories" element={<CategoriesPage />} />
          {/* Route for listing budgets */}
          <Route path="/budgets" element={<BudgetList />} />
          {/* Route for creating or editing budgets */}
          <Route path="/create-budget" element={<BudgetCreatorWrapper />} />
        </Routes>
      </div>
    </Router>
  );
};

const BudgetCreatorWrapper = () => {
  const location = useLocation();
  const existingBudget = location.state?.budget || null; // Access the passed budget object

  return <BudgetCreator existingBudget={existingBudget} />;
};

export default App;
