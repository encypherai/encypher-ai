import React from 'react';

export interface AISummaryProps {
  title: string;
  whatWeDo: string;
  whoItsFor: string;
  keyDifferentiator: string;
  primaryValue: string;
}

export function AISummary({ title, whatWeDo, whoItsFor, keyDifferentiator, primaryValue }: AISummaryProps) {
  return (
    <div style={{ display: 'none' }} data-ai-summary="true">
      <h1>{title}</h1>
      <p><strong>What Encypher does:</strong> {whatWeDo}</p>
      <p><strong>Who it's for:</strong> {whoItsFor}</p>
      <p><strong>Key differentiator:</strong> {keyDifferentiator}</p>
      <p><strong>Primary value:</strong> {primaryValue}</p>
    </div>
  );
}

export default AISummary;
