import { FC } from "react";
import { BrowserRouter, Route, Routes } from "react-router";
import { LogInPage } from "../pages/LogIn";
import { AuthProvider } from "../context/auth/AuthProvider";
import { AuthenticatedRoute } from "./AuthenticatedRoute";
import { UnauthenticatedRoute } from "./UnauthenticatedRoute";
import { ErrorPage } from "../pages/Error";

export const Router: FC = () => {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          <Route element={<UnauthenticatedRoute />}>
            <Route index element={<LogInPage />} />
          </Route>
          <Route path="error" element={<ErrorPage />} />

          <Route element={<AuthenticatedRoute />}>
            <Route path="my-listings">
              <Route index element={<div>My Listings</div>} />
            </Route>
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  );
};
