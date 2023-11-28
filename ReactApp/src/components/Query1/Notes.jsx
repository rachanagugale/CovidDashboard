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
          <SheetDescription>Add some desc here</SheetDescription>
        </SheetHeader>
        <div className="grid gap-4 py-4">add notes here</div>
      </SheetContent>
    </Sheet>
  );
}
