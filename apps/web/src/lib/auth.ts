export type AuthRole = "admin" | "analyst" | "operator" | "viewer";

export interface AuthUser {
  username: string;
  role: AuthRole;
  exp: number;
}

const STORAGE_KEY = "wg_access_token";

interface TokenPayload {
  sub: string;
  role: AuthRole;
  exp: number;
}

function normalizeBase64(value: string) {
  return value.replace(/-/g, "+").replace(/_/g, "/");
}

function decodeTokenPayload(token: string): TokenPayload | null {
  try {
    const [encodedPayload] = token.split(".");
    if (!encodedPayload) return null;
    const normalized = normalizeBase64(encodedPayload);
    const padded = normalized + "=".repeat((4 - normalized.length % 4) % 4);
    const decoded = atob(padded);
    return JSON.parse(decoded) as TokenPayload;
  } catch {
    return null;
  }
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? process.env.ML_API_URL ?? "http://localhost:8000";

export function getStoredAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  try {
    return window.localStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

export function getStoredUser(): AuthUser | null {
  const token = getStoredAccessToken();
  if (!token) return null;
  const payload = decodeTokenPayload(token);
  if (!payload || !payload.exp || Date.now() / 1000 >= payload.exp) {
    clearStoredAccessToken();
    return null;
  }
  return {
    username: payload.sub,
    role: payload.role,
    exp: payload.exp,
  };
}

export function setStoredAccessToken(token: string) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(STORAGE_KEY, token);
  } catch {
    // ignore storage errors
  }
}

export function clearStoredAccessToken() {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.removeItem(STORAGE_KEY);
  } catch {
    // ignore storage errors
  }
}

export async function loginUser(username: string, password: string) {
  const response = await fetch(`${API_BASE_URL}/auth/token`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ username, password }),
    cache: "no-store",
  });

  const body = await response.json().catch(() => null);
  if (!response.ok || body == null || typeof body !== "object") {
    const message = body?.error || response.statusText || "Unable to authenticate.";
    throw new Error(message);
  }

  if (body.success === false) {
    throw new Error(body.error || "Authentication failed.");
  }

  const token = body.access_token;
  if (!token || typeof token !== "string") {
    throw new Error("Backend did not return an access token.");
  }

  setStoredAccessToken(token);
  const user = getStoredUser();
  if (!user) {
    throw new Error("Invalid token returned from backend.");
  }

  return user;
}

export function logoutUser() {
  clearStoredAccessToken();
}

export function getCurrentUser() {
  return getStoredUser();
}
