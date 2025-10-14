import { useCallback } from "react";
import { useSWRConfig } from "swr";
import { useAlert } from "../context/alert/AlertContext";

/**
 * This hook is used to fetch data on demand, only triggering
 * the fetch when the user calls the returned function.
 *
 * It leverages SWR's cache and mutate functions to fetch the data.
 */
export const useOnDemandFetching = <ResponseType = unknown, ArgsType = unknown>(
  cacheCategory: string,
  fetcher: (args: ArgsType) => Promise<ResponseType>
): ((args: ArgsType) => Promise<ResponseType>) => {
  const { cache, mutate } = useSWRConfig();
  const { addAlert } = useAlert();

  const fetchOnDemand = useCallback(
    async (args: ArgsType): Promise<ResponseType> => {
      const key = `${cacheCategory}:${JSON.stringify(args)}`;

      const cached = cache.get(key);
      const cachedData = cached?.data as ResponseType | undefined;
      if (cachedData !== undefined) {
        return cachedData;
      }

      const fetchPromise = fetcher(args);

      try {
        const result = await mutate(key, fetchPromise, {
          revalidate: false,
          populateCache: true,
        });
        return result ?? (await fetchPromise);
      } catch (error: unknown) {
        const message =
          error instanceof Error ? error.message : "Failed to fetch data";
        addAlert(message, "danger");
        throw error;
      }
    },
    [cache, mutate, cacheCategory, fetcher]
  );

  return fetchOnDemand;
};
