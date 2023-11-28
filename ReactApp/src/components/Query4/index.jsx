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
import { format } from "date-fns";
import _ from "lodash";

import Loading from "@/components/Loading";
import Options from "./Options";
import Notes from "./Notes";
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

ChartJS.defaults.font.size = 14; // Set the font size to 16px
ChartJS.defaults.color = "rgb(148, 163, 184)"; // Set the font color to white

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
    (attr) => _.map(data, (row) => _.get(row, attr, 0))
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
    from: new Date("01-JAN-2020"),
    to: new Date("31-DEC-2020"),
    physician_categories: [
      "Low (<200)",
      "Decent (200-300)",
      "Good (300-400)",
      "Very good (>400)",
    ],
  });

  useEffect(() => {
    if (form.from && form.to) {
      setLoading(true);
      getQuery4(
        format(form.from, "dd-MMM-yy").toUpperCase(),
        format(form.to, "dd-MMM-yy").toUpperCase()
      )
        .then((data) => {
          const formattedData = formatData(data);
          setData(formattedData);
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [form]);

  if (!data) return <Loading />;

  return (
    <div className="query-4">
      <Options
        dates={_.pick(form, ["from", "to"])}
        setDate={(dates) => setForm({ ...form, ...dates })}
      />

      <div className="chart">
        {isLoading && <Loading />}
        {!isLoading && (
          <div style={{ width: "100%", textAlign: "left" }}>
            <div className="flex flex-row">
              <div style={{ width: "100%", textAlign: "left" }}>
                <h2 style={{ marginBottom: "10px" }}>Query 4 Utility</h2>
                <p className="text-sm text-muted-foreground mb-12">
                  Ratio of number of deaths among hospitalized patients to the
                  number of newly hospitalized patients for US states grouped
                  into 4 categories according to the number of physicians per
                  100000 people.
                </p>
              </div>
              <Notes />
            </div>

            <Line options={options} data={data} />
          </div>
        )}
      </div>
    </div>
  );
}
