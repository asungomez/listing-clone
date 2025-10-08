import {
  FC,
  PropsWithChildren,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import { createPortal } from "react-dom";
import { Alert, AlertColor } from "../../atoms/Alert/Alert";
import { AlertContext } from "./AlertContext";

type AlertItem = {
  id: string;
  text: string;
  severity: AlertColor;
  timeoutId?: number;
};

const AUTO_DISMISS_MS = 4000;

export const AlertProvider: FC<PropsWithChildren> = ({ children }) => {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);

  const removeAlert = useCallback((id: string) => {
    setAlerts((currentAlerts) => {
      const alertToRemove = currentAlerts.find((a) => a.id === id);
      if (alertToRemove?.timeoutId) {
        clearTimeout(alertToRemove.timeoutId);
      }
      return currentAlerts.filter((a) => a.id !== id);
    });
  }, []);

  const addAlert = useCallback(
    (text: string, severity: AlertColor = "info") => {
      const id = `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
      const timeoutId = window.setTimeout(() => {
        removeAlert(id);
      }, AUTO_DISMISS_MS);
      setAlerts((currentAlerts) => [
        { id, text, severity, timeoutId },
        ...currentAlerts,
      ]);
    },
    [removeAlert]
  );

  useEffect(() => {
    return () => {
      alerts.forEach((a) => a.timeoutId && clearTimeout(a.timeoutId));
    };
  }, [alerts]);

  const contextValue = useMemo(() => ({ addAlert }), [addAlert]);

  const portalContent = (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col items-end">
      {alerts.map((alert) => (
        <div key={alert.id} className="mt-2">
          <Alert
            color={alert.severity}
            dismissable
            onDismiss={() => removeAlert(alert.id)}
          >
            {alert.text}
          </Alert>
        </div>
      ))}
    </div>
  );

  return (
    <AlertContext.Provider value={contextValue}>
      {children}
      {createPortal(portalContent, document.body)}
    </AlertContext.Provider>
  );
};
