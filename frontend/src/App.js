import React, { useState } from "react";
import { BrowserRouter as Router, Route, Routes, Link } from "react-router-dom";
import { useLocation } from "react-router-dom";
import Login from "./components/Login";
import UploadCSV from "./components/UploadCSV";
import CategoriesPage from "./components/CategoriesPage"; // Adjust the path as needed
import BudgetCreator from "./components/BudgetCreator"; // Import BudgetCreator
import BudgetList from "./components/BudgetList"; // Import BudgetList
import "bootstrap/dist/css/bootstrap.min.css";
import { Navbar, Nav, Container, Button } from "react-bootstrap";
import TransactionSearch from "./components/TransactionSearch";



const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem("token"));

  if (!isLoggedIn) {
    return <Login setIsLoggedIn={setIsLoggedIn} />;
  }

  return (
    <Router>
      <div>
      <Navbar bg="dark" variant="dark" expand="lg">
      <Container>
        {/* Brand / Logo */}
        <Navbar.Brand as={Link} to="/">
          Budget Tracker
        </Navbar.Brand>

        {/* Toggle button for mobile view */}
        <Navbar.Toggle aria-controls="basic-navbar-nav" />

        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link as={Link} to="/">Budgets</Nav.Link>
            <Nav.Link as={Link} to="/categories">Categories</Nav.Link>
            <Nav.Link as={Link} to="/upload">Upload</Nav.Link>
            <Nav.Link as={Link} to="/create-budget">Create Budget</Nav.Link>
            <Nav.Link as={Link} to="/transactions">Transactions</Nav.Link>
          </Nav>

          {/* Logout Button */}
          <Button variant="outline-light" onClick={() => setIsLoggedIn(false)}>
            Logout
          </Button>
        </Navbar.Collapse>
      </Container>
    </Navbar>
        <Routes>
          {/* Default route for transactions */}
          <Route
            path="/"
            element={
                  <BudgetList />
            }
          />
          {/* Route for categories */}
          <Route path="/categories" element={<CategoriesPage />} />
          {/* Route for listing budgets */}
          <Route path="/upload" element={<UploadCSV />} />
          {/* Route for creating or editing budgets */}
          <Route path="/create-budget" element={<BudgetCreatorWrapper />} />
          {/* Route for transactions */}
          <Route path="/transactions" element={<TransactionSearch />} />
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
