"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/auth/auth-provider";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { user, loading } = useAuth();
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    if (!loading) {
      setChecked(true);
      if (!user) {
        router.replace("/login");
      }
    }
  }, [loading, user, router]);

  if (!checked || loading) {
    return (
      <div className="min-h-screen flex items-center justify-center px-4 py-16">
        <Card className="border border-border bg-background/90 p-8 text-center shadow-xl">
          <CardHeader>
            <CardTitle>Checking access…</CardTitle>
            <CardDescription>Validating your ML backend authentication.</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">You will be redirected if access is not available.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return <>{children}</>;
}
