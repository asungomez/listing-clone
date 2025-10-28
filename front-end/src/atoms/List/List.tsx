import clsx from "clsx";
import { FC, useMemo } from "react";
import { Link } from "react-router";

type ListProps = React.DetailedHTMLProps<
  React.HTMLAttributes<HTMLUListElement>,
  HTMLUListElement
> & {
  children: React.ReactNode;
};

export const List: FC<ListProps> = ({ children, className, ...rest }) => {
  const classNames = clsx(
    className,
    "w-48 text-sm font-medium border rounded-lg bg-gray-700 border-gray-600 text-white"
  );
  return (
    <ul className={classNames} {...rest}>
      {children}
    </ul>
  );
};

type ListItemProps =
  | ({
      linkTo: React.ComponentProps<typeof Link>["to"];
    } & Omit<
      React.ComponentProps<typeof Link>,
      "to" | "className" | "children"
    > & {
        className?: string;
        children: React.ReactNode;
      })
  | (React.HTMLAttributes<HTMLDivElement> & {
      linkTo?: undefined;
      className?: string;
      children: React.ReactNode;
    });

export const ListItem: FC<ListItemProps> = ({
  children,
  className,
  linkTo,
  ...rest
}) => {
  const isLink = useMemo(() => linkTo !== undefined, [linkTo]);
  const liClassNames = clsx(
    className,
    "w-full border-b border-gray-600 first:rounded-t-lg last:rounded-b-lg last:border-b-0 overflow-hidden"
  );

  if (isLink) {
    const linkProps = rest as Omit<
      React.ComponentProps<typeof Link>,
      "to" | "className" | "children"
    >;
    return (
      <li className={liClassNames}>
        <Link
          to={linkTo as React.ComponentProps<typeof Link>["to"]}
          className={
            "block w-full px-4 py-2 cursor-pointer focus:outline-none focus:ring-2 hover:bg-gray-600 hover:text-white focus:ring-gray-500 focus:text-white"
          }
          {...linkProps}
        >
          {children}
        </Link>
      </li>
    );
  }

  const liProps = rest as React.HTMLAttributes<HTMLLIElement>;
  return (
    <li className={clsx(liClassNames, "px-4 py-2")} {...liProps}>
      {children}
    </li>
  );
};
