import { makeApi, Zodios, type ZodiosOptions } from "@zodios/core";
import { z } from "zod";

const CreateListing = z
  .object({ title: z.string().min(1), description: z.string().min(1) })
  .passthrough();
const Coordinator = z
  .object({ id: z.number().int(), email: z.string().min(1).email() })
  .passthrough();
const Listing = z
  .object({
    id: z.number().int().optional(),
    title: z.string().min(1).max(255),
    description: z.string().min(1),
    updated_by: z.number().int().optional(),
    updated_at: z.string().datetime({ offset: true }).optional(),
    coordinators: z.array(Coordinator),
  })
  .passthrough();
const ListingsListResponse = z
  .object({ listings: z.array(Listing), total_count: z.number().int() })
  .passthrough();
const User = z
  .object({
    id: z.number().int(),
    email: z.string().min(1).email(),
    username: z.string().min(1),
    first_name: z.string().min(1).max(255).nullable(),
    last_name: z.string().min(1).max(255).nullable(),
    is_superuser: z.boolean(),
  })
  .partial()
  .passthrough();
const ListUsersResponse = z
  .object({ users: z.array(User), total_count: z.number().int() })
  .passthrough();
const CurrentUserResponse = z.object({ user: User }).passthrough();

export const schemas = {
  CreateListing,
  Coordinator,
  Listing,
  ListingsListResponse,
  User,
  ListUsersResponse,
  CurrentUserResponse,
};

const endpoints = makeApi([
  {
    method: "get",
    path: "/accounts/login/",
    alias: "redirect_to_login",
    description: `Redirect to the login page. This endpoint is only used for the Swagger
UI.`,
    requestFormat: "json",
    response: z.void(),
    errors: [
      {
        status: 302,
        description: `Redirect to the login page`,
        schema: z.void(),
      },
    ],
  },
  {
    method: "post",
    path: "/listings/",
    alias: "listings_create",
    description: `:param request: The request object
:param args: The arguments
:param kwargs: The keyword arguments
:return: The response object`,
    requestFormat: "json",
    parameters: [
      {
        name: "body",
        type: "Body",
        schema: CreateListing,
      },
      {
        name: "Authorization",
        type: "Header",
        schema: z.string().optional(),
      },
      {
        name: "mock-session-user-id",
        type: "Header",
        schema: z.string().optional(),
      },
    ],
    response: Listing,
  },
  {
    method: "get",
    path: "/listings/my-listings",
    alias: "my_listings",
    description: `View for the my listings endpoint`,
    requestFormat: "json",
    parameters: [
      {
        name: "offset",
        type: "Query",
        schema: z.number().int().gte(0).optional().default(0),
      },
      {
        name: "page_size",
        type: "Query",
        schema: z.number().int().gte(1).lte(100).optional().default(25),
      },
      {
        name: "Authorization",
        type: "Header",
        schema: z.string().optional(),
      },
      {
        name: "mock-session-user-id",
        type: "Header",
        schema: z.string().optional(),
      },
    ],
    response: ListingsListResponse,
  },
  {
    method: "get",
    path: "/users/",
    alias: "users_list",
    description: `List users.
:param request: The request object
:return: The response object`,
    requestFormat: "json",
    parameters: [
      {
        name: "offset",
        type: "Query",
        schema: z.number().int().gte(0).optional().default(0),
      },
      {
        name: "page_size",
        type: "Query",
        schema: z.number().int().gte(1).lte(100).optional().default(25),
      },
      {
        name: "email",
        type: "Query",
        schema: z.string().optional(),
      },
      {
        name: "Authorization",
        type: "Header",
        schema: z.string().optional(),
      },
      {
        name: "mock-session-user-id",
        type: "Header",
        schema: z.string().optional(),
      },
    ],
    response: ListUsersResponse,
  },
  {
    method: "get",
    path: "/users/login-callback",
    alias: "login_callback",
    requestFormat: "json",
    parameters: [
      {
        name: "code",
        type: "Query",
        schema: z.string(),
      },
      {
        name: "state",
        type: "Query",
        schema: z.string(),
      },
    ],
    response: z.void(),
    errors: [
      {
        status: 302,
        description: `Redirect to the login page`,
        schema: z.void(),
      },
    ],
  },
  {
    method: "post",
    path: "/users/logout",
    alias: "logout",
    description: `Logout the user by invalidating the access token and removing the
credentials from the cookies.
:param request: The request object
:return: The response object`,
    requestFormat: "json",
    parameters: [
      {
        name: "Authorization",
        type: "Header",
        schema: z.string().optional(),
      },
      {
        name: "mock-session-user-id",
        type: "Header",
        schema: z.string().optional(),
      },
    ],
    response: z.void(),
  },
  {
    method: "get",
    path: "/users/me",
    alias: "users_me",
    requestFormat: "json",
    parameters: [
      {
        name: "Authorization",
        type: "Header",
        schema: z.string().optional(),
      },
      {
        name: "mock-session-user-id",
        type: "Header",
        schema: z.string().optional(),
      },
    ],
    response: CurrentUserResponse,
  },
]);

export const api = new Zodios(endpoints);

export function createApiClient(baseUrl: string, options?: ZodiosOptions) {
  return new Zodios(baseUrl, endpoints, options);
}
