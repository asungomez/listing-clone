import { createContext, useContext } from "react";
import { AlertColor } from "../../atoms/Alert/Alert";

type AlertContextType = {
  addAlert: (text: string, severity?: AlertColor) => void;
};

export const AlertContext = createContext<AlertContextType>({
  addAlert: () => {},
});

export const useAlert = () => useContext(AlertContext);
