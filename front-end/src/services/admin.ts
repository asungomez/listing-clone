import { client } from "./api-client";
import { schemas } from "./generated-zodios-client";
import { z } from "zod";

export type ListUsersResponse = z.infer<
  typeof schemas.ListUsersResponse
>["users"];
export type ListUsersArgs = {
  query?: string;
  limit?: number;
};
export const listUsers = async ({
  query,
  limit,
}: ListUsersArgs): Promise<ListUsersResponse> => {
  const { users } = await client.users_list({
    queries: { page_size: limit, email: query },
  });
  return users;
};
