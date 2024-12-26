import React from "react";

const LogoutButton = ({ setIsLoggedIn }) => {
  const handleLogout = async () => {
    try {
      await localStorage.removeItem("token"); // Notify the backend (optional)
    } catch (error) {
      console.error("Error logging out:", error);
    } finally {
      setIsLoggedIn(false); // Update the app state
    }
  };

  return (
    <button onClick={handleLogout} className="logout-button">
      Logout
    </button>
  );
};

export default LogoutButton;
