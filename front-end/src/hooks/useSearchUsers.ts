import { listUsers } from "../services/admin";
import { useOnDemandFetching } from "./useOnDemandFetching";

type SearchUsersOptions = {
  actAsMockedUser?: boolean;
};

export const useSearchUsers = (options: SearchUsersOptions = {}) => {
  const { actAsMockedUser = true } = options;
  const searchUsers = useOnDemandFetching(listUsers, { actAsMockedUser });

  return { searchUsers };
};
