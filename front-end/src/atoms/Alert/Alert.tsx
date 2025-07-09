import { FC, ReactNode, useState } from "react";
import { FaInfoCircle } from "react-icons/fa";
import { MdOutlineReportGmailerrorred } from "react-icons/md";
import { IoWarning } from "react-icons/io5";
import { FaCheck } from "react-icons/fa";
import { IoIosClose } from "react-icons/io";

const ALERT_COLORS = ["info", "danger", "success", "warning"] as const;
type AlertColor = (typeof ALERT_COLORS)[number];
const ALERT_COLOR_MAP: Record<AlertColor, string> = {
  info: "blue",
  danger: "red",
  success: "green",
  warning: "yellow",
};
const DEFAULT_ICON_MAP: Record<AlertColor, ReactNode> = {
  info: <FaInfoCircle />,
  danger: <MdOutlineReportGmailerrorred />,
  warning: <IoWarning />,
  success: <FaCheck />,
};
const SCREEN_READER_TEXT_MAP: Record<AlertColor, string> = {
  info: "Info",
  danger: "Error",
  warning: "Warning",
  success: "Success",
};

type AlertProps = {
  color?: AlertColor;
  icon?: ReactNode;
  children?: ReactNode;
  dismissable?: boolean;
  title?: string;
};

export const Alert: FC<AlertProps> = ({
  color = "info",
  icon: iconOverride,
  children,
  dismissable = false,
  title: titleOverride,
}) => {
  const [show, setShow] = useState(true);
  const alertColor = ALERT_COLOR_MAP[color];
  const alertClasses = `text-${alertColor}-400 border-${alertColor}-800`;
  const buttonClasses = `focus:ring-${alertColor}-400`;
  const titleClasses = children ? "text-lg font-bold" : "text-sm font-normal";
  const icon = iconOverride ?? DEFAULT_ICON_MAP[color];
  const title = titleOverride ?? SCREEN_READER_TEXT_MAP[color];

  const handleDismiss = () => {
    setShow(false);
  };

  return show ? (
    <div
      className={`${alertClasses} p-4 mb-4 border rounded-lg bg-gray-800`}
      role="alert"
    >
      <div className="flex flex-row items-center align-middle">
        <div
          className={`${titleClasses} flex items-center align-middle justify-start`}
        >
          <div className="inline me-3">{icon}</div>
          <span>{title}</span>
        </div>
        {dismissable && (
          <div className="flex flex-row items-center align-middle">
            <button
              type="button"
              className={`${buttonClasses} ms-auto ml-3 -mr-1.5 -my-1.5 rounded-lg focus:ring-2 p-1.5  inline-flex items-center justify-center h-8 w-8 bg-gray-800  hover:bg-gray-700`}
              aria-label="Close"
              onClick={handleDismiss}
            >
              <span className="sr-only">Close</span>
              <IoIosClose />
            </button>
          </div>
        )}
      </div>
      {children && <div className="text-sm font-normal mt-3">{children}</div>}
    </div>
  ) : null;
};
