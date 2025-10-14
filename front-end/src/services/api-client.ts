import { createApiClient } from "./generated-zodios-client";
import { ZodiosHooks } from "@zodios/react";

const API_URL = import.meta.env.VITE_API_URL;

export const client = createApiClient(API_URL, {
  axiosConfig: {
    withCredentials: true,
  },
});

export const apiHooks = new ZodiosHooks("api", client);
