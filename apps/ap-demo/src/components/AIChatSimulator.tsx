"use client";

import { useState, useEffect } from "react";
import { Bot, Send, User, Sparkles, ExternalLink } from "lucide-react";
import { cn } from "@/lib/utils";
import { AI_CHAT_SCENARIOS, Citation, QuoteData } from "@/lib/demo-data";
import { EmbeddingInfo } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  isTyping?: boolean;
}

interface AIChatSimulatorProps {
  onQuoteSelected: (quote: string, isAccurate: boolean, displayQuote?: string, modifications?: { original: string; modified: string }[]) => void;
  disabled?: boolean;
  markedContent?: string | null;
  embeddings?: EmbeddingInfo[];
}

export default function AIChatSimulator({ onQuoteSelected, disabled, markedContent, embeddings }: AIChatSimulatorProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [activeScenario, setActiveScenario] = useState<"accurate" | "modified" | null>(null);
  const [isTyping, setIsTyping] = useState(false);
  const [displayedText, setDisplayedText] = useState("");
  const [hoveredQuoteId, setHoveredQuoteId] = useState<number | null>(null);

  // Typing animation effect
  useEffect(() => {
    if (!isTyping || !activeScenario) return;

    const scenario = AI_CHAT_SCENARIOS[activeScenario];
    const fullText = scenario.response;
    let currentIndex = 0;

    const typingInterval = setInterval(() => {
      if (currentIndex <= fullText.length) {
        setDisplayedText(fullText.slice(0, currentIndex));
        currentIndex += 3; // Type 3 characters at a time for speed
      } else {
        clearInterval(typingInterval);
        setIsTyping(false);
        // Add the complete message
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            role: "assistant",
            content: fullText,
          };
          return updated;
        });
      }
    }, 20);

    return () => clearInterval(typingInterval);
  }, [isTyping, activeScenario]);

  const runScenario = (scenario: "accurate" | "modified") => {
    if (disabled) return;
    
    setActiveScenario(scenario);
    const scenarioData = AI_CHAT_SCENARIOS[scenario];
    
    // Add user message
    setMessages([
      { role: "user", content: scenarioData.prompt },
      { role: "assistant", content: "", isTyping: true },
    ]);
    
    // Start typing animation
    setIsTyping(true);
    setDisplayedText("");
  };

  // Handle clicking a specific quote citation
  const handleSelectQuoteById = (quoteId: number) => {
    if (!activeScenario) return;
    const scenario = AI_CHAT_SCENARIOS[activeScenario];
    const quote = scenario.quotes?.find((q: QuoteData) => q.id === quoteId);
    if (!quote) return;
    
    // For accurate quotes, find the embedded version from markedContent
    // The embeddings array has "basic" format, but markedContent has the full C2PA wrapper
    let quoteToVerify = quote.text;
    if (quote.isAccurate && markedContent) {
      // Find the sentence in markedContent that matches this quote
      // markedContent contains the full article with embedded provenance
      // We need to extract the exact sentence with its invisible characters
      
      // Split markedContent by sentence boundaries while preserving invisible chars
      // Use a regex that matches sentence endings but keeps the invisible chars attached
      const sentences = markedContent.split(/(?<=[.!?])\s+/);
      
      const matchingSentence = sentences.find(s => {
        // Strip invisible chars for comparison only
        const visibleSentence = s.replace(/[\u200B-\u200D\uFEFF\uE0100-\uE01EF\uFE00-\uFE0F]/g, '');
        // Check if this sentence matches the quote
        return quote.text.startsWith(visibleSentence.slice(0, 40)) || 
               visibleSentence.startsWith(quote.text.slice(0, 40));
      });
      
      if (matchingSentence) {
        // Use the sentence from markedContent which has the C2PA manifest
        quoteToVerify = matchingSentence;
        console.log('Found matching sentence with embedded provenance:', quoteToVerify.length, 'chars');
      } else {
        console.log('No matching sentence found in markedContent');
      }
    }
    
    // Pass the text to verify, accuracy flag, display quote, and modifications
    onQuoteSelected(quoteToVerify, quote.isAccurate, quote.text, quote.modifications);
  };

  const handleSelectQuote = () => {
    if (!activeScenario) return;
    // Default to first quote
    handleSelectQuoteById(1);
  };

  // Get quote by ID for highlighting
  const getQuoteById = (quoteId: number): QuoteData | undefined => {
    if (!activeScenario) return undefined;
    return AI_CHAT_SCENARIOS[activeScenario].quotes?.find((q: QuoteData) => q.id === quoteId);
  };

  // Render text with inline citation badges [1], [2], etc. and highlight quoted text on hover
  const renderTextWithCitations = (text: string) => {
    // First, wrap quoted text in spans that can be highlighted
    let processedText = text;
    const quotes = activeScenario ? AI_CHAT_SCENARIOS[activeScenario].quotes || [] : [];
    
    // Split by citation markers and quoted text
    const parts = text.split(/(\[\d+\]|"[^"]+"|"[^"]+"|'[^']+')/);
    
    return parts.map((part, index) => {
      // Check if this is a citation badge
      const citationMatch = part.match(/^\[(\d+)\]$/);
      if (citationMatch) {
        const quoteId = parseInt(citationMatch[1]);
        const quote = getQuoteById(quoteId);
        return (
          <button
            key={index}
            onClick={() => handleSelectQuoteById(quoteId)}
            onMouseEnter={() => setHoveredQuoteId(quoteId)}
            onMouseLeave={() => setHoveredQuoteId(null)}
            className={cn(
              "inline-flex items-center justify-center w-4 h-4 ml-0.5 text-[10px] font-bold text-white rounded-sm align-super cursor-pointer transition-colors",
              hoveredQuoteId === quoteId ? "bg-yellow-500 scale-110" : "bg-blue-500 hover:bg-blue-600"
            )}
            title={`Click to verify quote ${quoteId}${quote?.isAccurate ? ' (accurate)' : ' (modified)'}`}
          >
            {citationMatch[1]}
          </button>
        );
      }
      
      // Check if this is quoted text that matches a quote
      const isQuotedText = part.startsWith('"') || part.startsWith('"') || part.startsWith("'");
      if (isQuotedText && activeScenario) {
        const cleanQuote = part.replace(/^["'"']|["'"']$/g, '');
        const matchingQuote = quotes.find((q: QuoteData) => 
          q.text.includes(cleanQuote) || cleanQuote.includes(q.text.slice(0, 50))
        );
        
        if (matchingQuote) {
          const isHighlighted = hoveredQuoteId === matchingQuote.id;
          return (
            <span 
              key={index}
              className={cn(
                "transition-all duration-200 rounded px-0.5",
                isHighlighted && "bg-yellow-200 ring-2 ring-yellow-400"
              )}
            >
              {part}
            </span>
          );
        }
      }
      
      return <span key={index}>{part}</span>;
    });
  };

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200">
      {/* Header */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 text-white px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="bg-green-500 p-2 rounded-lg">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="font-bold">AI Assistant</div>
            <div className="text-gray-400 text-sm">Simulated AI Response</div>
          </div>
        </div>
      </div>

      {/* Scenario Buttons */}
      <div className="p-4 bg-gray-50 border-b border-gray-200">
        <div className="text-sm text-gray-600 mb-3 font-medium">
          Select a scenario to simulate:
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => runScenario("accurate")}
            disabled={disabled || isTyping}
            className={cn(
              "flex-1 px-4 py-3 rounded-lg text-sm font-medium transition-all",
              activeScenario === "accurate"
                ? "bg-green-100 text-green-700 border-2 border-green-500"
                : "bg-white border border-gray-300 text-gray-700 hover:bg-gray-50",
              (disabled || isTyping) && "opacity-50 cursor-not-allowed"
            )}
          >
            <div className="font-semibold">Accurate Quote</div>
            <div className="text-xs opacity-75 mt-1">AI quotes AP correctly</div>
          </button>
          <button
            onClick={() => runScenario("modified")}
            disabled={disabled || isTyping}
            className={cn(
              "flex-1 px-4 py-3 rounded-lg text-sm font-medium transition-all",
              activeScenario === "modified"
                ? "bg-red-100 text-red-700 border-2 border-red-500"
                : "bg-white border border-gray-300 text-gray-700 hover:bg-gray-50",
              (disabled || isTyping) && "opacity-50 cursor-not-allowed"
            )}
          >
            <div className="font-semibold">Modified Quote</div>
            <div className="text-xs opacity-75 mt-1">AI alters AP content</div>
          </button>
        </div>
      </div>

      {/* Chat Messages */}
      <div className="h-80 overflow-y-auto p-4 space-y-4 bg-gray-50">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center text-gray-400">
            <div className="text-center">
              <Bot className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Select a scenario above to see how AI might quote AP content</p>
            </div>
          </div>
        ) : (
          messages.map((message, index) => (
            <div
              key={index}
              className={cn(
                "flex gap-3",
                message.role === "user" ? "justify-end" : "justify-start"
              )}
            >
              {message.role === "assistant" && (
                <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center flex-shrink-0">
                  <Bot className="w-4 h-4 text-white" />
                </div>
              )}
              <div
                className={cn(
                  "max-w-[80%] rounded-2xl px-4 py-3",
                  message.role === "user"
                    ? "bg-blue-500 text-white rounded-br-md"
                    : "bg-white text-gray-800 rounded-bl-md shadow-sm border border-gray-200"
                )}
              >
                {message.isTyping ? (
                  <span>
                    {renderTextWithCitations(displayedText)}
                    <span className="typing-cursor" />
                  </span>
                ) : (
                  <>
                    <span className="whitespace-pre-wrap">{renderTextWithCitations(message.content)}</span>
                    {/* Citation badges - show after AI response is complete */}
                    {message.role === "assistant" && activeScenario && !isTyping && (
                      <div className="mt-3 pt-3 border-t border-gray-200">
                        <div className="text-xs text-gray-500 mb-2">Sources</div>
                        <div className="flex flex-wrap gap-2">
                          {AI_CHAT_SCENARIOS[activeScenario].citations.map((citation: Citation) => (
                            <button
                              key={citation.id}
                              onClick={handleSelectQuote}
                              className="flex items-center gap-1.5 px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded text-xs text-gray-700 transition-colors"
                            >
                              <span className="w-4 h-4 bg-red-600 text-white rounded text-[10px] flex items-center justify-center font-bold">AP</span>
                              <span>{citation.source}</span>
                              <ExternalLink className="w-3 h-3 text-gray-400" />
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
              {message.role === "user" && (
                <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0">
                  <User className="w-4 h-4 text-white" />
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Action Bar */}
      {activeScenario && !isTyping && messages.length > 0 && (
        <div className="p-4 bg-white border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-600">
              <span className="font-medium">Question:</span> Is that quote accurate, or did the AI hallucinate it?
              <span className="text-gray-400 ml-2">Click the AP citation badge above or:</span>
            </div>
            <button
              onClick={handleSelectQuote}
              className="flex items-center gap-2 px-4 py-2 bg-delft-blue text-white rounded-lg font-medium hover:bg-delft-blue/90 transition-all active:scale-95"
            >
              <Send className="w-4 h-4" />
              Verify Quote
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
