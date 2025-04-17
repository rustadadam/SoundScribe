export function Footer() {
  return (
    <footer className="bg-slate-900 text-slate-300 py-12">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center">
          <div className="mb-6 md:mb-0">
            <h2 className="text-2xl font-bold text-white">
              Sound<span className="text-teal-400">Scribe</span>
            </h2>
            <p className="mt-2 text-sm">Transform text into lifelike audiobooks</p>
          </div>
          <div className="text-sm">
            <p>© {new Date().getFullYear()} Sound Scribe. All rights reserved.</p>
            <p className="mt-1">A class project for BYU - CS 401r - MLOPS - Winter 2025</p>
          </div>
        </div>
      </div>
    </footer>
  )
}

