export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <h1 className="text-4xl font-bold text-primary mb-4">
        Chat Emploi
      </h1>
      <p className="text-lg text-text-secondary mb-8">
        Votre coach emploi empathique
      </p>
      <div className="bg-surface rounded-lg p-8 shadow-lg max-w-md">
        <p className="text-text-primary mb-4">
          L&apos;application est en cours d&apos;initialisation...
        </p>
        <p className="text-sm text-text-tertiary">
          Le frontend Tauri + Next.js sera bientôt prêt !
        </p>
      </div>
    </main>
  )
}