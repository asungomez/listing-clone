import { createApiClient } from "./generated-zodios-client";

const API_URL = import.meta.env.VITE_API_URL;

export const client = createApiClient(API_URL, {
  axiosConfig: {
    withCredentials: true,
  },
});
