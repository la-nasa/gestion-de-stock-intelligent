import { Sidebar } from "@/components/layout/sidebar"
import { Header } from "@/components/layout/header"
import { WebSocketProvider } from "@/components/features/websocket-provider"
import { Toaster } from "react-hot-toast"

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <WebSocketProvider>
      <div className="min-h-screen bg-gray-50/50 dark:bg-gray-950">
        <Sidebar />
        <div className="ml-64">
          <Header />
          <main className="p-6">
            {children}
          </main>
        </div>
      </div>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: "#fff",
            color: "#111827",
            border: "1px solid #e5e7eb",
            borderRadius: "12px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.05)",
            fontSize: "14px",
          },
        }}
      />
    </WebSocketProvider>
  )
}