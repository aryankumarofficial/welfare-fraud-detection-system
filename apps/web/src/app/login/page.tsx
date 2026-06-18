"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/auth/auth-provider";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

export default function LoginPage() {
  const router = useRouter();
  const { login, user, loading } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);

  if (user) {
    if (typeof window !== "undefined") {
      router.push("/admin/dashboard");
    }
    return null;
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    try {
      await login(username.trim(), password.trim());
      router.push("/admin/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed.");
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-16">
      <Card className="w-full max-w-xl border border-border">
        <CardHeader className="px-8 py-10 text-center">
          <CardTitle className="text-3xl">Admin Sign In</CardTitle>
          <CardDescription>Authenticate with the ML backend credentials to access the admin workspace.</CardDescription>
        </CardHeader>
        <CardContent className="px-8 pb-10">
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-muted-foreground">
                Username
              </label>
              <input
                id="username"
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                placeholder="Username"
                className="mt-2 w-full rounded-xl border border-input bg-background px-4 py-3 text-base text-foreground shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-muted-foreground">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Password"
                className="mt-2 w-full rounded-xl border border-input bg-background px-4 py-3 text-base text-foreground shadow-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20"
              />
            </div>
            {error ? (
              <div className="rounded-3xl border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
                {error}
              </div>
            ) : null}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Signing in…" : "Sign in"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
