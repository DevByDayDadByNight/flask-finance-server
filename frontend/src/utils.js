export const formatDate = (date) => {
    const d = new Date(date); // Ensure the input date is in ISO format or similar
  const year = d.getUTCFullYear();
  const month = String(d.getUTCMonth() + 1).padStart(2, "0"); // Add leading zero
  const day = String(d.getUTCDate()).padStart(2, "0"); // Add leading zero
  return `${year}-${month}-${day}`;
  };

  export const formatMoney = (amount) => {
    return `$${amount.toFixed(2)}`;
  }