import axios from "axios";

const API = axios.create({
  baseURL: process.env.REACT_APP_API_URL, // Flask backend URL
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Add Authorization header if token is present
API.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Add response interceptor to handle token refresh
API.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is not 401 or request has already been retried, reject
    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      })
        .then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return API(originalRequest);
        })
        .catch((err) => Promise.reject(err));
    }

    originalRequest._retry = true;
    isRefreshing = true;

    const refreshToken = localStorage.getItem("refreshToken");
    if (!refreshToken) {
      return Promise.reject(error);
    }

    try {
      const response = await axios.post(`${process.env.REACT_APP_API_URL}/refresh`, {}, {
        headers: {
          Authorization: `Bearer ${refreshToken}`
        }
      });

      const { access_token, refresh_token } = response.data;
      localStorage.setItem("token", access_token);
      localStorage.setItem("refreshToken", refresh_token);

      processQueue(null, access_token);
      originalRequest.headers.Authorization = `Bearer ${access_token}`;
      return API(originalRequest);
    } catch (err) {
      processQueue(err, null);
      localStorage.removeItem("token");
      localStorage.removeItem("refreshToken");
      window.location.reload();
      return Promise.reject(err);
    } finally {
      isRefreshing = false;
    }
  }
);

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
  API.put(`/transactions/${id}`, updatedFields);

export const createTransaction = (updatedFields) =>
  API.post(`/transactions`, updatedFields);

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
  API.get(`/line_items/${budgetId}`);

export const createLineItem = (lineItem) =>
  API.post("/line_items", lineItem);

export const updateLineItem = (id, updatedFields) =>
  API.put(`/line_items/${id}`, updatedFields);

export const deleteLineItem = (id) =>
  API.delete(`/line_items/${id}`);

export default API;
