import { FC } from "react";
import { NavLink } from "react-router";
import { clsx } from "clsx";

type MenuItemBase = { label: string; disabled?: boolean };
export type MenuItem =
  | (MenuItemBase & { href: string; onClick?: never })
  | (MenuItemBase & { onClick: () => void; href?: never });

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
                    item.disabled
                      ? "text-gray-400 cursor-not-allowed pointer-events-none"
                      : isActive
                      ? "text-blue-500"
                      : "text-white border-0 hover:text-blue-500"
                  )
                }
                aria-current="page"
                aria-disabled={item.disabled ?? undefined}
                onClick={item.disabled ? (e) => e.preventDefault() : undefined}
                tabIndex={item.disabled ? -1 : undefined}
              >
                {item.label}
              </NavLink>
            ) : (
              <button
                type="button"
                disabled={item.disabled}
                onClick={item.onClick}
                className={clsx(
                  "block py-2 px-3 rounded-sm cursor-pointer",
                  item.disabled
                    ? "text-gray-400 cursor-not-allowed"
                    : "text-white border-0 hover:text-blue-500"
                )}
                aria-disabled={item.disabled ?? undefined}
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
