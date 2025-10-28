import { useMemo } from "react";
import { useAuth } from "../context/auth/AuthContext";
import { useApiCall, UseApiCallOptions } from "./useApiCall";
import useSWR from "swr";

export const useAutomaticFetching = <ResponseType = void, ArgsType = void>(
  args: ArgsType,
  cacheCategory: string,
  fetcher: (args: ArgsType) => Promise<ResponseType>,
  options: UseApiCallOptions = {}
) => {
  const apiCall = useApiCall(fetcher, options);
  const { user } = useAuth();
  const cacheKey: [string, ArgsType, number | undefined] = useMemo(() => {
    if (options.actAsMockedUser == false) {
      return [cacheCategory, args, undefined];
    } else {
      return [cacheCategory, args, user?.id];
    }
  }, [cacheCategory, args, options.actAsMockedUser, user?.id]);
  const { data, isLoading } = useSWR(
    cacheKey,
    ([_cacheCategory, args, _userId]: [string, ArgsType, number | undefined]) =>
      apiCall(args)
  );
  return { data, isLoading };
};
