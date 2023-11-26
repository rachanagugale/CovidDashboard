import { useEffect, useRef, useState } from "react";
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

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

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

import Loading from "./Loading";

import { getQuery1 } from "../helpers/api";
import "./Query1.css";

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

const states = [
  "California",
  "Rhode Island",
  "Tennessee",
  "New York",
  "South Dakota",
  "Arizona",
  "Pennsylvania",
  "Texas",
  "Virginia",
  "Kansas",
  "Montana",
  "Oregon",
  "Washington",
  "Wisconsin",
  "Connecticut",
  "Minnesota",
  "South Carolina",
  "Iowa",
  "Massachusetts",
  "West Virginia",
  "Nevada",
  "Arkansas",
  "Hawaii",
  "Wyoming",
  "Colorado",
  "Michigan",
  "District of Columbia",
  "Idaho",
  "Ohio",
  "North Carolina",
  "Illinois",
  "Oklahoma",
  "Florida",
  "Kentucky",
  "Louisiana",
  "Alabama",
  "Alaska",
  "Georgia",
  "Maryland",
  "New Jersey",
  "New Hampshire",
  "North Dakota",
  "New Mexico",
  "Delaware",
  "Indiana",
  "Maine",
  "Nebraska",
  "Mississippi",
  "Utah",
  "Vermont",
  "Missouri",
];

export default function Query3() {
  const [data, setData] = useState(null);
  const [isLoading, setLoading] = useState(true);
  const [form, setForm] = useState({ state: "Florida" });

  useEffect(() => {
    setLoading(true);
    getQuery1(form.state)
      .then((data) => {
        const dates = data.map(({ date }) => new Date(date).toDateString());
        const pick = (data, attr) => data.map((res) => res[attr]);

        const infected_population_percent = pick(
          data,
          "infected_population_percent"
        );
        const mobility_grocery_and_pharmacy = pick(
          data,
          "mobility_grocery_and_pharmacy"
        );
        const mobility_parks = pick(data, "mobility_parks");
        const mobility_residential = pick(data, "mobility_residential");
        const mobility_retail_and_recreation = pick(
          data,
          "mobility_retail_and_recreation"
        );
        const mobility_transit_stations = pick(
          data,
          "mobility_transit_stations"
        );
        const mobility_workplaces = pick(data, "mobility_workplaces");

        setData({
          labels: dates,
          datasets: [
            {
              label: "Infected Population Percent",
              data: infected_population_percent,
              borderWidth: 2,
              pointRadius: 0,
            },
            {
              label: "Mobility Grocery and Pharmacy",
              data: mobility_grocery_and_pharmacy,
              borderWidth: 2,
              pointRadius: 0,
            },
            {
              label: "Monthly Parks",
              data: mobility_parks,
              borderWidth: 2,
              pointRadius: 0,
            },
            {
              label: "Mobility Residential",
              data: mobility_residential,
              borderWidth: 2,
              pointRadius: 0,
            },
            {
              label: "Mobility Retail and Recreation",
              data: mobility_retail_and_recreation,
              borderWidth: 2,
              pointRadius: 0,
            },
            {
              label: "Mobility Transit Stations",
              data: mobility_transit_stations,
              borderWidth: 2,
              pointRadius: 0,
            },
            {
              label: "Mobility Workspaces",
              data: mobility_workplaces,
              borderWidth: 2,
              pointRadius: 0,
            },
          ],
        });
      })
      .finally(() => {
        setLoading(false);
      });
  }, [form]);

  if (!data) return <Loading />;

  return (
    <div className="query-1">
      <div className="options">
        <h2>Options</h2>

        <Select
          onValueChange={(val) => setForm({ ...form, state: val })}
          defaultValue={form.state}
        >
          <SelectTrigger>
            <SelectValue placeholder="State" />
          </SelectTrigger>
          <SelectContent>
            {states.map((state) => (
              <SelectItem key={state} value={state}>
                {state}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Alert style={{ position: "fixed", bottom: "1rem", width: "250px" }}>
          <AlertTitle
            style={{
              fontSize: "15px",
              marginBottom: "1rem",
              textDecoration: "underline",
            }}
          >
            Heads up!
          </AlertTitle>
          <AlertDescription>
            You can toggle the trends by clicking on the legend in the chart.
          </AlertDescription>
        </Alert>
      </div>

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
