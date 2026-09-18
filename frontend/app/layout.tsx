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
    <html lang="en">
      <body className="bg-[#FAF9F5] text-[#1E1E1E] antialiased selection:bg-amber-100 selection:text-amber-900">
        {children}
      </body>
    </html>
  );
}
