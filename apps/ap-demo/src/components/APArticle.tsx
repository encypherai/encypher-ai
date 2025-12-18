"use client";

import { useState } from "react";
import { Newspaper, Shield, Loader2, CheckCircle2, FileWarning } from "lucide-react";
import { cn } from "@/lib/utils";
import { AP_ARTICLE, generateDocumentId } from "@/lib/demo-data";
import { encodeContent, EmbeddingInfo } from "@/lib/api";

interface APArticleProps {
  onContentMarked: (markedContent: string, embeddings?: EmbeddingInfo[]) => void;
  markedContent: string | null;
  highlightedSentence?: string | null;
}

export default function APArticle({ onContentMarked, markedContent, highlightedSentence }: APArticleProps) {
  const [isMarking, setIsMarking] = useState(false);
  const [isMarked, setIsMarked] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [embeddedParagraphs, setEmbeddedParagraphs] = useState<string[]>([]);

  const handleMarkContent = async () => {
    setIsMarking(true);
    setError(null);
    
    try {
      const fullText = AP_ARTICLE.paragraphs.join("\n\n");
      
      const response = await encodeContent({
        document_id: generateDocumentId(),
        text: fullText,
        metadata: {
          title: AP_ARTICLE.headline,
          author: AP_ARTICLE.byline,
          source: AP_ARTICLE.source,
          published_at: new Date().toISOString(),
        },
      });
      
      if (response.success && response.embedded_content) {
        onContentMarked(response.embedded_content, response.embeddings);
        
        // Map embedded sentences back to original paragraph structure
        // The embeddings array contains each sentence with its embedded text
        if (response.embeddings && response.embeddings.length > 0) {
          // Build a map of original sentences to embedded sentences
          const embeddedSentences = response.embeddings
            .filter((e: { text?: string }) => e.text)
            .map((e: { text?: string }) => e.text as string);
          
          // Reconstruct paragraphs using embedded sentences
          const reconstructedParagraphs: string[] = [];
          let sentenceIndex = 0;
          
          for (const originalParagraph of AP_ARTICLE.paragraphs) {
            const originalSentences = originalParagraph.split(/(?<=[.!?])\s+/);
            const embeddedParagraphSentences: string[] = [];
            
            for (let i = 0; i < originalSentences.length && sentenceIndex < embeddedSentences.length; i++) {
              embeddedParagraphSentences.push(embeddedSentences[sentenceIndex]);
              sentenceIndex++;
            }
            
            reconstructedParagraphs.push(embeddedParagraphSentences.join(' '));
          }
          
          setEmbeddedParagraphs(reconstructedParagraphs);
        } else {
          // Fallback: split by double newline
          const paragraphs = response.embedded_content.split("\n\n");
          setEmbeddedParagraphs(paragraphs);
        }
        
        setIsMarked(true);
      } else {
        throw new Error("Failed to embed provenance");
      }
    } catch (err) {
      console.error("Error marking content:", err);
      setError(err instanceof Error ? err.message : "Failed to mark content");
      
      // For demo purposes, use placeholder if API fails
      const fullText = AP_ARTICLE.paragraphs.join("\n\n");
      onContentMarked(fullText);
      setEmbeddedParagraphs(AP_ARTICLE.paragraphs);
      setIsMarked(true);
    } finally {
      setIsMarking(false);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
      {/* AP Header */}
      <div className="bg-ap-dark text-white px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="bg-ap-red p-2 rounded">
            <Newspaper className="w-5 h-5" />
          </div>
          <div>
            <div className="font-bold text-lg">Associated Press</div>
            <div className="text-gray-400 text-sm">apnews.com</div>
          </div>
        </div>
        <div className="text-right text-sm text-gray-400">
          {AP_ARTICLE.date}
        </div>
      </div>

      {/* Article Content */}
      <div className="p-6">
        {/* Headline */}
        <h1 className="text-2xl font-bold text-gray-900 mb-3 leading-tight">
          {AP_ARTICLE.headline}
        </h1>
        
        {/* Byline */}
        <div className="text-gray-600 text-sm mb-4">
          {AP_ARTICLE.byline}
        </div>
        
        {/* Dateline */}
        <div className="text-gray-500 text-sm mb-6 font-medium">
          {AP_ARTICLE.dateline} —
        </div>

        {/* Article Body */}
        <div 
          id="ap-article-body"
          className={cn(
            "space-y-4 text-gray-800 leading-relaxed transition-all duration-500",
            isMarked && "bg-green-50/50 -mx-4 px-4 py-4 rounded-lg border border-green-200"
          )}
        >
          {(isMarked && embeddedParagraphs.length > 0 ? embeddedParagraphs : AP_ARTICLE.paragraphs).map((paragraph, index) => {
            const isHighlighted = highlightedSentence && paragraph.includes(highlightedSentence);
            
            return (
              <p 
                key={index} 
                id={`paragraph-${index}`}
                className={cn(
                  "transition-all duration-300",
                  isMarked && "relative",
                  isHighlighted && "bg-yellow-100 -mx-2 px-2 py-1 rounded border-l-4 border-yellow-400 scroll-mt-32"
                )}
              >
                {isMarked ? (
                  // Sentence-level granularity view when marked - use embedded content
                  <span className="relative group">
                    {paragraph.split(/(?<=[.!?])\s+/).map((sentence, sIndex) => (
                      <span 
                        key={sIndex} 
                        className="relative inline hover:bg-green-100 rounded transition-colors cursor-default"
                      >
                        {sentence}{' '}
                        <span className="opacity-0 group-hover:opacity-100 absolute -top-6 left-0 text-[10px] bg-green-600 text-white px-1.5 py-0.5 rounded whitespace-nowrap z-10 pointer-events-none">
                          Sentence {sIndex + 1} • Signed ✓
                        </span>
                      </span>
                    ))}
                  </span>
                ) : (
                  paragraph
                )}
                {isMarked && (
                  <span className="absolute -left-2 top-0 w-1 h-full bg-green-400 rounded-full opacity-50" />
                )}
              </p>
            );
          })}
        </div>

        {/* Provenance Status */}
        {isMarked && (
          <div className="mt-6 space-y-2">
            <div className="flex items-center gap-2 text-green-700 bg-green-100 px-4 py-3 rounded-lg">
              <CheckCircle2 className="w-5 h-5" />
              <span className="font-medium">Provenance embedded at sentence level</span>
              <span className="text-green-600 text-sm ml-auto">
                Invisible cryptographic signatures applied
              </span>
            </div>
            <div className="flex items-center gap-2 text-amber-700 bg-amber-50 px-4 py-3 rounded-lg border border-amber-200">
              <FileWarning className="w-5 h-5" />
              <span className="font-medium">Formal Notice Capability Enabled</span>
              <span className="text-amber-600 text-sm ml-auto">
                Content marked as owned by Associated Press
              </span>
            </div>
          </div>
        )}

        {error && (
          <div className="mt-4 text-amber-700 bg-amber-50 px-4 py-3 rounded-lg text-sm">
            Note: Using demo mode. {error}
          </div>
        )}
      </div>

      {/* Action Bar */}
      <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
        <div className="flex items-center justify-between">
          <div className="text-sm text-gray-500">
            {isMarked ? (
              <span className="text-green-600 font-medium">
                ✓ Content marked with cryptographic provenance
              </span>
            ) : (
              "Standard AP article - no provenance embedded"
            )}
          </div>
          
          <button
            onClick={handleMarkContent}
            disabled={isMarking || isMarked}
            className={cn(
              "flex items-center gap-2 px-5 py-2.5 rounded-lg font-medium transition-all",
              isMarked
                ? "bg-green-100 text-green-700 cursor-default"
                : "bg-blue-ncs text-white hover:bg-blue-ncs/90 active:scale-95"
            )}
          >
            {isMarking ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Embedding Provenance...
              </>
            ) : isMarked ? (
              <>
                <Shield className="w-4 h-4" />
                Provenance Embedded
              </>
            ) : (
              <>
                <Shield className="w-4 h-4" />
                Embed Provenance
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
