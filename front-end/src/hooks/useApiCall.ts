import { useCallback } from "react";
import { useAlert } from "../context/alert/AlertContext";
import { useAuth } from "../context/auth/AuthContext";
import { client } from "../services/api-client";

export type UseApiCallOptions = {
  showAlertOnError?: boolean;
  actAsMockedUser?: boolean;
};

export const useApiCall = <ResponseType = void, ArgsType = void>(
  fetcher: (args: ArgsType) => Promise<ResponseType>,
  options: UseApiCallOptions = {}
) => {
  const { showAlertOnError = true, actAsMockedUser = true } = options;
  const { addAlert } = useAlert();
  const { mockSessionUser } = useAuth();

  const apiCall = useCallback(
    async (args: ArgsType) => {
      try {
        if (mockSessionUser?.id && actAsMockedUser) {
          client.axios.defaults.headers.common["Mock-Session-User-Id"] =
            mockSessionUser.id.toString();
        } else {
          delete client.axios.defaults.headers.common["Mock-Session-User-Id"];
        }
        return await fetcher(args);
      } catch (error: unknown) {
        const errorMessage =
          error instanceof Error ? error.message : "An unknown error occurred";
        if (showAlertOnError) {
          addAlert(errorMessage, "danger");
        } else {
          throw error;
        }
      }
    },
    [addAlert, showAlertOnError, fetcher]
  );
  return apiCall;
};
