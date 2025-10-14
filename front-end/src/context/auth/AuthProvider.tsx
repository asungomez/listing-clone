import {
  FC,
  ReactNode,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import { logOut as logOutService } from "../../services/auth";
import { AuthContext, AuthStatus } from "./AuthContext";
import { Spinner } from "../../atoms/Spinner/Spinner";
import { MessagePage } from "../../features/MessagePage/MessagePage";
import { GetAuthenticatedUserResponse } from "../../services/auth";
import { useNavigate } from "react-router";
import { AxiosError } from "axios";
import { useAlert } from "../alert/AlertContext";
import { useGetCurrentUser } from "../../hooks/useGetCurrentUser";

type AuthProviderProps = {
  children: ReactNode;
};

export const AuthProvider: FC<AuthProviderProps> = ({ children }) => {
  const [authenticatedUser, setAuthenticatedUser] =
    useState<GetAuthenticatedUserResponse | null>(null);
  const [mockSessionUser, setMockSessionUser] =
    useState<GetAuthenticatedUserResponse | null>(null);
  const [authStatus, setAuthStatus] = useState<AuthStatus>("loading");
  const navigate = useNavigate();
  const { addAlert } = useAlert();
  const getCurrentUser = useGetCurrentUser();

  useEffect(() => {
    if (authStatus == "loading") {
      getCurrentUser()
        .then((user) => {
          if (user) {
            setAuthenticatedUser(user);
            setAuthStatus("authenticated");
            navigate("/my-listings");
          }
        })
        .catch((error) => {
          let errorMessage: string | undefined = undefined;
          if (error instanceof AxiosError) {
            const errorCode = error.response?.data?.code;
            switch (errorCode) {
              case "session_expired":
                errorMessage = "Your session has expired. Please log in again.";
                break;
              case "session_invalid":
                errorMessage =
                  "Your credentials are invalid. Please log in again.";
                break;
              case "inactive_user":
                errorMessage =
                  "Your account is inactive. Please contact support.";
                break;
              case "user_not_found":
                errorMessage =
                  "Your account does not exist. Please contact support.";
                break;
            }
          }
          if (errorMessage) {
            navigate("/?error_message=" + encodeURIComponent(errorMessage));
          }
          setAuthStatus("unauthenticated");
        });
    }
  }, [authStatus]);

  const redirectToLogin = useCallback(async () => {
    const oktaLoginUrl = `${
      import.meta.env.VITE_OKTA_DOMAIN
    }/authorize?response_type=code&client_id=${
      import.meta.env.VITE_OKTA_CLIENT_ID
    }&state=vitecourse&scope=openid%20email%20offline_access&redirect_uri=${encodeURI(
      import.meta.env.VITE_OKTA_LOGIN_REDIRECT
    )}`;
    window.location.href = oktaLoginUrl;
  }, []);

  const logOut = useCallback(async () => {
    try {
      await logOutService();
      setAuthStatus("unauthenticated");
      setAuthenticatedUser(null);
      navigate("/");
    } catch (error) {
      console.error(error);
      addAlert("Failed to log out. Please try again.", "danger");
    }
  }, []);

  const startMockingSession = useCallback(
    (user: GetAuthenticatedUserResponse) => {
      setMockSessionUser(user);
    },
    []
  );

  const stopMockingSession = useCallback(() => {
    setMockSessionUser(null);
  }, []);

  const isAdmin = useMemo(() => {
    if (mockSessionUser) {
      return !!mockSessionUser.is_superuser;
    }
    if (authenticatedUser) {
      return !!authenticatedUser.is_superuser;
    }
    return false;
  }, [mockSessionUser, authenticatedUser]);

  const user = useMemo(() => {
    if (mockSessionUser) {
      return mockSessionUser;
    }
    return authenticatedUser;
  }, [mockSessionUser, authenticatedUser]);

  if (authStatus == "loading") {
    return (
      <MessagePage>
        <Spinner size={10} />
        <div>Loading...</div>
      </MessagePage>
    );
  }

  return (
    <AuthContext.Provider
      value={{
        redirectToLogin,
        user,
        authenticatedUser,
        status: authStatus,
        logOut,
        isAdmin,
        mockSessionUser,
        startMockingSession,
        stopMockingSession,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
