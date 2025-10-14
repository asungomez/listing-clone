import { FC, useCallback, useMemo, useState } from "react";
import { useAuth } from "../../context/auth/AuthContext";
import { Menu, MenuItem } from "../../atoms/Menu/Menu";
import {
  AutoSuggestion,
  SuggestionItem,
} from "../../atoms/AutoSuggestion/AutoSuggestion";
import { useSearchUsers } from "../../hooks/useSearchUsers";
import { ListUsersResponse } from "../../services/admin";

const SEARCH_RESULTS_LIMIT = 5;

type SuggestedUser = ListUsersResponse[number];

export const UserMenu: FC = () => {
  const {
    logOut,
    startMockingSession,
    authenticatedUser,
    stopMockingSession,
    mockSessionUser,
  } = useAuth();
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [selectedUser, setSelectedUser] =
    useState<SuggestionItem<SuggestedUser> | null>(
      mockSessionUser
        ? {
            label: mockSessionUser?.email ?? "",
            value: mockSessionUser,
          }
        : null
    );
  const { searchUsers } = useSearchUsers(SEARCH_RESULTS_LIMIT, {
    actAsMockedUser: false,
  });

  const emailSuggestions = useCallback(
    async (search: string): Promise<SuggestionItem<SuggestedUser>[]> => {
      const list = (await searchUsers(search)) ?? [];
      const suggestions = list.map((e) => ({
        label: e.email ?? "",
        value: e,
      }));
      return suggestions;
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

  const handleSwitchUser = useCallback(
    async (user: SuggestionItem<SuggestedUser> | null) => {
      if (user && user.value.id !== authenticatedUser?.id) {
        startMockingSession(user.value);
        setSelectedUser({
          label: user.value.email ?? "",
          value: user.value,
        });
      } else {
        stopMockingSession();
      }
    },
    [startMockingSession, stopMockingSession, authenticatedUser]
  );

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
      {authenticatedUser?.is_superuser && (
        <div className="px-1 pb-2">
          <AutoSuggestion<SuggestedUser>
            label="Switch user"
            placeholder="Type an email..."
            autoComplete="off"
            value={selectedUser}
            onChange={handleSwitchUser}
            suggestionsGenerator={emailSuggestions}
          />
        </div>
      )}
      <Menu items={menuItems} />
    </>
  );
};
