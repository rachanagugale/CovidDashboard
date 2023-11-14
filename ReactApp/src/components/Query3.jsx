import { useEffect, useRef, useState } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

import { getQuery3 } from "../helpers/api";

const options = {
  responsive: true,
  plugins: {
    legend: {
      position: "top",
    },
    title: {
      display: true,
      text: "Chart.js Line Chart",
    },
  },
};

export default function Query3() {
  const [data, setData] = useState(null);

  useEffect(() => {
    getQuery3().then((data) => {
      const dates = data.map(({ date }) => new Date(date).toDateString());
      const avg_stock_prices = data.map(
        ({ avg_stock_prices }) => avg_stock_prices
      );
      const icu_patients = data.map(({ icu_patients }) => icu_patients);
      const monthly_new_cases = data.map(
        ({ monthly_new_cases }) => monthly_new_cases
      );

      setData({
        labels: dates,
        datasets: [
          {
            label: "Average Stock Prices",
            data: avg_stock_prices,
            borderColor: "rgba(255, 99, 132, 1)",
            borderWidth: 2,
          },
          {
            label: "ICU Patients",
            data: icu_patients,
            borderColor: "rgba(54, 162, 235, 1)",
            borderWidth: 2,
          },
          {
            label: "Monthly New Cases",
            data: monthly_new_cases,
            borderColor: "rgba(255, 206, 86, 1)",
            borderWidth: 2,
          },
        ],
      });
    });
  }, []);

  if (!data) return <>Loading</>;

  return (
    <>
      <Line options={options} data={data} />
    </>
  );
}
