import Link from "next/link"

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-blue-900 to-blue-700">
      <div className="text-center text-white">
        <h1 className="text-5xl font-bold mb-4">IUC Inventory System</h1>
        <p className="text-xl mb-8 text-blue-200">
          Plateforme de Gestion de Stock Intelligente
        </p>
        <p className="text-lg mb-8 text-blue-300">
          Institut Universitaire de la Côte
        </p>
        <div className="flex gap-4 justify-center">
          <Link
            href="/login"
            className="px-8 py-3 bg-white text-blue-900 font-semibold rounded-lg hover:bg-blue-50 transition-colors"
          >
            Se connecter
          </Link>
          <Link
            href="/dashboard"
            className="px-8 py-3 border-2 border-white text-white font-semibold rounded-lg hover:bg-white/10 transition-colors"
          >
            Tableau de bord
          </Link>
        </div>
      </div>
    </div>
  )
}