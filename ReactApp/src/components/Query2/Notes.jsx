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
          <SheetTitle>Query 2 Notes</SheetTitle>
          <SheetDescription></SheetDescription>
        </SheetHeader>
        <div
          className="grid gap-4 py-4"
          style={{ overflowY: "scroll", maxHeight: "calc(100vh - 65px)" }}
        >
          <ul>
            <li>
              Helps in understanding of the dynamics surrounding vaccination
              efforts.
            </li>
            <li>
              Monitoring "general_vaccine_interest" helps gauge overall public
              awareness.
            </li>
            <li>
              "vaccination_intent_interest" indicates the population's
              willingness to get vaccinated.
            </li>
            <li>
              Simultaneously, tracking "safety_side_effects_interest" assists in
              addressing concerns related to vaccine safety.
            </li>
            <li>
              By correlating these trends with vaccination rates, policymakers
              can tailor communication strategies, targeting areas with low
              intent or high safety concerns.
            </li>
            <li>
              The data also enables rapid response to emerging issues, supports
              predictive modeling, and allows for informed allocation of
              resources, ultimately aiding in fostering vaccination uptake and
              addressing hesitancy effectively.
            </li>
          </ul>
        </div>
      </SheetContent>
    </Sheet>
  );
}
