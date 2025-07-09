export type User = {
  email: string;
};

export const isUser = (value: unknown): value is User => {
  if (!value) {
    return false;
  }
  if (typeof value !== "object") {
    return false;
  }
  const obj = value as User;
  if (!obj.email) {
    return false;
  }
  if (typeof obj.email !== "string") {
    return false;
  }
  return true;
};
