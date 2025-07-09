import { FC } from "react";
import { Spinner } from "../Spinner/Spinner";
import { NavLink } from "react-router";

type ButtonProps = React.DetailedHTMLProps<
  React.AnchorHTMLAttributes<HTMLAnchorElement>,
  HTMLAnchorElement
> & { loading?: boolean; to?: string };

export const Button: FC<ButtonProps> = ({
  loading,
  children,
  to,
  href,
  onClick,
  ...anchorProps
}) => {
  const DEFAULT_CLASS_NAME =
    "inline-flex items-center text-white bg-[#1d4ed8] hover:bg-[#1e40af] focus:ring-4 font-medium rounded-lg text-sm px-5 py-2.5 text-center focus:ring-[#1e3a8a] cursor-pointer";
  const className = anchorProps.className
    ? `${DEFAULT_CLASS_NAME} ${anchorProps.className}`
    : DEFAULT_CLASS_NAME;

  if (to && !href && !onClick) {
    return (
      <NavLink className={className} to={to} {...anchorProps}>
        {loading && <Spinner className="mr-2" />}
        {children}
      </NavLink>
    );
  }
  return (
    <a className={className} href={href} onClick={onClick} {...anchorProps}>
      {loading && <Spinner className="mr-2" />}
      {children}
    </a>
  );
};
