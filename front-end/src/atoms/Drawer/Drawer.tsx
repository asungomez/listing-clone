import { FC, ReactNode } from "react";
import { clsx } from "clsx";

type DrawerProps = React.DetailedHTMLProps<
  React.HTMLAttributes<HTMLDivElement>,
  HTMLDivElement
> & {
  open: boolean;
  children: ReactNode;
  onClose?: () => void;
};

export const Drawer: FC<DrawerProps> = ({
  open,
  children,
  className,
  onClose,
  ...rest
}) => {
  return (
    <div
      className={clsx(
        "fixed inset-0 z-50",
        open ? "pointer-events-auto" : "pointer-events-none"
      )}
      aria-hidden={!open}
    >
      {/* overlay */}
      <div
        className={clsx(
          "absolute inset-0 bg-black/40 transition-opacity duration-300",
          open ? "opacity-100" : "opacity-0"
        )}
        onClick={onClose}
      />
      {/* panel */}
      <div
        className={clsx(
          "absolute left-0 top-0 h-full w-80 max-w-[90vw] bg-gray-900 text-white shadow-xl",
          "transition-transform duration-300 ease-in-out",
          open ? "translate-x-0" : "-translate-x-full",
          className
        )}
        {...rest}
      >
        {children}
      </div>
    </div>
  );
};
