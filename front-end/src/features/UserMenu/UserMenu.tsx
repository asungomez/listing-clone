import { FC, useCallback, useMemo, useState } from "react";
import { useAuth } from "../../context/auth/AuthContext";
import { Menu, MenuItem } from "../../atoms/Menu/Menu";
import {
  AutoSuggestion,
  SuggestionItem,
} from "../../atoms/AutoSuggestion/AutoSuggestion";

export const UserMenu: FC = () => {
  const { logOut } = useAuth();
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [selectedUser, setSelectedUser] =
    useState<SuggestionItem<string> | null>(null);

  const emailSuggestions = useMemo(() => {
    const base = [
      "jane.doe@example.com",
      "john.smith@example.com",
      "demo.user@example.com",
      "admin@example.com",
      "support@example.com",
    ];
    return (search: string): SuggestionItem<string>[] => {
      const q = search.trim().toLowerCase();
      const matched = q
        ? base.filter((e) => e.toLowerCase().includes(q))
        : base;
      const unique = Array.from(new Set(matched));
      return unique.slice(0, 8).map((e) => ({ label: e, value: e }));
    };
  }, []);

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
  return (
    <>
      <div className="px-1 pb-2">
        <AutoSuggestion<string>
          label="Switch user"
          placeholder="Type an email..."
          autoComplete="off"
          value={selectedUser}
          onChange={setSelectedUser}
          suggestionsGenerator={emailSuggestions}
        />
      </div>
      <Menu items={menuItems} />
    </>
  );
};
