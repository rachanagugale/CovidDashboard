import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import "./Home.css";

export default function Home() {
  return (
    <div className="home">
      <h2 className="mb-12">COVID 19 Dashboard</h2>
      <div style={{ width: "50%" }}>
        <Alert>
          <AlertDescription style={{ fontSize: "16px", textAlign: "center" }}>
            Welcome to the COVID-19 Dashboard. This interactive tool provides a
            complex analysis on the COVID-19 global pandemic, offering
            comprehensive insights of the situation. Stay informed, stay safe.
            Together, we can overcome this crisis. 😊
          </AlertDescription>
        </Alert>

        <div className="mt-20" style={{ textAlign: "center" }}>
          <b className="my-5 block" style={{ textDecoration: "underline" }}>
            PROJECT BY GROUP 8
          </b>
          <p>Ammar Amjad – 59921730</p>
          <p>Mohammad Uzair Fasih - 62861020</p>
          <p>Rachana Gugale - 63532454</p>
          <p>Imthiaz Hussasin Hussain - 43681284</p>
        </div>
      </div>
    </div>
  );
}
