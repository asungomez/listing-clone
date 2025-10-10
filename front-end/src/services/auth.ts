import { client } from "./api-client";
import { schemas } from "./generated-zodios-client";
import { z } from "zod";

export type GetAuthenticatedUserResponse = z.infer<
  typeof schemas.CurrentUserResponse
>["user"];
export const getAuthenticatedUser =
  async (): Promise<GetAuthenticatedUserResponse> => {
    const { user } = await client.users_me();
    return user;
  };

export const logOut = async (): Promise<void> => {
  await client.users_logout_create(undefined);
};
