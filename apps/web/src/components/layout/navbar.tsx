"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Shield, Menu, LogIn, LogOut } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetTrigger,
  SheetClose,
} from "@/components/ui/sheet";
import { useAuth } from "@/components/auth/auth-provider";

const navItems = [
  { label: "Home", href: "/", roles: ["public"] },
  { label: "Dashboard", href: "/admin/dashboard", roles: ["viewer", "operator", "analyst", "admin"] },
  { label: "Predictions", href: "/admin/predictions", roles: ["viewer", "operator", "analyst", "admin"] },
  { label: "Workflows", href: "/admin/workflows", roles: ["operator", "analyst", "admin"] },
  { label: "Queue", href: "/admin/analytics/queue", roles: ["operator", "analyst", "admin"] },
  { label: "Alerts", href: "/admin/analytics/alerts", roles: ["operator", "analyst", "admin"] },
  { label: "Model Health", href: "/admin/analytics/model-health", roles: ["analyst", "admin"] },
  { label: "Models", href: "/admin/models", roles: ["analyst", "admin"] },
  { label: "Reviews", href: "/admin/reviews", roles: ["analyst", "admin"] },
];

export function Navbar() {
  const pathname = usePathname();
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  const { user, logout } = useAuth();

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 10);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const visibleItems = navItems.filter((item) =>
    item.roles.includes("public") || (user?.role && item.roles.includes(user.role))
  );

  return (
    <header
      className={`sticky top-0 z-50 w-full border-b transition-colors ${
        scrolled ? "bg-background/95 backdrop-blur-sm" : "bg-background"
      }`}
    >
      <div className="mx-auto px-4 sm:px-6 lg:px-8 max-w-7xl">
        <div className="flex items-center justify-between h-16">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary flex items-center justify-center rounded-lg">
              <Shield className="h-4 w-4 text-primary-foreground" />
            </div>
            <span className="font-bold text-lg tracking-tight">WelfareGuard</span>
          </Link>

          <nav className="hidden md:flex items-center gap-px">
            {visibleItems.map((item) => (
              <Link
                key={item.label}
                href={item.href}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  pathname === item.href
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-muted"
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            {user ? (
              <>
                <span className="hidden md:inline-flex items-center rounded-full border border-border bg-muted px-3 py-2 text-sm text-muted-foreground">
                  {user.role.toUpperCase()}
                </span>
                <Button size="sm" variant="outline" onClick={logout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  Sign out
                </Button>
              </>
            ) : (
              <Button asChild size="sm" className="hidden md:flex">
                <Link href="/login">
                  <LogIn className="mr-2 h-4 w-4" />
                  Sign in
                </Link>
              </Button>
            )}

            <Sheet open={open} onOpenChange={setOpen}>
              <SheetTrigger asChild className="md:hidden">
                <Button variant="ghost" size="icon">
                  <Menu className="h-5 w-5" />
                </Button>
              </SheetTrigger>
              <SheetContent side="right">
                <div className="flex flex-col h-full pt-6">
                  <nav className="flex-1 space-y-px">
                    {visibleItems.map((item) => (
                      <SheetClose asChild key={item.label}>
                        <Link
                          href={item.href}
                          className={`block px-4 py-3 text-sm font-medium ${
                            pathname === item.href
                              ? "bg-primary text-primary-foreground"
                              : "border-b border-border"
                          }`}
                        >
                          {item.label}
                        </Link>
                      </SheetClose>
                    ))}
                  </nav>
                  {user ? (
                    <Button variant="outline" className="w-full mt-4" onClick={logout}>
                      <LogOut className="mr-2 h-4 w-4" />
                      Sign out
                    </Button>
                  ) : (
                    <SheetClose asChild>
                      <Button asChild className="w-full mt-4">
                        <Link href="/login">
                          <LogIn className="mr-2 h-4 w-4" />
                          Sign in
                        </Link>
                      </Button>
                    </SheetClose>
                  )}
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>
    </header>
  );
}
