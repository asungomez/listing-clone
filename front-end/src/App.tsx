import { FC } from "react";
import { Router } from "./router/router";
import { AlertProvider } from "./context/alert/AlertProvider";

export const App: FC = () => {
  return (
    <AlertProvider>
      <Router />
    </AlertProvider>
  );
};
