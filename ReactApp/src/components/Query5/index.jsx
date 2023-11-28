import { useEffect, useState } from "react";
import {
  Colors,
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Chart } from "react-chartjs-2";
import { format } from "date-fns";
import _ from "lodash";

import Loading from "@/components/Loading";
import Options from "./Options";
import Notes from "./Notes";
import { getQuery5 } from "../../helpers/api";
import "./Query5.css";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  Colors,
  Title,
  Tooltip,
  Legend
);

ChartJS.defaults.font.size = 14; // Set the font size to 16px
ChartJS.defaults.color = "rgb(148, 163, 184)"; // Set the font color to white

const options = {
  responsive: true,
  interaction: {
    mode: "index",
    intersect: true,
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
      title: {
        display: true,
        text: "Number of states",
      },
    },
    y1: {
      display: true,
      position: "right",
      grid: {
        drawOnChartArea: false,
      },
      title: {
        display: true,
        text: "Mortality rate per 100000 people",
      },
    },
  },
};

const formatData = (data) => {
  const dates = [];
  const mortality_rate = [];
  const stringency_cat_0_19 = [];
  const stringency_cat_20_39 = [];
  const stringency_cat_40_59 = [];
  const stringency_cat_60_79 = [];
  const stringency_cat_80_100 = [];

  const colors = [
    "#4c9fe9",
    "#fb6585",
    "#56bfbf",
    "#faa247",
    "#9f5efd",
    "#facf5c",
    "#c9cbcf",
  ];

  for (const date in data) {
    dates.push(new Date(date).toDateString());
    const _get = (arr, key) => {
      arr.push(_.get(data[date], ["stringency_categories", key], 0));
    };

    _get(stringency_cat_0_19, "0-19");
    _get(stringency_cat_20_39, "20-39");
    _get(stringency_cat_40_59, "40-59");
    _get(stringency_cat_60_79, "60-79");
    _get(stringency_cat_80_100, "80-100");
    mortality_rate.push(_.get(data[date], "mortality_rate_100000", 0));
  }

  const datasets = [
    [stringency_cat_0_19, "0-19"],
    [stringency_cat_20_39, "20-39"],
    [stringency_cat_40_59, "40-59"],
    [stringency_cat_60_79, "60-79"],
    [stringency_cat_80_100, "80-100"],
  ];

  return {
    labels: dates,
    datasets: [
      {
        type: "line",
        label: "Mortality Rate",
        borderColor: "#FFF",
        borderWidth: 2,
        fill: false,
        data: mortality_rate,
        yAxisID: "y1",
      },
    ].concat(
      _.map(datasets, ([data, label], idx) => ({
        type: "bar",
        label,
        data,
        stack: "Stack 0",
        borderColor: colors[idx],
        backgroundColor: colors[idx],
      }))
    ),
  };
};

export default function Query5() {
  const [data, setData] = useState(null);
  const [isLoading, setLoading] = useState(true);
  const [form, setForm] = useState({
    from: new Date("01-JAN-20"),
    to: new Date("01-JAN-23"),
    party: "D",
  });

  useEffect(() => {
    if (form.from && form.to) {
      setLoading(true);
      getQuery5(
        form.party,
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
    <div className="query-5">
      <Options
        party={form.party}
        setParty={(party) => setForm({ ...form, party })}
        dates={_.pick(form, ["from", "to"])}
        setDate={(dates) => setForm({ ...form, ...dates })}
      />

      <div className="chart">
        {isLoading && <Loading />}
        {!isLoading && (
          <div style={{ width: "100%", textAlign: "left" }}>
            <div className="flex flex-row">
              <div style={{ width: "100%", textAlign: "left" }}>
                <h2 style={{ marginBottom: "10px" }}>Query 5</h2>
                <p className="text-sm text-muted-foreground mb-12">
                  Comparing the mortality rate in democratic vs republican
                  states based on their stringency index per month.
                </p>
              </div>
              <Notes />
            </div>

            <Chart type="bar" options={options} data={data} />
          </div>
        )}
      </div>
    </div>
  );
}
