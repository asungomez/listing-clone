import { listUsers } from "../services/admin";
import { useOnDemandFetching } from "./useOnDemandFetching";

export const useSearchUsers = (limit: number = 25) => {
  const searchUsers = useOnDemandFetching("users-search", (query: string) =>
    listUsers({ query, limit })
  );

  return { searchUsers };
};
