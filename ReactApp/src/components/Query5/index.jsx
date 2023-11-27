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
import { getQuery5 } from "../../helpers/api";
import "./Query5.css";

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
        text: "Mortality rate per 100000 people",
      },
    },
    y1: {
      type: "linear",
      display: true,
      position: "right",
      grid: {
        drawOnChartArea: false,
      },
      title: {
        display: true,
        text: "Number of states",
      },
    },
  },
};

const formatData = (data) => {
  const dates = _.map(data, ({ date }) => new Date(date).toDateString());
  const [cat_1, cat_2, cat_3, cat_4, cat_5, count] = _.map(
    ["0-19", "20-39", "40-59", "60-79", "80-100", "count"],
    (attr) => _.map(data, (row) => _.get(row, attr))
  );

  const datasets = [
    ["0-19", cat_1],
    ["20-39", cat_2],
    ["40-59", cat_3],
    ["60-79", cat_4],
    ["80-100", cat_5],
  ];

  return {
    labels: dates,
    datasets: _.map(datasets, ([label, data]) => ({
      label,
      data,
      borderWidth: 2,
      pointRadius: 0,
      yAxisID: "y",
    })).concat([
      {
        label: "Count of States",
        data: count,
        borderWidth: 2,
        pointRadius: 0,
        yAxisID: "y1",
      },
    ]),
  };
};

export default function Query2() {
  const [data, setData] = useState(null);
  const [isLoading, setLoading] = useState(true);
  const [form, setForm] = useState({
    start_date: "01-JAN-20",
    end_date: "01-JAN-23",
    party: "D",
  });

  useEffect(() => {
    setLoading(true);
    getQuery5(form.party, form.start_date, form.end_date)
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
    <div className="query-5">
      <Options
        party={form.party}
        setParty={(party) => setForm({ ...form, party })}
        dates={_.pick(form, ["start_date", "end_date"])}
        setDate={(start_date, end_date) =>
          setForm({ ...form, start_date, end_date })
        }
      />

      <div className="chart">
        {isLoading && <Loading />}
        {!isLoading && (
          <div style={{ width: "100%", textAlign: "left" }}>
            <h2 style={{ marginBottom: "10px" }}>Query 5 Utility</h2>
            <p className="text-sm text-muted-foreground mb-20">
              Query to compare the mortality rate in democratic vs republican
              states based on their stringency index per week
            </p>
            <Line options={options} data={data} />
          </div>
        )}
      </div>
    </div>
  );
}
