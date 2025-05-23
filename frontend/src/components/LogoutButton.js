import React from "react";

const LogoutButton = ({ setIsLoggedIn }) => {
  const handleLogout = async () => {
    try {
      await localStorage.removeItem("token");
      await localStorage.removeItem("refreshToken");
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
