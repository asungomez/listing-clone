import { FC, useState } from "react";
import { Link } from "react-router";
import { TopBar } from "../../atoms/TopBar/TopBar";
import logo from "../../assets/logo.svg";
import { Menu } from "../../atoms/Menu/Menu";
import { Drawer } from "../../atoms/Drawer/Drawer";

const MENU_ITEMS = [
  { label: "My Listings", href: "/my-listings" },
  { label: "All JLL Properties", href: "/properties" },
  { label: "Team Listings", href: "/team-listings" },
  { label: "Reports", href: "/reports" },
];

export const NavBar: FC = () => {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  return (
    <TopBar>
      <div className="flex w-full items-center justify-between">
        <div className="flex items-center gap-8">
          <button
            type="button"
            className="md:hidden inline-flex items-center justify-center p-2 text-white hover:bg-gray-800 rounded-sm"
            aria-label="Toggle menu"
            onClick={() => setIsDrawerOpen(true)}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="currentColor"
              className="size-6"
            >
              <path
                fillRule="evenodd"
                d="M3.75 6.75A.75.75 0 0 1 4.5 6h15a.75.75 0 0 1 0 1.5h-15a.75.75 0 0 1-.75-.75Zm0 5.25a.75.75 0 0 1 .75-.75h15a.75.75 0 0 1 0 1.5h-15a.75.75 0 0 1-.75-.75Zm.75 4.5a.75.75 0 0 0 0 1.5h15a.75.75 0 0 0 0-1.5h-15Z"
                clipRule="evenodd"
              />
            </svg>
          </button>
          <Link
            to="/"
            className="flex items-center space-x-3 rtl:space-x-reverse"
          >
            <img src={logo} className="h-8" alt="My Listings Logo" />
            <span className="self-center text-2xl font-semibold whitespace-nowrap text-white">
              My Listings
            </span>
          </Link>
          <Menu className="hidden md:block" items={MENU_ITEMS} />
        </div>
        <div>{/* user menu goes here */}</div>
      </div>
      <Drawer open={isDrawerOpen} onClose={() => setIsDrawerOpen(false)}>
        <div className="p-4">
          <Menu items={MENU_ITEMS} orientation="vertical" />
        </div>
      </Drawer>
    </TopBar>
  );
};
