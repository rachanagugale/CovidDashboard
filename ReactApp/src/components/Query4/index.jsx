import { useEffect, useState } from "react";
import {
  Colors,
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
import _ from "lodash";

import Loading from "@/components/Loading";
import Options from "./Options";
import { getQuery4 } from "../../helpers/api";
import "./Query4.css";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Colors
);

const options = {
  responsive: true,
  interaction: {
    mode: "index",
    intersect: false,
  },
  stacked: false,
  scales: {
    x: {
      title: {
        display: true,
        text: "Time",
      },
    },
    y: {
      type: "linear",
      display: true,
      position: "left",

      title: {
        display: true,
        text: "Average Ratio of Deaths to Hospitalized People",
      },
    },
  },
};

const formatData = (data) => {
  const dates = _.map(data, ({ date }) => new Date(date).toDateString());
  const [low, decent, good, very_good] = _.map(
    ["Low (<200)", "Decent (200-300)", "Good (300-400)", "Very good (>400)"],
    (attr) => _.map(data, (row) => _.get(row, attr, null))
  );

  const datasets = [
    ["Low (<200)", low],
    ["Decent (200-300)", decent],
    ["Good (300-400)", good],
    ["Very good (>400)", very_good],
  ];

  return {
    labels: dates,
    datasets: _.map(datasets, ([label, data]) => ({
      label,
      data,
      borderWidth: 2,
      pointRadius: 0,
    })),
  };
};

export default function Query4() {
  const [data, setData] = useState(null);
  const [isLoading, setLoading] = useState(true);
  const [form, setForm] = useState({
    start_date: "01-JAN-2020",
    end_date: "31-DEC-2020",
    physician_categories: [
      "Low (<200)",
      "Decent (200-300)",
      "Good (300-400)",
      "Very good (>400)",
    ],
  });

  useEffect(() => {
    setLoading(true);
    getQuery4(form.start_date, form.end_date)
      .then((data) => {
        const formattedData = formatData(data);
        setData(formattedData);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [form]);

  if (!data) return <Loading />;

  return (
    <div className="query-4">
      <Options
        dates={_.pick(form, ["start_date", "end_date"])}
        setDate={(start_date, end_date) =>
          setForm({ ...form, start_date, end_date })
        }
      />

      <div className="chart">
        {isLoading && <Loading />}
        {!isLoading && (
          <div style={{ width: "100%", textAlign: "left" }}>
            <h2 style={{ marginBottom: "10px" }}>Query 4 Utility</h2>
            <p className="text-sm text-muted-foreground mb-20">
              Ratio of number of deaths among hospitalized patients to the
              number of newly hospitalized patients for US states grouped into 4
              categories according to the number of physicians per 100000
              people.
            </p>
            <Line options={options} data={data} />
          </div>
        )}
      </div>
    </div>
  );
}
