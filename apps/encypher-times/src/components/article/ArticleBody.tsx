interface ArticleBodyProps {
  paragraphs: string[];
  signedText: string;
}

export function ArticleBody({ paragraphs, signedText }: ArticleBodyProps) {
  // If we have signed text with ZWC markers, render it preserving the invisible characters.
  // The Chrome extension will detect these markers in the DOM.
  // If we only have paragraph array (placeholder mode), render those instead.
  const hasSigned = signedText && signedText.length > 0;

  if (hasSigned) {
    // Split signed text by double newline to get paragraphs while preserving ZWC chars
    const signedParagraphs = signedText.split(/\n\n+/).filter((p) => p.trim());
    return (
      <div className="article-prose">
        {signedParagraphs.map((paragraph, i) => (
          <p key={i}>{paragraph}</p>
        ))}
      </div>
    );
  }

  return (
    <div className="article-prose">
      {paragraphs.map((paragraph, i) => (
        <p key={i}>{paragraph}</p>
      ))}
    </div>
  );
}
