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
          <SheetTitle>Query 5 Notes</SheetTitle>
          <SheetDescription></SheetDescription>
        </SheetHeader>
        <div
          className="grid gap-4 py-4"
          style={{ overflowY: "scroll", maxHeight: "calc(100vh - 65px)" }}
        >
          <ul>
            <li>
              <strong>Query:</strong> Comparing mortality rates in democratic
              vs. republican states based on their monthly stringency index.
            </li>
            <li>
              <strong>Usefulness:</strong> Correlating stringency indices with
              mortality rates provides a visual tool to assess the effectiveness
              of measures across states with different political leanings.
            </li>
            <li>
              <strong>Objective:</strong> Drawing comparisons based on two
              parameters:
              <ol>
                <li>Number of states categorized by their Stringency Index.</li>
                <li>
                  Aggregate mortality rate trends in Democratic versus
                  Republican states.
                </li>
              </ol>
            </li>
            <li>
              <strong>Temporal Trends:</strong>
              <ul>
                <li>Mortality peaks and troughs at different points.</li>
                <li>
                  Stringency index varies over time, reflecting evolving policy
                  responses to the pandemic.
                </li>
              </ul>
            </li>
            <li>
              <strong>Stringency Index Analysis:</strong>
              <ul>
                <li>
                  Stringency peaks after mortality rate increases, suggesting
                  reactive policy tightening.
                </li>
                <li>
                  Lower stringency indices don't always correspond with higher
                  mortality rates, indicating other factors at play.
                </li>
              </ul>
            </li>
            <li>
              <strong>Mortality Rate Analysis:</strong>
              <ul>
                <li>
                  Mortality rates appear cyclical, reflecting waves of COVID-19
                  infections.
                </li>
                <li>
                  Noticeable decrease in mortality rates in the latter half of
                  2021, possibly linked to vaccination rollouts and improved
                  treatment protocols.
                </li>
              </ul>
            </li>
            <li>
              <strong>Differences Between Political Leaning:</strong>
              <ul>
                <li>
                  Democratic states show a trend with higher stringency indices
                  (40-100) more common.
                </li>
                <li>
                  Republican states exhibit lower stringency indices (0-39) more
                  frequently, suggesting a more relaxed policy approach.
                </li>
              </ul>
            </li>
            <li>
              <strong>Critical Analysis and Conclusion:</strong>
              <ul>
                <li>
                  Visual trends suggest a relationship between policy stringency
                  and mortality outcomes, but a direct causal link cannot be
                  asserted.
                </li>
                <li>
                  Consideration of demographic variations, healthcare
                  infrastructure, and public compliance is crucial in policy
                  decisions.
                </li>
              </ul>
            </li>
          </ul>
        </div>
      </SheetContent>
    </Sheet>
  );
}
