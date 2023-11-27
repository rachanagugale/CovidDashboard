import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { format } from "date-fns";
import { Calendar as CalendarIcon } from "lucide-react";

import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

import "./Options.css";

function DatePickerWithRange({ className, dates, setDate }) {
  const date = {
    from: new Date(dates.start_date),
    to: new Date(dates.end_date),
  };

  const setDateHandler = ({ from, to }) => {
    const start_date = format(from, "dd-MMM-yy").toUpperCase();
    const end_date = format(to, "dd-MMM-yy").toUpperCase();
    setDate(start_date, end_date);
  };

  return (
    <div className={cn("grid gap-2", className)}>
      <Popover>
        <PopoverTrigger asChild>
          <Button
            id="date"
            variant={"outline"}
            className={cn(
              "w-[300px] justify-start text-left font-normal",
              !date && "text-muted-foreground"
            )}
          >
            <CalendarIcon className="mr-2 h-4 w-4" />
            {date?.from ? (
              date.to ? (
                <>
                  {format(date.from, "LLL dd, y")} -{" "}
                  {format(date.to, "LLL dd, y")}
                </>
              ) : (
                format(date.from, "LLL dd, y")
              )
            ) : (
              <span>Pick a date</span>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            initialFocus
            mode="range"
            defaultMonth={date?.from}
            selected={date}
            onSelect={setDateHandler}
            numberOfMonths={2}
          />
        </PopoverContent>
      </Popover>
    </div>
  );
}

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

export default function Options({ dates, setDate }) {
  return (
    <div className="options">
      <h2>Options</h2>

      <p className="label">Date Range</p>
      <DatePickerWithRange dates={dates} setDate={setDate} />

      <Alert style={{ position: "fixed", bottom: "30px", width: "295px" }}>
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
  );
}