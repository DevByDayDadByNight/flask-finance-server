import React, { useState } from "react";
import Login from "./components/Login";
import TransactionList from "./components/TransactionList";
import UploadCSV from "./components/UploadCSV";
import UpdateTransaction from "./components/UpdateTransaction";
import LogoutButton from "./components/LogoutButton";

const App = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(!!localStorage.getItem("token"));
  const [transactionToEdit, setTransactionToEdit] = useState(null);

  if (!isLoggedIn) {
    return <Login setIsLoggedIn={setIsLoggedIn} />;
  }

  return (
    <div>
      <h1>React-Flask App</h1>
      <LogoutButton setIsLoggedIn={setIsLoggedIn} /> {/* Add Logout Button */}
      {transactionToEdit ? (
        <UpdateTransaction
          transaction={transactionToEdit}
          setTransactionToEdit={setTransactionToEdit}
        />
      ) : (
        <>
          <TransactionList setTransactionToEdit={setTransactionToEdit} />
          <UploadCSV />
        </>
      )}
    </div>
  );
};

export default App;
