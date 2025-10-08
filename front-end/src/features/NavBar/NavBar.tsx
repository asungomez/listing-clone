import { FC } from "react";
import { Link } from "react-router";
import { TopBar } from "../../atoms/TopBar/TopBar";
import logo from "../../assets/logo.svg";
import { Menu } from "../../atoms/Menu/Menu";

const MENU_ITEMS = [
  { label: "My Listings", href: "/my-listings" },
  { label: "All JLL Properties", href: "/properties" },
  { label: "Team Listings", href: "/team-listings" },
  { label: "Reports", href: "/reports" },
];

export const NavBar: FC = () => {
  return (
    <TopBar>
      <div className="flex w-full items-center justify-between">
        <div className="flex items-center gap-8">
          <Link
            to="/"
            className="flex items-center space-x-3 rtl:space-x-reverse"
          >
            <img src={logo} className="h-8" alt="My Listings Logo" />
            <span className="self-center text-2xl font-semibold whitespace-nowrap text-white">
              My Listings
            </span>
          </Link>
          <Menu items={MENU_ITEMS} />
        </div>
        <div>{/* user menu goes here */}</div>
      </div>
    </TopBar>
  );
};
