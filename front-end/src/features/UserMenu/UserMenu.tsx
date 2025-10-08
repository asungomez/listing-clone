import { FC, useCallback, useMemo, useState } from "react";
import { useAuth } from "../../context/auth/AuthContext";
import { Menu, MenuItem } from "../../atoms/Menu/Menu";

export const UserMenu: FC = () => {
  const { logOut } = useAuth();
  const [isLoggingOut, setIsLoggingOut] = useState(false);

  const handleLogOut = useCallback(async () => {
    if (isLoggingOut) return;
    try {
      setIsLoggingOut(true);
      await logOut();
    } finally {
      setIsLoggingOut(false);
    }
  }, [logOut, isLoggingOut]);

  const menuItems: MenuItem[] = useMemo(
    () => [
      {
        label: "Log Out",
        onClick: () => {
          void handleLogOut();
        },
        disabled: isLoggingOut,
      },
    ],
    [handleLogOut, isLoggingOut]
  );
  return <Menu items={menuItems} />;
};
