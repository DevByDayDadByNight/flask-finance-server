import axios from "axios";

const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL, // Flask backend URL
});

// Add Authorization header if token is present
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const login = (username, password) =>
  API.post("/login", { username, password });

// Transactions
export const getTransactions = (start_date, end_date) =>
  API.get(`/transactions?start_date=${start_date}&end_date=${end_date}`);

export const deleteTransaction = (id) => 
  API.delete(`/transactions/${id}`)

export const uploadCSV = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return API.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const updateTransaction = (id, updatedFields) =>
  API.put(`/update_transaction/${id}`, updatedFields);

// Categories
export const getCategories = () => API.get("/categories");

export const addCategory = (name) =>
  API.post("/categories", { name });

// Budgets
export const getBudgets = () => API.get("/budgets");

export const getBudgetById = (id) => API.get(`/budgets/${id}`);

export const createBudget = (budget) =>
  API.post("/budgets", budget);

export const updateBudget = (id, updatedFields) =>
  API.put(`/budgets/${id}`, updatedFields);

export const deleteBudget = (id) =>
  API.delete(`/budgets/${id}`);

// Line Items
export const getLineItems = () => API.get("/line_items");

export const getLineItemsByBudgetId = (budgetId) =>
  API.get(`/line_items?budget_id=${budgetId}`);

export const createLineItem = (lineItem) =>
  API.post("/line_items", lineItem);

export const updateLineItem = (id, updatedFields) =>
  API.put(`/line_items/${id}`, updatedFields);

export const deleteLineItem = (id) =>
  API.delete(`/line_items/${id}`);

export default API;
