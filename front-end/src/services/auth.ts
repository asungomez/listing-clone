import { isUser, User } from "../models/user";
import { fetcher } from "./axios";

export const getAuthenticatedUser = async (): Promise<User> => {
  const { data } = await fetcher.get("/users/me");
  if (!isUser(data?.user)) {
    throw new Error("Invalid user data");
  }
  return data.user;
};
