import { useState, useEffect } from "react";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
  SheetFooter,
} from "@/components/ui/sheet";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Separator } from "@/components/ui/separator";
import _ from "lodash";

import { count } from "@/helpers/api";
import Loading from "@/components/Loading";
import "./NavigationBar.css";

export default function NavigationBar({ routes }) {
  const [counts, setCount] = useState(false);
  const [segment, setSegment] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    count()
      .then((data) => {
        setCount(data);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [segment]);

  return (
    <nav>
      <a href="/" id="logo">
        <span className="material-symbols-outlined">token</span>
      </a>
      <Sheet>
        <div className="links">
          {routes
            .filter(({ path }) => path != "/")
            .map(({ label, path }) => (
              <a key={label} href={path}>
                {label}
              </a>
            ))}
          <SheetTrigger>Get Table Counts</SheetTrigger>
        </div>

        <SheetContent>
          <SheetHeader>
            <SheetTitle>Covid19 Dashboard</SheetTitle>
            <SheetDescription>
              Real time fetch of counts from backend
            </SheetDescription>
          </SheetHeader>

          {loading && <Loading />}
          {!loading && (
            <Alert className="my-10">
              <AlertDescription>
                <div className="flex flex-row justify-between">
                  <label>Tables</label>
                  <p>Counts</p>
                </div>
                <Separator className="my-4" />
                {_.toPairs(counts).map(([key, value]) => (
                  <div key={key} className="flex flex-row justify-between">
                    <label>{key}</label>
                    <p>{value}</p>
                  </div>
                ))}
                <Separator className="my-4" />
                <div className="flex flex-row justify-between">
                  <label>TOTAL</label>
                  <p>{_.sum(_.values(counts))}</p>
                </div>
              </AlertDescription>
            </Alert>
          )}
          <SheetFooter>
            <button
              className="my-10 refresh-count-button"
              onClick={() => setSegment(segment + 1)}
            >
              Refresh Count
            </button>
          </SheetFooter>
        </SheetContent>
      </Sheet>
    </nav>
  );
}
