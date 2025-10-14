import { useCallback } from "react";
import { useSWRConfig } from "swr";
import { useApiCall, UseApiCallOptions } from "./useApiCall";

/**
 * This hook is used to fetch data on demand, only triggering
 * the fetch when the user calls the returned function.
 *
 * It leverages SWR's cache and mutate functions to fetch the data.
 */
export const useOnDemandFetching = <ResponseType = void, ArgsType = void>(
  cacheCategory: string,
  fetcher: (args: ArgsType) => Promise<ResponseType>,
  options: UseApiCallOptions = {}
): ((args: ArgsType) => Promise<ResponseType | undefined>) => {
  const { cache, mutate } = useSWRConfig();
  const apiCall = useApiCall(fetcher, options);

  const fetchOnDemand = useCallback(
    async (args: ArgsType): Promise<ResponseType | undefined> => {
      const key = `${cacheCategory}:${JSON.stringify(args)}`;

      const cached = cache.get(key);
      const cachedData = cached?.data as ResponseType | undefined;
      if (cachedData !== undefined) {
        return cachedData;
      }

      const fetchPromise = apiCall(args);

      const result = await mutate(key, fetchPromise, {
        revalidate: false,
        populateCache: true,
      });
      return result ?? (await fetchPromise);
    },
    [cache, mutate, cacheCategory, fetcher, apiCall]
  );

  return fetchOnDemand;
};
