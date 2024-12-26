import axios from "axios";

const API = axios.create({
  baseURL: "http://127.0.0.1:5000", // Flask backend URL
});

// Add Authorization header if token is present
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const login = (username, password) =>
  API.post("/login", { username, password });

export const getTransactions = () => API.get("/transactions");

export const uploadCSV = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return API.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const updateTransaction = (id, updatedFields) =>
  API.put(`/update_transaction/${id}`, updatedFields);

export default API;
