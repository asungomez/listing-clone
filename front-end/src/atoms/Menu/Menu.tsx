import { FC } from "react";
import { NavLink } from "react-router";
import { clsx } from "clsx";

export type MenuItem =
  | { label: string; href: string; onClick?: never }
  | { label: string; onClick: () => void; href?: never };

type MenuProps = React.DetailedHTMLProps<
  React.HTMLAttributes<HTMLDivElement>,
  HTMLDivElement
> & {
  items: MenuItem[];
  orientation?: "vertical" | "horizontal";
};

export const Menu: FC<MenuProps> = ({
  items,
  className,
  orientation = "horizontal",
  ...rest
}) => {
  return (
    <div className={clsx(className)} {...rest}>
      <ul
        className={clsx("font-medium flex gap-6", {
          "flex-col items-start": orientation === "vertical",
          "flex-row items-center": orientation === "horizontal",
        })}
      >
        {items.map((item) => (
          <li key={"href" in item ? item.href : item.label}>
            {"href" in item ? (
              <NavLink
                to={item.href as string}
                className={({ isActive }) =>
                  clsx(
                    "block py-2 px-3 rounded-sm",
                    isActive
                      ? "text-blue-500"
                      : "text-white border-0 hover:text-blue-500"
                  )
                }
                aria-current="page"
              >
                {item.label}
              </NavLink>
            ) : (
              <button
                type="button"
                onClick={item.onClick}
                className={clsx(
                  "block py-2 px-3 rounded-sm",
                  "text-white border-0 hover:text-blue-500"
                )}
              >
                {item.label}
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};
