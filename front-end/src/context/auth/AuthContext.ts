import { createContext, useContext } from "react";
import { GetAuthenticatedUserResponse } from "../../services/auth";

export type AuthStatus =
  | "authenticated" // The authentication process has completed successfully and the authenticated user is available.
  | "unauthenticated" // The authentication process has completed unsuccessfully and the user is not authenticated.
  | "loading"; // The authentication process is in progress.

type AuthContextType = {
  logOut: () => Promise<void>;
  redirectToLogin: () => Promise<void>;
  startMockingSession: (user: GetAuthenticatedUserResponse) => void;
  stopMockingSession: () => void;
  status: AuthStatus;
  user: GetAuthenticatedUserResponse | null;
  authenticatedUser: GetAuthenticatedUserResponse | null;
  isAdmin: boolean;
  mockSessionUser: GetAuthenticatedUserResponse | null;
};

export const AuthContext = createContext<AuthContextType>({
  logOut: async () => {},
  redirectToLogin: async () => {},
  status: "loading",
  user: null,
  authenticatedUser: null,
  isAdmin: false,
  mockSessionUser: null,
  startMockingSession: () => {},
  stopMockingSession: () => {},
});

export const useAuth = () => useContext(AuthContext);
