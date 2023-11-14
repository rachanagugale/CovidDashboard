import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:5000/",
});

api.interceptors.response.use(
  (response) => response.data,
  (err) => Promise.reject(err)
);

export const getQuery3 = () => {
  return api.get("/query3");
};
