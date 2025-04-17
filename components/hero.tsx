import { Headphones } from "lucide-react"

export function Hero() {
  return (
    <div className="bg-slate-900 text-white">
      <div className="container mx-auto px-4 py-12 md:py-16">
        <div className="flex flex-col items-center text-center space-y-4">
          <div className="flex items-center justify-center p-3 bg-slate-800 rounded-full">
            <Headphones className="w-8 h-8 text-teal-400" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
            Sound<span className="text-teal-400">Scribe</span>
          </h1>
          <p className="text-xl text-slate-300 max-w-xl">Convert text to audiobooks in under 60 seconds</p>
          <a
            href="#upload"
            className="mt-4 px-6 py-2 bg-teal-500 hover:bg-teal-600 transition-colors rounded-full font-medium text-white"
          >
            Get Started
          </a>
        </div>
      </div>
    </div>
  )
}

