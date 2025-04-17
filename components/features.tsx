import { Clock, Sparkles, VolumeX, Mic2 } from "lucide-react"

const features = [
  {
    icon: Clock,
    title: "Fast Conversion",
    description: "Get your audiobook in under 60 seconds, no matter the length of your text.",
  },
  {
    icon: Sparkles,
    title: "AI-Powered Tagging",
    description: "Our AI automatically identifies characters, emotions, and context for natural narration.",
  },
  {
    icon: VolumeX,
    title: "No Background Noise",
    description: "Crystal clear audio without the background noise found in traditional recordings.",
  },
  {
    icon: Mic2,
    title: "Natural Voices",
    description: "Choose from a variety of lifelike voices or let our AI select the best match for your content.",
  },
]

export function Features() {
  return (
    <section className="py-12">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold mb-4">Why Choose Sound Scribe</h2>
        <p className="text-slate-600 max-w-2xl mx-auto">
          Our AI-powered platform offers unique advantages over traditional audiobook creation methods.
        </p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
        {features.map((feature, index) => (
          <div key={index} className="bg-white rounded-xl p-6 shadow-sm border border-slate-100">
            <div className="p-3 bg-teal-50 rounded-full w-fit mb-4">
              <feature.icon className="h-6 w-6 text-teal-500" />
            </div>
            <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
            <p className="text-slate-600">{feature.description}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

