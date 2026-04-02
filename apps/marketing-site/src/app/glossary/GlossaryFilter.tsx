'use client';

import React, { useState, useMemo } from 'react';
import Link from 'next/link';

export interface GlossaryTerm {
  id: string;
  name: string;
  letter: string;
  definition: string;
  relatedLinks?: Array<{ label: string; href: string }>;
}

interface GlossaryFilterProps {
  terms: GlossaryTerm[];
}

export function GlossaryFilter({ terms }: GlossaryFilterProps) {
  const [query, setQuery] = useState('');
  const [activeLetter, setActiveLetter] = useState<string | null>(null);

  const filtered = useMemo(() => {
    let result = terms;
    if (activeLetter) {
      result = result.filter(t => t.letter === activeLetter);
    }
    if (query.trim()) {
      const q = query.toLowerCase();
      result = result.filter(
        t => t.name.toLowerCase().includes(q) || t.definition.toLowerCase().includes(q)
      );
    }
    return result;
  }, [terms, query, activeLetter]);

  const letters = useMemo(() => {
    const set = new Set(terms.map(t => t.letter));
    return Array.from(set).sort();
  }, [terms]);

  const groupedByLetter = useMemo(() => {
    const groups: Record<string, GlossaryTerm[]> = {};
    for (const term of filtered) {
      if (!groups[term.letter]) groups[term.letter] = [];
      groups[term.letter].push(term);
    }
    return groups;
  }, [filtered]);

  const sortedLetters = Object.keys(groupedByLetter).sort();

  return (
    <>
      {/* Search and filter controls */}
      <div className="sticky top-16 z-10 bg-background/95 backdrop-blur py-4 border-b border-border mb-8">
        <div className="max-w-4xl mx-auto">
          <input
            type="search"
            placeholder="Search terms and definitions..."
            value={query}
            onChange={e => { setQuery(e.target.value); setActiveLetter(null); }}
            className="w-full px-4 py-2.5 rounded-lg border border-border bg-muted/30 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 mb-4"
            aria-label="Search glossary terms"
          />
          <div className="flex flex-wrap gap-1.5">
            <button
              onClick={() => { setActiveLetter(null); setQuery(''); }}
              className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${activeLetter === null && !query ? 'text-white' : 'bg-muted/50 text-muted-foreground hover:bg-muted'}`}
              style={activeLetter === null && !query ? { backgroundColor: '#2a87c4', color: '#ffffff' } : {}}
            >
              All
            </button>
            {letters.map(letter => (
              <button
                key={letter}
                onClick={() => { setActiveLetter(activeLetter === letter ? null : letter); setQuery(''); }}
                className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${activeLetter === letter ? 'text-white' : 'bg-muted/50 text-muted-foreground hover:bg-muted'}`}
                style={activeLetter === letter ? { backgroundColor: '#2a87c4', color: '#ffffff' } : {}}
                aria-label={`Filter terms starting with ${letter}`}
              >
                {letter}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Results count */}
      {(query || activeLetter) && (
        <div className="max-w-4xl mx-auto mb-6 text-sm text-muted-foreground">
          {filtered.length === 0
            ? 'No terms match your search.'
            : `${filtered.length} term${filtered.length === 1 ? '' : 's'} found.`}
        </div>
      )}

      {/* Terms grouped by letter */}
      <div className="max-w-4xl mx-auto space-y-10">
        {sortedLetters.map(letter => (
          <div key={letter}>
            <h2
              className="text-2xl font-bold mb-4 pb-2 border-b border-border"
              id={`letter-${letter}`}
              style={{ color: '#2a87c4' }}
            >
              {letter}
            </h2>
            <div className="space-y-8">
              {groupedByLetter[letter].map(term => (
                <div key={term.id} id={term.id} className="scroll-mt-52">
                  <h3 className="text-lg font-semibold mb-2">{term.name}</h3>
                  <p className="text-muted-foreground text-sm leading-relaxed mb-3">{term.definition}</p>
                  {term.relatedLinks && term.relatedLinks.length > 0 && (
                    <div className="flex flex-wrap gap-3">
                      {term.relatedLinks.map(link => (
                        <Link
                          key={link.href}
                          href={link.href}
                          className="text-xs underline hover:opacity-80"
                          style={{ color: '#2a87c4' }}
                        >
                          {link.label} &rarr;
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}

        {filtered.length === 0 && (
          <div className="text-center py-16 text-muted-foreground">
            No terms match your search. Try a broader term.
          </div>
        )}
      </div>
    </>
  );
}
