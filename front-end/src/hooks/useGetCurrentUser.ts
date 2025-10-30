import { getAuthenticatedUser } from "../services/auth";
import { useOnDemandFetching } from "./useOnDemandFetching";

export const useGetCurrentUser = () => {
  const getCurrentUser = useOnDemandFetching(getAuthenticatedUser, {
    showAlertOnError: false,
  });
  return getCurrentUser;
};
