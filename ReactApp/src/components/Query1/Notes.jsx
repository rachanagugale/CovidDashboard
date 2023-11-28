import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";

export default function Notes() {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outline">
          <span class="material-symbols-outlined">info</span>
        </Button>
      </SheetTrigger>
      <SheetContent>
        <SheetHeader>
          <SheetTitle>Query 1 Notes</SheetTitle>
          <SheetDescription></SheetDescription>
        </SheetHeader>
        <div
          className="grid gap-4 py-4"
          style={{ overflowY: "scroll", maxHeight: "calc(100vh - 65px)" }}
        >
          Mobility types
          <ul>
            <li>
              <strong>mobility_grocery_and_pharmacy</strong> - Percentage change
              in visits to places like grocery markets, food warehouses, farmers
              markets, specialty food shops, drug stores, and pharmacies
              compared to baseline.
            </li>
            <li>
              <strong>mobility_parks</strong> - Percentage change in visits to
              places like local parks, national parks, public beaches, marinas,
              dog parks, plazas, and public gardens compared to baseline.
            </li>
            <li>
              <strong>mobility_transit_stations</strong> - Percentage change in
              visits to places like public transport hubs such as subway, bus,
              and train stations compared to baseline.
            </li>
            <li>
              <strong>mobility_retail_and_recreation</strong> - Percentage
              change in visits to restaurants, cafes, shopping centers, theme
              parks, museums, libraries, and movie theaters compared to
              baseline.
            </li>
            <li>
              <strong>mobility_residential</strong> - Percentage change in
              visits to places of residence compared to baseline.
            </li>
            <li>
              <strong>mobility_workplaces</strong> - Percentage change in visits
              to places of work compared to baseline.
            </li>
          </ul>
          The baseline is the median value, for the corresponding day of the
          week
        </div>
      </SheetContent>
    </Sheet>
  );
}
