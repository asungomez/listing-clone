import { FC, useEffect } from "react";
import { useAuth } from "../context/auth/AuthContext";
import { Outlet, useNavigate } from "react-router";
import { NavBar } from "../features/NavBar/NavBar";

/**
 * Route that can only be accessed by authenticated users.
 * If the user is not authenticated, they will be redirected to the login page.
 */
export const AuthenticatedRoute: FC = () => {
  const { status } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (status !== "authenticated") {
      navigate("/");
    }
  }, []);

  if (status !== "authenticated") {
    return null;
  }
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <NavBar />
      <main className="mx-auto max-w-screen-xl px-4 py-6 md:py-10">
        <Outlet />
      </main>
    </div>
  );
};
