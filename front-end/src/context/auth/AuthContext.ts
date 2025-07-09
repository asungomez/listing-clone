import { createContext, useContext } from "react";
import { User } from "../../models/user";

export type AuthStatus =
  | "authenticated" // The authentication process has completed successfully and the authenticated user is available.
  | "unauthenticated" // The authentication process has completed unsuccessfully and the user is not authenticated.
  | "loading"; // The authentication process is in progress.

type AuthContextType = {
  redirectToLogin: () => Promise<void>;
  user: User | null;
  status: AuthStatus;
};

export const AuthContext = createContext<AuthContextType>({
  redirectToLogin: async () => {},
  user: null,
  status: "loading",
});

export const useAuth = () => useContext(AuthContext);
