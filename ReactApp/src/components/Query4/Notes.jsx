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
          <SheetTitle>Query 4 Notes</SheetTitle>
          <SheetDescription></SheetDescription>
        </SheetHeader>
        <div
          className="grid gap-4 py-4"
          style={{ overflowY: "scroll", maxHeight: "calc(100vh - 65px)" }}
        >
          <ul>
            <li>
              Our analysis looks at the number of deaths and new
              hospitalizations in different states. This ratio, called the 'D:H
              ratio,' helps us gauge the immediate outcome of hospital care.
            </li>
            <li>
              We've grouped states into four categories based on the number of
              physicians per 100,000 people: Low, Decent, Good, and Very Good.
              This grouping is crucial for understanding variations in the D:H
              ratio with different healthcare resource levels.
            </li>
            <li>
              Expectations vs reality:
              <ul>
                <li>
                  While common belief suggests a simple inverse correlation —
                  more physicians leading to fewer deaths relative to
                  hospitalizations — our data tells a more complex story.
                </li>
                <li>
                  We can see that the D:H ratio is higher for the 'Very Good'
                  category than for the other categories. While for the other 3
                  categories ('Low', 'Decent', 'Good'), their D:H ratio values
                  are very similar to each other.
                </li>
                <li>
                  The initial peak in D:H values between Mar20-Jun20 suggests
                  that the medical community wasn’t properly equipped to handle
                  a pandemic.
                </li>
                <li>The other peaks probably indicate next covid waves.</li>
              </ul>
            </li>
            <li>
              Inference:
              <ul>
                <li>
                  These variations suggest that physician numbers alone don't
                  determine patient outcomes. Other factors, like the quality of
                  medical resources, access to essentials like oxygen, the
                  responsiveness of the healthcare system to surges in
                  hospitalization also play a pivotal role and probably
                  overshadow the positive effects that having a higher number of
                  physicians would have had on the D:H ratio.
                </li>
                <li>
                  The graph, when considered in conjunction with other
                  healthcare resource, demographic, and economic metrics can be
                  used to make policy decisions like allocation of healthcare
                  resources and medical personnel.
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </SheetContent>
    </Sheet>
  );
}
