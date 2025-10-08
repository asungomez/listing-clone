import { FC, useRef, useState } from "react";
import { Link } from "react-router";
import { TopBar } from "../../atoms/TopBar/TopBar";
import logo from "../../assets/logo.svg";
import { Menu, MenuItem } from "../../atoms/Menu/Menu";
import { Drawer } from "../../atoms/Drawer/Drawer";
import { Popover } from "../../atoms/Popover/Popover";
import { useAuth } from "../../context/auth/AuthContext";
import { UserMenu } from "../UserMenu/UserMenu";
import { FiMenu, FiUser } from "react-icons/fi";

const MENU_ITEMS: MenuItem[] = [
  { label: "My Listings", href: "/my-listings" },
  { label: "All JLL Properties", href: "/properties" },
  { label: "Team Listings", href: "/team-listings" },
  { label: "Reports", href: "/reports" },
];

export const NavBar: FC = () => {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = useState(false);
  const userButtonRef = useRef<HTMLButtonElement | null>(null);
  const { user } = useAuth();
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
            <FiMenu size={24} />
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
        <div className="flex items-center">
          {user && (
            <>
              <button
                ref={userButtonRef}
                type="button"
                className="inline-flex items-center justify-center p-2 text-white hover:bg-gray-800 rounded-full"
                aria-label="User menu"
                aria-haspopup="dialog"
                aria-expanded={isUserMenuOpen}
                onClick={() => setIsUserMenuOpen((v) => !v)}
              >
                <FiUser size={24} />
              </button>

              <Popover
                anchor={userButtonRef}
                open={isUserMenuOpen}
                position="bottom"
              >
                <Popover.Title>{user.email}</Popover.Title>
                <div className="px-3 py-2">
                  <UserMenu />
                </div>
              </Popover>
            </>
          )}
        </div>
      </div>
      <Drawer open={isDrawerOpen} onClose={() => setIsDrawerOpen(false)}>
        <div className="p-4">
          <Menu items={MENU_ITEMS} orientation="vertical" />
        </div>
      </Drawer>
    </TopBar>
  );
};
