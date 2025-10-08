import { FC } from "react";
import { NavLink } from "react-router";
import { clsx } from "clsx";

type MenuProps = React.DetailedHTMLProps<
  React.HTMLAttributes<HTMLDivElement>,
  HTMLDivElement
> & {
  items: {
    label: string;
    href: string;
  }[];
};

export const Menu: FC<MenuProps> = ({ items }) => {
  return (
    <div className="hidden md:block">
      <ul className="font-medium flex items-center gap-6">
        {items.map((item) => (
          <li key={item.href}>
            <NavLink
              to={item.href}
              className={({ isActive }) =>
                clsx(
                  "block py-2 px-3 rounded-sm md:p-0",
                  isActive
                    ? "text-white md:text-blue-500"
                    : "text-white hover:bg-gray-700 hover:text-white md:border-0 md:hover:bg-transparent md:hover:text-blue-500"
                )
              }
              aria-current="page"
            >
              {item.label}
            </NavLink>
          </li>
        ))}
      </ul>
    </div>
  );
};
