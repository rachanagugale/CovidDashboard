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
        text: "Time (month)",
      },
    },
    y: {
      type: "linear",
      display: true,
      position: "left",

      title: {
        display: true,
        text: "SNI",
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
        text: "Vaccination Rate",
      },
    },
  },
};

const colors = ["#797ef6", "#4adede", "#1aa7ec", "#faa247"];

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
    datasets: _.map(datasets, ([label, data], index) => ({
      label,
      data,
      borderWidth: 2,
      pointRadius: 0,
      yAxisID: "y",
      borderColor: colors[index],
      backgroundColor: colors[index],
    })).concat([
      {
        label: "Vaccination Rate",
        data: vaccination_rate,
        borderColor: colors[3],
        backgroundColor: colors[3],
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
    state: "Florida",
    from: new Date("11-FEB-21"),
    to: new Date("11-DEC-22"),
  });

  useEffect(() => {
    if (form.from && form.to) {
      setLoading(true);
      getQuery2(
        form.state,
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
    <div className="query-2">
      <Options
        state={form.state}
        setState={(state) => setForm({ ...form, state })}
        dates={_.pick(form, ["from", "to"])}
        setDate={(dates) => setForm({ ...form, ...dates })}
      />

      <div className="chart">
        {isLoading && <Loading />}
        {!isLoading && (
          <div style={{ width: "100%", textAlign: "left" }}>
            <div className="flex flex-row">
              <div style={{ width: "100%", textAlign: "left" }}>
                <h2 style={{ marginBottom: "10px" }}>Query 2</h2>
                <p className="text-sm text-muted-foreground mb-12">
                  Query to understand people's interest in vaccination-related
                  information and its relationship with the vaccination rate.
                  Searches about vaccination-related info are divided into 3
                  types:
                  <ul>
                    <li>
                      <strong>1. SNI Covid19 Vaccination - </strong> The scaled
                      normalized interest related to all COVID-19 vaccinations
                      topics for the region and date.
                    </li>
                    <li>
                      <strong>2. SNI Safety Side Effects - </strong> The scaled
                      normalized interest related to safety and side effects of
                      the vaccines for the region and date.
                    </li>
                    <li>
                      <strong>3. SNI Vaccination Intent - </strong> The scaled
                      normalized interest for all searches related to
                      eligibility, availability, and accessibility for the
                      region and date.
                    </li>
                  </ul>
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
