import type { Metadata } from "next";
import { Inter, Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/layout/navbar";
import { Footer } from "@/components/layout/footer";
import { ThemeProvider } from "@/components/layout/theme-provider";
import { AuthProvider } from "@/components/auth/auth-provider";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const plusJakarta = Plus_Jakarta_Sans({
  variable: "--font-plus-jakarta",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "WelfareGuard | AI-Powered Fraud Detection System",
  description: "AI-powered welfare detection system ensuring benefits reach genuine citizens. Real-time monitoring, predictive analytics, and comprehensive fraud prevention.",
  keywords: ["welfare", "fraud detection", "AI", "government", "analytics"],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${inter.variable} ${plusJakarta.variable} font-sans antialiased bg-background text-foreground smooth-scroll custom-scrollbar`}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
        >
          <AuthProvider>
            <div className="relative flex min-h-screen flex-col">
              <div className="pointer-events-none fixed inset-0 -z-10">
                <div className="absolute inset-0 bg-gradient-to-b from-muted/30 via-background to-background" />
                <div className="absolute inset-0 bg-grid-pattern opacity-[0.4]" />
              </div>
              <Navbar />
              <main className="flex-1">
                {children}
              </main>
              <Footer />
            </div>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
