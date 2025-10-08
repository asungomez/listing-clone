import { FC, useMemo } from "react";
import { useAuth } from "../../context/auth/AuthContext";
import { Menu, MenuItem } from "../../atoms/Menu/Menu";

export const UserMenu: FC = () => {
  const { logOut } = useAuth();
  const menuItems: MenuItem[] = useMemo(
    () => [{ label: "Log Out", onClick: logOut }],
    [logOut]
  );
  return <Menu items={menuItems} />;
};
