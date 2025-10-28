import { getMyListings, GetMyListingsArgs } from "../services/listings";
import { useAutomaticFetching } from "./useAutomaticFetching";

export const useGetMyListings = (args: GetMyListingsArgs) => {
  const { data, isLoading } = useAutomaticFetching(
    args,
    "my-listings",
    getMyListings
  );
  return { listings: data, isLoading };
};
