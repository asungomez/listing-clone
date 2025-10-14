import { listUsers } from "../services/admin";
import { useOnDemandFetching } from "./useOnDemandFetching";

type SearchUsersOptions = {
  actAsMockedUser?: boolean;
};

export const useSearchUsers = (
  limit: number = 25,
  options: SearchUsersOptions = {}
) => {
  const { actAsMockedUser = true } = options;
  const searchUsers = useOnDemandFetching(
    "users-search",
    (query: string) => listUsers({ email: query, page_size: limit }),
    { actAsMockedUser }
  );

  return { searchUsers };
};
