"use client";

import { useState, useEffect, useRef } from "react";
import Image from "next/image";
import { ArrowRight, RotateCcw, TreeDeciduous } from "lucide-react";
import Link from "next/link";
import APArticle from "@/components/APArticle";
import AIChatSimulator from "@/components/AIChatSimulator";
import VerificationDecoder from "@/components/VerificationDecoder";
import DownstreamSurvival from "@/components/DownstreamSurvival";

import { EmbeddingInfo } from "@/lib/api";

export default function APDemo() {
  const [currentStep, setCurrentStep] = useState(1);
  const [markedContent, setMarkedContent] = useState<string | null>(null);
  const [embeddings, setEmbeddings] = useState<EmbeddingInfo[]>([]);
  const [textToVerify, setTextToVerify] = useState<string | null>(null);
  const [isAccurate, setIsAccurate] = useState<boolean | null>(null);
  const [highlightedSentence, setHighlightedSentence] = useState<string | null>(null);
  const articleRef = useRef<HTMLDivElement>(null);

  const handleContentMarked = (content: string, embeddingsList?: EmbeddingInfo[]) => {
    setMarkedContent(content);
    if (embeddingsList) {
      setEmbeddings(embeddingsList);
    }
    setCurrentStep(2);
  };

  const handleQuoteSelected = (quote: string, accurate: boolean) => {
    setTextToVerify(quote);
    setIsAccurate(accurate);
    setCurrentStep(3);
  };

  const handleReset = () => {
    setTextToVerify(null);
    setIsAccurate(null);
    setCurrentStep(2);
  };

  const handleFullReset = () => {
    setCurrentStep(1);
    setMarkedContent(null);
    setTextToVerify(null);
    setIsAccurate(null);
    setHighlightedSentence(null);
  };

  const verifyRef = useRef<HTMLDivElement>(null);

  const handleVerificationComplete = (verifiedSentence: string | null) => {
    setHighlightedSentence(verifiedSentence);
  };

  // Scroll to verify section when quote is selected
  useEffect(() => {
    if (textToVerify && verifyRef.current) {
      setTimeout(() => {
        verifyRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 300);
    }
  }, [textToVerify]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Image
                src="/encypher_full_logo_color.svg"
                alt="Encypher"
                width={140}
                height={40}
                priority
              />
              <div className="border-l border-gray-300 pl-3 ml-1">
                <p className="text-sm font-medium text-delft-blue">AP Quote Integrity Demo</p>
              </div>
            </div>
            
            {/* Merkle Demo Link */}
            {/* <Link 
              href="/merkle"
              className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg text-sm font-medium hover:from-purple-600 hover:to-pink-600 transition-all"
            >
              <TreeDeciduous className="w-4 h-4" />
              Merkle Tree Demo
            </Link> */}
            
            {/* Progress Steps */}
            <div className="flex items-center gap-2">
              {[
                { num: 1, label: "Mark" },
                { num: 2, label: "Simulate AI" },
                { num: 3, label: "Verify" },
                { num: 4, label: "Survival" },
              ].map((step, index) => (
                <div key={step.num} className="flex items-center">
                  <div
                    className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all ${
                      currentStep >= step.num
                        ? "bg-columbia-blue/30 text-blue-ncs"
                        : "bg-gray-100 text-gray-400"
                    }`}
                  >
                    <span
                      className={`w-5 h-5 rounded-full flex items-center justify-center text-xs ${
                        currentStep >= step.num
                          ? "bg-blue-ncs text-white"
                          : "bg-gray-300 text-gray-500"
                      }`}
                    >
                      {step.num}
                    </span>
                    <span className="hidden sm:inline">{step.label}</span>
                  </div>
                  {index < 3 && (
                    <ArrowRight className="w-4 h-4 mx-1 text-gray-300" />
                  )}
                </div>
              ))}
            </div>

            <button
              onClick={handleFullReset}
              className="flex items-center gap-2 px-4 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <RotateCcw className="w-4 h-4" />
              <span className="hidden sm:inline">Reset Demo</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* Demo Title */}
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            AP Quote Integrity Test
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Demonstrating how cryptographic provenance enables verification of accurate attribution
            when AI systems quote AP content.
          </p>
        </div>

        {/* Step 1: AP Article */}
        <section className="mb-8">
          <div className="flex items-center gap-3 mb-4">
            <span className="bg-blue-ncs text-white w-8 h-8 rounded-full flex items-center justify-center font-bold">
              1
            </span>
            <h3 className="text-xl font-semibold text-gray-800">
              Mark Content
            </h3>
            {currentStep > 1 && (
              <span className="text-green-600 text-sm font-medium">
                ✓ Complete
              </span>
            )}
          </div>
          <p className="text-gray-600 mb-4 ml-11">
            This is an example AP article. Click to mark it with cryptographic provenance.
            The article carries an invisible signature, without affecting the reader experience.
          </p>
          <div ref={articleRef}>
            <APArticle
              onContentMarked={handleContentMarked}
              markedContent={markedContent}
              highlightedSentence={highlightedSentence}
            />
          </div>
        </section>

        {/* Step 2: AI Chat Simulation */}
        <section className={`mb-8 transition-opacity ${currentStep < 2 ? "opacity-50" : ""}`}>
          <div className="flex items-center gap-3 mb-4">
            <span
              className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                currentStep >= 2
                  ? "bg-blue-ncs text-white"
                  : "bg-gray-300 text-gray-500"
              }`}
            >
              2
            </span>
            <h3 className="text-xl font-semibold text-gray-800">
              Simulate AI Use Case
            </h3>
            {currentStep > 2 && (
              <span className="text-green-600 text-sm font-medium">
                ✓ Quote Selected
              </span>
            )}
          </div>
          <p className="text-gray-600 mb-4 ml-11">
            Simulate what happens when an AI system uses this content. The question:
            <strong> Is that quote accurate, or did AI hallucinate it?</strong>
          </p>
          <AIChatSimulator
            onQuoteSelected={handleQuoteSelected}
            disabled={currentStep < 2}
            markedContent={markedContent}
            embeddings={embeddings}
          />
        </section>

        {/* Step 3: Verification */}
        <section ref={verifyRef} className={`mb-8 transition-opacity scroll-mt-24 ${currentStep < 3 ? "opacity-50" : ""}`}>
          <div className="flex items-center gap-3 mb-4">
            <span
              className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                currentStep >= 3
                  ? "bg-blue-ncs text-white"
                  : "bg-gray-300 text-gray-500"
              }`}
            >
              3
            </span>
            <h3 className="text-xl font-semibold text-gray-800">
              Verify Quote
            </h3>
          </div>
          <p className="text-gray-600 mb-4 ml-11">
            Let&apos;s check if the AI&apos;s quote matches AP&apos;s original publication.
          </p>
          <VerificationDecoder
            textToVerify={textToVerify}
            isAccurate={isAccurate}
            markedContent={markedContent}
            onReset={handleReset}
            onVerificationComplete={handleVerificationComplete}
          />
        </section>

        {/* Step 4: Downstream Survival */}
        <section className={`mb-8 transition-opacity ${currentStep < 2 ? "opacity-50" : ""}`}>
          <div className="flex items-center gap-3 mb-4">
            <span
              className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                markedContent
                  ? "bg-blue-ncs text-white"
                  : "bg-gray-300 text-gray-500"
              }`}
            >
              4
            </span>
            <h3 className="text-xl font-semibold text-gray-800">
              Downstream Survival
            </h3>
          </div>
          <p className="text-gray-600 mb-4 ml-11">
            Copy the marked text and paste it anywhere. Simulating scraping, syndication, or database storage.
            Provenance survives.
          </p>
          <DownstreamSurvival markedContent={markedContent} />
        </section>

        {/* Closing Statement */}
        <section className="bg-gradient-to-r from-delft-blue to-blue-ncs rounded-2xl p-8 text-white text-center">
          <h3 className="text-2xl font-bold mb-4">
            What This Means for AP
          </h3>
          <p className="text-lg text-columbia-blue max-w-3xl mx-auto mb-6">
            Every article leaving the wire could carry this proof, through B2B licensees, 
            through scrapers, and via copy-paste into AI systems. When someone says 
            &quot;According to AP,&quot; you can verify whether that&apos;s true.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="bg-white/10 rounded-xl p-4">
              <div className="text-3xl font-bold">Proves</div>
              <div className="text-columbia-blue">It&apos;s yours</div>
            </div>
            <div className="bg-white/10 rounded-xl p-4">
              <div className="text-3xl font-bold">Proves</div>
              <div className="text-columbia-blue">It wasn&apos;t changed</div>
            </div>
            <div className="bg-white/10 rounded-xl p-4">
              <div className="text-3xl font-bold">Survives</div>
              <div className="text-columbia-blue">Wherever it goes</div>
            </div>
          </div>
          <p className="mt-6 text-sm text-columbia-blue">
            Compliant with C2PA, coming in January 2026
          </p>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white mt-12">
        <div className="max-w-7xl mx-auto px-6 py-6 text-center text-gray-500 text-sm">
          <p>Encypher — Cryptographic Provenance for Digital Content</p>
          <p className="mt-1">Demo prepared for Associated Press</p>
        </div>
      </footer>
    </div>
  );
}
