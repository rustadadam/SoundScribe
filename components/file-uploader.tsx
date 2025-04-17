"use client"

import type React from "react"

import { useState } from "react"
import { Upload, Check, AlertCircle, Loader2, Play, Download, BookText } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"

type Status = "idle" | "uploading" | "processing" | "complete" | "error"

export function FileUploader() {
  const [file, setFile] = useState<File | null>(null)
  const [status, setStatus] = useState<Status>("idle")
  const [progress, setProgress] = useState(0)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile && selectedFile.type === "text/plain") {
      setFile(selectedFile)
      setStatus("idle")
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return

    // Simulate the upload and processing
    setStatus("uploading")
    setProgress(0)

    // Simulate upload progress
    const uploadInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 40) {
          clearInterval(uploadInterval)
          simulateProcessing()
          return 40
        }
        return prev + 5
      })
    }, 200)

    const simulateProcessing = () => {
      setStatus("processing")

      // Simulate processing progress
      const processInterval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 100) {
            clearInterval(processInterval)
            setStatus("complete")
            // Mock audio URL
            setAudioUrl(`${file.name.replace(".txt", "")}.mp3`)
            return 100
          }
          return prev + 5
        })
      }, 200)
    }
  }

  const resetForm = () => {
    setFile(null)
    setStatus("idle")
    setProgress(0)
    setAudioUrl(null)
  }

  return (
    <section id="upload" className="scroll-mt-16">
      <div className="max-w-3xl mx-auto">
        <h2 className="text-2xl font-bold text-center mb-6">Upload Your Text File</h2>

        <Card className="border-2 border-dashed border-slate-200">
          <CardContent className="p-6">
            {status === "idle" && (
              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="flex flex-col items-center justify-center py-6 px-6 bg-slate-50 rounded-lg">
                  {!file ? (
                    <>
                      <div className="flex items-center mb-4">
                        <Upload className="h-8 w-8 text-slate-400 mr-3" />
                        <p className="text-lg font-medium">Drag and drop your text file here</p>
                      </div>
                      <input
                        id="file-upload"
                        type="file"
                        accept=".txt"
                        onChange={handleFileChange}
                        className="hidden"
                      />
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => document.getElementById("file-upload")?.click()}
                      >
                        Select .txt File
                      </Button>
                    </>
                  ) : (
                    <div className="w-full space-y-4">
                      <div className="flex items-center justify-between p-4 bg-white rounded-lg border border-slate-200">
                        <div className="flex items-center space-x-3">
                          <div className="p-2 bg-slate-100 rounded">
                            <BookText className="h-5 w-5 text-slate-600" />
                          </div>
                          <div>
                            <p className="font-medium">{file.name}</p>
                            <p className="text-sm text-slate-500">{(file.size / 1024).toFixed(2)} KB</p>
                          </div>
                        </div>
                        <Button type="button" variant="ghost" size="sm" onClick={() => setFile(null)}>
                          Change
                        </Button>
                      </div>
                      <Button type="submit" className="w-full bg-teal-500 hover:bg-teal-600">
                        Generate Audiobook
                      </Button>
                    </div>
                  )}
                </div>
              </form>
            )}

            {status === "idle" && !file && (
              <div className="mt-6 p-6 bg-slate-50 rounded-lg border border-dashed border-slate-200 opacity-60">
                <div className="text-center mb-4">
                  <p className="text-sm text-slate-500 mb-1">After processing, you'll be able to:</p>
                  <h3 className="text-lg font-medium text-slate-400">Preview Your Audiobook</h3>
                </div>

                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                  <div className="flex-1 bg-white p-4 rounded-lg border border-slate-200 flex items-center gap-3">
                    <div className="p-2 bg-slate-100 rounded-full">
                      <BookText className="h-5 w-5 text-slate-400" />
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-slate-400">your-book-title.mp3</p>
                      <p className="text-xs text-slate-400">Generated in under 60 seconds</p>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button disabled variant="outline" size="sm" className="flex gap-2 items-center">
                      <Play className="h-4 w-4" />
                      Play
                    </Button>
                    <Button disabled variant="outline" size="sm" className="flex gap-2 items-center">
                      <Download className="h-4 w-4" />
                      Download MP3
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {(status === "uploading" || status === "processing") && (
              <div className="py-10 px-6 space-y-6">
                <div className="flex items-center justify-center">
                  <Loader2 className="h-8 w-8 text-teal-500 animate-spin" />
                </div>
                <div className="space-y-2 text-center">
                  <h3 className="text-lg font-medium">
                    {status === "uploading" ? "Uploading your text file..." : "Generating your audiobook..."}
                  </h3>
                  <p className="text-sm text-slate-500">
                    {status === "uploading"
                      ? "Your file is being uploaded and analyzed."
                      : "Our AI is creating natural-sounding voices for your content."}
                  </p>
                </div>
                <div className="space-y-2">
                  <Progress value={progress} className="h-2" />
                  <p className="text-sm text-slate-500 text-right">{progress}%</p>
                </div>
              </div>
            )}

            {status === "complete" && audioUrl && (
              <div className="py-10 px-6 space-y-6">
                <div className="flex items-center justify-center">
                  <div className="p-3 bg-teal-100 rounded-full">
                    <Check className="h-8 w-8 text-teal-600" />
                  </div>
                </div>
                <div className="space-y-2 text-center">
                  <h3 className="text-lg font-medium">Your audiobook is ready!</h3>
                  <p className="text-sm text-slate-500">Your text has been successfully converted to an audiobook.</p>
                </div>
                <div className="flex flex-col space-y-3">
                  <Button
                    className="bg-teal-500 hover:bg-teal-600"
                    onClick={() => {
                      // In a real app, this would download the actual file
                      alert("In a real app, this would download your audiobook.")
                    }}
                  >
                    Download Audiobook
                  </Button>
                  <Button variant="outline" onClick={resetForm}>
                    Convert Another File
                  </Button>
                </div>
              </div>
            )}

            {status === "error" && (
              <div className="py-10 px-6 space-y-6">
                <div className="flex items-center justify-center">
                  <div className="p-3 bg-red-100 rounded-full">
                    <AlertCircle className="h-8 w-8 text-red-600" />
                  </div>
                </div>
                <div className="space-y-2 text-center">
                  <h3 className="text-lg font-medium">Something went wrong</h3>
                  <p className="text-sm text-slate-500">There was an error processing your file. Please try again.</p>
                </div>
                <Button variant="outline" onClick={resetForm} className="w-full">
                  Try Again
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </section>
  )
}

