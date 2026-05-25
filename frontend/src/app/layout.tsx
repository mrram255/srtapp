import type { Metadata, Viewport } from "next";
import { DM_Sans, JetBrains_Mono, Playfair_Display, Bebas_Neue } from "next/font/google";

import "./globals.css";

const fontNumeric = Bebas_Neue({
  subsets: ["latin"],
  weight: ["400"],
  variable: "--font-numeric",
  display: "swap",
});

const fontSans = DM_Sans({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  variable: "--font-sans",
  display: "swap",
});

const fontDisplay = Playfair_Display({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-display",
  display: "swap",
});

const fontMono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-mono",
  display: "swap",
});

const appName = process.env.NEXT_PUBLIC_APP_NAME ?? "SRTAPP";

export const metadata: Metadata = {
  title: `${appName} — College Management`,
  description: "Production-grade college management system.",
  keywords: ["college", "management", "education", "ERP"],
  authors: [{ name: appName }],
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${fontSans.variable} ${fontDisplay.variable} ${fontMono.variable} ${fontNumeric.variable}`}
    >
      <body className="min-h-screen bg-background font-sans antialiased">{children}</body>
    </html>
  );
}
