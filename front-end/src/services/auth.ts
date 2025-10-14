import { ApiOf, ZodiosResponseByAlias } from "@zodios/core";
import { client } from "./api-client";
import { api } from "./generated-zodios-client";

type UsersMeApiResponse = ZodiosResponseByAlias<ApiOf<typeof api>, "users_me">;
export type GetAuthenticatedUserResponse = UsersMeApiResponse["user"];

export const getAuthenticatedUser =
  async (): Promise<GetAuthenticatedUserResponse> => {
    const { user } = await client.users_me();
    return user;
  };

export const logOut = async (): Promise<void> => {
  await client.logout(undefined);
};
