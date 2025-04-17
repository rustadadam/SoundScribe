import { FileText, Wand2, Headphones } from "lucide-react"

const steps = [
  {
    icon: FileText,
    title: "Upload Your Text",
    description: "Simply upload any .txt file containing your book or document.",
  },
  {
    icon: Wand2,
    title: "AI Processing",
    description: "Our AI analyzes your text, identifies characters, and selects appropriate voices.",
  },
  {
    icon: Headphones,
    title: "Download Audiobook",
    description: "Within 60 seconds, your audiobook is ready to download as an MP3 file.",
  },
]

export function HowItWorks() {
  return (
    <section className="py-12">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold mb-4">How It Works</h2>
        <p className="text-slate-600 max-w-2xl mx-auto">
          Sound Scribe uses advanced AI to transform your text into natural-sounding audiobooks in three simple steps.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-8">
        {steps.map((step, index) => (
          <div key={index} className="relative">
            {index < steps.length - 1 && (
              <div className="hidden md:block absolute top-16 left-full w-full h-0.5 bg-slate-200 -translate-x-1/2 z-0" />
            )}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-slate-100 relative z-10">
              <div className="flex flex-col items-center text-center">
                <div className="p-3 bg-teal-50 rounded-full mb-4">
                  <step.icon className="h-6 w-6 text-teal-500" />
                </div>
                <h3 className="text-xl font-semibold mb-2">{step.title}</h3>
                <p className="text-slate-600">{step.description}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}

