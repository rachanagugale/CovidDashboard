import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import "./index.css";

import { ThemeProvider } from "@/components/theme-provider";
import NavigationBar from "@/components/NavigationBar";
import Query1 from "@/components/Query1";
import Query2 from "@/components/Query2";
import Query3 from "@/components/Query3";

const routes = [
  {
    label: "Home",
    path: "/",
    element: <>Hello World</>,
  },
  {
    label: "Query 1",
    path: "/query1",
    element: <Query1 />,
  },
  {
    label: "Query 2",
    path: "/query2",
    element: <Query2 />,
  },
  {
    label: "Query 3",
    path: "/query3",
    element: <Query3 />,
  },
  {
    label: "Query 4",
    path: "/query4",
    element: <Query3 />,
  },
  {
    label: "Query 5",
    path: "/query5",
    element: <Query3 />,
  },
];

const router = createBrowserRouter(routes);

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <main>
        <NavigationBar routes={routes} />
        <div className="content">
          <RouterProvider router={router} />
        </div>
      </main>
    </ThemeProvider>
  </React.StrictMode>
);
