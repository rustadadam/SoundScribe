import { FileUploader } from "@/components/file-uploader"
import { HowItWorks } from "@/components/how-it-works"
import { Hero } from "@/components/hero"
import { Features } from "@/components/features"
import { Footer } from "@/components/footer"

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
      <Hero />
      <div className="container mx-auto px-4 py-12 space-y-24">
        <FileUploader />
        <HowItWorks />
        <Features />
      </div>
      <Footer />
    </main>
  )
}

