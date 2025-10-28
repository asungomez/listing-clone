import {
  ApiOf,
  ZodiosQueryParamsByAlias,
  ZodiosResponseByAlias,
} from "@zodios/core";
import { client } from "./api-client";
import { api } from "./generated-zodios-client";

type MyListingsApiResponse = ZodiosResponseByAlias<
  ApiOf<typeof api>,
  "my_listings"
>;
export type GetMyListingsResponse = MyListingsApiResponse["listings"];
export type GetMyListingsArgs = ZodiosQueryParamsByAlias<
  ApiOf<typeof api>,
  "my_listings"
>;

export const getMyListings = async (
  args: GetMyListingsArgs
): Promise<GetMyListingsResponse> => {
  const { listings } = await client.my_listings({
    queries: args,
  });
  return listings;
};
