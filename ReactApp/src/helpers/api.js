import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:5000/",
});

api.interceptors.response.use(
  (response) => response.data,
  (err) => Promise.reject(err)
);

export const getQuery1 = (state, start_date, end_date) => {
  return api.post("/query1", {
    state,
    start_date,
    end_date,
    mobility_types: [
      "mobility_retail_and_recreation",
      "mobility_grocery_and_pharmacy",
      "mobility_parks",
      "mobility_transit_stations",
      "mobility_workplaces",
      "mobility_residential",
    ],
  });
};

export const getQuery3 = () => {
  return api.get("/query3");
};
