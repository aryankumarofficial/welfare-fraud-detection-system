import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft, UserX } from "lucide-react";

export default function Unauthorized() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="text-center max-w-2xl mx-auto">
        {/* Animated 401 */}
        <div className="relative mb-8">
          <h1 className="text-9xl font-bold text-chart-2/20">401</h1>
          <div className="absolute inset-0 flex items-center justify-center">
            <UserX className="h-24 w-24 text-chart-2/40" />
          </div>
        </div>

        {/* Message */}
        <h2 className="text-3xl font-bold mb-4">Unauthorized Access</h2>
        <p className="text-muted-foreground text-lg mb-8 max-w-md mx-auto">
          You need to be logged in to access this page. Please sign in or create an account to continue.
        </p>

        {/* Actions */}
        <div className="flex gap-4 justify-center flex-wrap">
          <Button asChild size="lg">
            <Link href="/">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Home
            </Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link href="/admin/dashboard">
              Sign In
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
