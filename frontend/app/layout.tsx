import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Oráculo de Zonas | Análise de Criptoativos",
  description: "SaaS de identificação de zonas de interesse em BTC, ETH e SOL usando análise estatística avançada, Fibonacci, Gann, Wyckoff e Market Makers",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="pt-BR">
      <body className="min-h-screen bg-gray-50">
        {children}
      </body>
    </html>
  );
}
