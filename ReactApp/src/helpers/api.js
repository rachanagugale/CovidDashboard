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

export const getQuery2 = (state, start_date, end_date) => {
  return api.post("/query2", {
    state,
    start_date,
    end_date,
  });
};

export const getQuery3 = () => {
  return api.get("/query3");
};

export const getQuery4 = (start_date, end_date) => {
  return api.post("/query4", {
    start_date,
    end_date,
    physician_categories: [
      "Low (<200)",
      "Decent (200-300)",
      "Good (300-400)",
      "Very good (>400)",
    ],
  });
};

export const getQuery5 = (party, start_date, end_date) => {
  return api.post("/query5", {
    start_date,
    end_date,
    party,
  });
};
