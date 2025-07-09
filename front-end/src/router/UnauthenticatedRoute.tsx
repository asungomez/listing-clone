import { useNavigate } from "react-router";
import { useAuth } from "../context/auth/AuthContext";
import { FC, useEffect } from "react";
import { Outlet } from "react-router";

/**
 * Route that can only be accessed by unauthenticated users.
 * If the user is authenticated, they will be redirected to the profiles page.
 */
export const UnauthenticatedRoute: FC = () => {
  const { status } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (status !== "unauthenticated") {
      navigate("/my-listings");
    }
  }, []);

  if (status !== "unauthenticated") {
    return null;
  }
  return <Outlet />;
};
