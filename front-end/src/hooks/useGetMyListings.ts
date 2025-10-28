import { useApiCall } from "./useApiCall";
import { getMyListings, GetMyListingsArgs } from "../services/listings";
import useSWR from "swr";

export const useGetMyListings = (args: GetMyListingsArgs) => {
  const getMyListingsApiCall = useApiCall(getMyListings);
  const { data, isLoading } = useSWR(["my-listings", args], ([_, args]) =>
    getMyListingsApiCall(args)
  );
  return { listings: data, isLoading };
};
