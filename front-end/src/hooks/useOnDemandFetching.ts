import { useCallback } from "react";
import { useSWRConfig, unstable_serialize } from "swr";
import { useApiCall, UseApiCallOptions } from "./useApiCall";
import { useAuth } from "../context/auth/AuthContext";

/**
 * This hook is used to fetch data on demand, only triggering
 * the fetch when the user calls the returned function.
 *
 * It leverages SWR's cache and mutate functions to fetch the data.
 */
export const useOnDemandFetching = <ResponseType = void, ArgsType = void>(
  fetcher: (args: ArgsType) => Promise<ResponseType>,
  options: UseApiCallOptions = {}
): ((args: ArgsType) => Promise<ResponseType | undefined>) => {
  const cacheCategory = fetcher.name;
  const { cache, mutate } = useSWRConfig();
  const apiCall = useApiCall(fetcher, options);
  const { user, authenticatedUser } = useAuth();

  const fetchOnDemand = useCallback(
    async (args: ArgsType): Promise<ResponseType | undefined> => {
      const keyParts: [string, ArgsType, number | undefined] = [
        cacheCategory,
        args,
        options.actAsMockedUser ? user?.id : authenticatedUser?.id,
      ];
      const cacheKey = unstable_serialize(keyParts);

      const cached = cache.get(cacheKey);
      const cachedData = cached?.data as ResponseType | undefined;
      if (cachedData !== undefined) {
        return cachedData;
      }

      const fetchPromise = apiCall(args);

      const result = await mutate(cacheKey, fetchPromise, {
        revalidate: false,
        populateCache: true,
      });
      return result ?? (await fetchPromise);
    },
    [
      cache,
      mutate,
      cacheCategory,
      fetcher,
      apiCall,
      options.actAsMockedUser,
      user?.id,
      authenticatedUser?.id,
    ]
  );

  return fetchOnDemand;
};
