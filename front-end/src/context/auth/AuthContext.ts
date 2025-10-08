import { createContext, useContext } from "react";
import { User } from "../../models/user";

export type AuthStatus =
  | "authenticated" // The authentication process has completed successfully and the authenticated user is available.
  | "unauthenticated" // The authentication process has completed unsuccessfully and the user is not authenticated.
  | "loading"; // The authentication process is in progress.

type AuthContextType = {
  logOut: () => Promise<void>;
  redirectToLogin: () => Promise<void>;
  status: AuthStatus;
  user: User | null;
};

export const AuthContext = createContext<AuthContextType>({
  logOut: async () => {},
  redirectToLogin: async () => {},
  status: "loading",
  user: null,
});

export const useAuth = () => useContext(AuthContext);
