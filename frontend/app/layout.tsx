import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "CareerOS — AI Candidate Studio",
  description: "Conversational career agent and strategic opportunity intelligence for candidates.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full overflow-hidden">
      <body className="h-full overflow-hidden antialiased bg-canvas text-content-primary">
        {children}
      </body>
    </html>
  );
}
