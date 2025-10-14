import { FC, useCallback, useMemo, useState } from "react";
import { useAuth } from "../../context/auth/AuthContext";
import { Menu, MenuItem } from "../../atoms/Menu/Menu";
import {
  AutoSuggestion,
  SuggestionItem,
} from "../../atoms/AutoSuggestion/AutoSuggestion";
import { useSearchUsers } from "../../hooks/useSearchUsers";

const SEARCH_RESULTS_LIMIT = 5;

export const UserMenu: FC = () => {
  const { logOut, isAdmin } = useAuth();
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [selectedUser, setSelectedUser] =
    useState<SuggestionItem<string> | null>(null);
  const { searchUsers } = useSearchUsers(SEARCH_RESULTS_LIMIT);

  const emailSuggestions = useCallback(
    async (search: string): Promise<SuggestionItem<string>[]> => {
      const list = await searchUsers(search);
      const suggestions = list
        .map((u) => u.email)
        .filter((e): e is string => Boolean(e))
        .map((e) => ({ label: e, value: e }));
      const uniqueByLabel = Array.from(
        new Map(suggestions.map((s) => [s.label.toLowerCase(), s])).values()
      );
      return uniqueByLabel;
    },
    [searchUsers]
  );

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
      {isAdmin && (
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
      )}
      <Menu items={menuItems} />
    </>
  );
};
