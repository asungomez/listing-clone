import { listUsers } from "../services/admin";
import { useOnDemandFetching } from "./useOnDemandFetching";

export const useSearchUsers = (limit: number = 25) => {
  const searchUsers = useOnDemandFetching("users-search", (query: string) =>
    listUsers({ email: query, page_size: limit })
  );

  return { searchUsers };
};
