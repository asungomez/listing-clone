import { client } from "./api-client";
import { api } from "./generated-zodios-client";
import type {
  ApiOf,
  ZodiosQueryParamsByAlias,
  ZodiosResponseByAlias,
} from "@zodios/core";

type UsersListApiResponse = ZodiosResponseByAlias<
  ApiOf<typeof api>,
  "users_list"
>;
export type ListUsersResponse = UsersListApiResponse["users"];

export type ListUsersArgs = ZodiosQueryParamsByAlias<
  ApiOf<typeof api>,
  "users_list"
>;

export const listUsers = async (
  args: ListUsersArgs
): Promise<ListUsersResponse> => {
  const { users } = await client.users_list({
    queries: args,
  });
  return users;
};
