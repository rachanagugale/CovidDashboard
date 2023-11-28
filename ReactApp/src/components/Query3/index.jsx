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
import { getQuery3 } from "../../helpers/api";
import "./Query3.css";

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
        text: "Percentage of companies in profit",
      },
    },
    y1: {
      type: "linear",
      display: true,
      position: "right",
      title: {
        display: true,
        text: "Number of tested people per 100000 people",
      },
      grid: {
        drawOnChartArea: false,
      },
    },
  },
};

const formatData = (data) => {
  const dates = [];
  const no_of_tested_people_per_100000_people = []; // Y1-axis

  const consumer_discretionary = [];
  const consumer_staples = [];
  const energy = [];
  const financials = [];
  const health_care = [];
  const industrials = [];
  const information_technology = [];
  const materials = [];
  const real_estate = [];
  const telecommunication_services = [];
  const utilities = [];

  for (const date in data) {
    dates.push(new Date(date).toDateString());
    no_of_tested_people_per_100000_people.push(
      _.get(data[date], "no_of_tested_people_per_100000_people", 0)
    );

    const _add = (arr, attr) => {
      arr.push(
        _.get(
          data[date],
          ["sectorwise_percent_of_companies_in_profit", attr],
          0
        )
      );
    };

    _add(consumer_discretionary, "Consumer Discretionary");
    _add(consumer_staples, "Consumer Staples");
    _add(energy, "Energy");
    _add(financials, "Financials");
    _add(health_care, "Health Care");
    _add(industrials, "Industrials");
    _add(information_technology, "Information Technology");
    _add(materials, "Materials");
    _add(real_estate, "Real Estate");
    _add(telecommunication_services, "Telecommunication Services");
    _add(utilities, "Utilities");
  }

  const datasets = [
    [consumer_discretionary, "Consumer Discretionary"],
    [consumer_staples, "Consumer Staples"],
    [energy, "Energy"],
    [financials, "Financials"],
    [health_care, "Health Care"],
    [industrials, "Industrials"],
    [information_technology, "Information Technology"],
    [materials, "Materials"],
    [real_estate, "Real Estate"],
    [telecommunication_services, "Telecommunication Services"],
    [utilities, "Utilities"],
  ];

  const colors = [
    "#4c9fe9",
    "#fb6585",
    "#56bfbf",
    "#faa247",
    "#9f5efd",
    "#facf5c",
    "#c9cbcf",
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
    "#aec7e8",
    "#ffbb78",
  ];

  return {
    labels: dates,
    datasets: _.map(datasets, ([data, label], index) => ({
      label,
      data,
      borderWidth: 2,
      pointRadius: 0,
      borderColor: colors[index],
      backgroundColor: colors[index],
      hidden: label != "Health Care",
    })).concat([
      {
        label: "Number of tested people per 100000 people",
        data: no_of_tested_people_per_100000_people,
        borderWidth: 2,
        pointRadius: 0,
        yAxisID: "y1",
        borderColor: colors[12],
        backgroundColor: colors[12],
      },
    ]),
  };
};

export default function Query3() {
  const [data, setData] = useState(null);
  const [isLoading, setLoading] = useState(true);
  const [form, setForm] = useState({
    from: new Date("01-JAN-2020"),
    to: new Date("01-JUN-2020"),
  });

  useEffect(() => {
    if (form.from && form.to) {
      setLoading(true);
      getQuery3(
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
    <div className="query-3">
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
                <h2 style={{ marginBottom: "10px" }}>Query 3 Utility</h2>
                <p className="text-sm text-muted-foreground mb-12">
                  This query shows the number of people tested per 100000 for
                  the entire US vs the percentage of companies from a sector
                  whose stocks made a profit for the day.
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
