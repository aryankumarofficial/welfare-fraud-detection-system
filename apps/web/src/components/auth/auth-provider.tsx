"use client";

import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { loginUser, logoutUser, getCurrentUser } from "@/lib/auth";
import type { AuthUser } from "@/lib/auth";

interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = getCurrentUser();
    setUser(stored);
    setLoading(false);
  }, []);

  const login = async (username: string, password: string) => {
    setLoading(true);
    try {
      const authUser = await loginUser(username, password);
      setUser(authUser);
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    logoutUser();
    setUser(null);
  };

  const value = useMemo(
    () => ({ user, loading, login, logout }),
    [user, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
