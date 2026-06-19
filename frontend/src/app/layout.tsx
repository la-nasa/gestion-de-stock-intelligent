import type { Metadata } from "next"
import "./globals.css"

export const metadata: Metadata = {
  title: "IUC Inventory System",
  description: "Gestion de stock intelligente - IUC",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fr">
      <body>{children}</body>
    </html>
  )
}