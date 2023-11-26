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
import { getQuery1 } from "../../helpers/api";
import "./Query1.css";

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
  plugins: {
    colors: {
      enabled: true,
    },
    legend: {
      position: "top",
    },
    title: {
      display: true,
      text: "Query 1",
    },
  },
};

const formatData = (data) => {
  const dates = _.map(data, ({ date }) => new Date(date).toDateString());
  const [
    infected_population_percent,
    mobility_grocery_and_pharmacy,
    mobility_parks,
    mobility_residential,
    mobility_retail_and_recreation,
    mobility_transit_stations,
    mobility_workplaces,
  ] = _.map(
    [
      "infected_population_percent",
      "mobility_grocery_and_pharmacy",
      "mobility_parks",
      "mobility_residential",
      "mobility_retail_and_recreation",
      "mobility_transit_stations",
      "mobility_workplaces",
    ],
    (attr) => _.map(data, (row) => _.get(row, attr))
  );

  const datasets = [
    ["Infected Population Percent", infected_population_percent],
    ["Mobility Grocery and Pharmacy", mobility_grocery_and_pharmacy],
    ["Monthly Parks", mobility_parks],
    ["Mobility Residential", mobility_residential],
    ["Mobility Retail and Recreation", mobility_retail_and_recreation],
    ["Mobility Transit Stations", mobility_transit_stations],
    ["Mobility Workspaces", mobility_workplaces],
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

export default function Query3() {
  const [data, setData] = useState(null);
  const [isLoading, setLoading] = useState(true);
  const [form, setForm] = useState({
    state: "Florida",
    start_date: "11-FEB-21",
    end_date: "11-MAR-21",
  });

  useEffect(() => {
    setLoading(true);
    getQuery1(form.state, form.start_date, form.end_date)
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
    <div className="query-1">
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
          <>
            <p style={{ width: "100%", textAlign: "left" }}>
              Percentage of state population infected and how it affects
              mobility across various sectors calculated for every week.
            </p>
            <Line options={options} data={data} />
          </>
        )}
      </div>
    </div>
  );
}
