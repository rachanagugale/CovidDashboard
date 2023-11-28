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
import Notes from "./Notes";
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
        text: "Mobility",
      },
    },
    y1: {
      type: "linear",
      display: true,
      position: "right",
      title: {
        display: true,
        text: "Infected Population Percentage",
      },
      grid: {
        drawOnChartArea: false,
      },
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
    })).concat([
      {
        label: "Infected Population Percent",
        data: infected_population_percent,
        borderWidth: 2,
        pointRadius: 0,
        yAxisID: "y1",
      },
    ]),
  };
};

export default function Query1() {
  const [data, setData] = useState(null);
  const [isLoading, setLoading] = useState(true);
  const [form, setForm] = useState({
    state: "Florida",
    from: new Date("01-JAN-21"),
    to: new Date("01-JAN-23"),
  });

  useEffect(() => {
    if (form.from && form.to) {
      setLoading(true);
      getQuery1(
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
    <div className="query-1">
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
                <h2 style={{ marginBottom: "10px" }}>Query 1</h2>
                <p className="text-sm text-muted-foreground mb-12">
                  Percentage of state population infected and how it affects
                  mobility across various sectors calculated for every week.
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
