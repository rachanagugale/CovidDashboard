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
import { getQuery2 } from "../../helpers/api";
import "./Query2.css";

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
  plugins: {
    title: {
      display: true,
      text: "Query 2",
    },
  },
  scales: {
    y: {
      type: "linear",
      display: true,
      position: "left",
    },
    y1: {
      type: "linear",
      display: true,
      position: "right",
      grid: {
        drawOnChartArea: false,
      },
    },
  },
};

// const labels = ["January", "February", "March", "April", "May", "June", "July"];

// const data = {
//   labels,
//   datasets: [
//     {
//       label: "Dataset 1",
//       data: labels.map(() => 12),
//       borderColor: "rgb(255, 99, 132)",
//       backgroundColor: "rgba(255, 99, 132, 0.5)",
//       yAxisID: "y",
//     },
//     {
//       label: "Dataset 2",
//       data: labels.map(() => 12),
//       borderColor: "rgb(53, 162, 235)",
//       backgroundColor: "rgba(53, 162, 235, 0.5)",
//       yAxisID: "y1",
//     },
//   ],
// };

const formatData = (data) => {
  const dates = _.map(data, ({ date }) => new Date(date).toDateString());
  const [
    avg_monthly_sni_covid19_vaccination,
    avg_monthly_sni_safety_side_effects,
    avg_monthly_sni_vaccination_intent,
    vaccination_rate,
  ] = _.map(
    [
      "avg_monthly_sni_covid19_vaccination",
      "avg_monthly_sni_safety_side_effects",
      "avg_monthly_sni_vaccination_intent",
      "vaccination_rate",
    ],
    (attr) => _.map(data, (row) => _.get(row, attr))
  );

  const datasets = [
    [
      "Average Monthly SNI Covid 19 Vaccination",
      avg_monthly_sni_covid19_vaccination,
    ],
    [
      "Average Monthly SNI Safety Side Effects",
      avg_monthly_sni_safety_side_effects,
    ],
    [
      "Average Monthly SNI Vaccination Intent",
      avg_monthly_sni_vaccination_intent,
    ],
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
        label: "Vaccination Rate",
        data: vaccination_rate,
        borderWidth: 2,
        pointRadius: 0,
        yAxisID: "y1",
      },
    ]),
  };
};

export default function Query3() {
  const [data, setData] = useState(null);
  const [isLoading, setLoading] = useState(true);
  const [form, setForm] = useState({
    state: "Florida",
    start_date: "11-FEB-21",
    end_date: "11-DEC-21",
  });

  useEffect(() => {
    setLoading(true);
    getQuery2(form.state, form.start_date, form.end_date)
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
    <div className="query-2">
      <Options
        state={form.state}
        setState={(state) => setForm({ ...form, state })}
        dates={_.pick(form, ["start_date", "end_date"])}
        setDate={(start_date, end_date) =>
          setForm({ ...form, start_date, end_date })
        }
      />

      <div className="chart">
        {isLoading && <Loading />}
        {!isLoading && (
          <div style={{ width: "100%", textAlign: "left" }}>
            <h2 style={{ marginBottom: "10px" }}>Query 2 Utility</h2>
            <p className="text-sm text-muted-foreground">
              Helps in understanding of the dynamics surrounding vaccination
              efforts. Monitoring "general_vaccine_interest" helps gauge overall
              public awareness, while "vaccination_intent_interest" indicates
              the population's willingness to get vaccinated. Simultaneously,
              tracking "safety_side_effects_interest" assists in addressing
              concerns related to vaccine safety. By correlating these trends
              with vaccination rates, policymakers can tailor communication
              strategies, targeting areas with low intent or high safety
              concerns. The data also enables rapid response to emerging issues,
              supports predictive modeling, and allows for informed allocation
              of resources, ultimately aiding in fostering vaccination uptake
              and addressing hesitancy effectively.
            </p>
            <Line options={options} data={data} />
          </div>
        )}
      </div>
    </div>
  );
}