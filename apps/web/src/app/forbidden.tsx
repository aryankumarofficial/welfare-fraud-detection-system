import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Lock } from "lucide-react";

export default function Forbidden() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <div className="text-center max-w-2xl mx-auto">
        {/* Animated 403 */}
        <div className="relative mb-8">
          <h1 className="text-9xl font-bold text-destructive/20">403</h1>
          <div className="absolute inset-0 flex items-center justify-center">
            <Lock className="h-24 w-24 text-destructive/40" />
          </div>
        </div>

        {/* Message */}
        <h2 className="text-3xl font-bold mb-4">Access Forbidden</h2>
        <p className="text-muted-foreground text-lg mb-8 max-w-md mx-auto">
          You don't have permission to access this resource. Contact an administrator if you believe this is an error.
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
            <Link href="/contact">
              Contact Support
            </Link>
          </Button>
        </div>
      </div>
    </div>
  );
}
