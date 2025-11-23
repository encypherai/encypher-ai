import React from 'react';

interface YouTubeEmbedProps {
  videoId: string;
  title?: string;
  className?: string;
}

const YouTubeEmbed: React.FC<YouTubeEmbedProps> = ({ 
  videoId, 
  title = 'YouTube video player', 
  className = '' 
}) => {
  return (
    // Outer div maintains aspect ratio and applies passed className
    <div className={`relative w-full overflow-hidden ${className}`} style={{ paddingTop: '56.25%' /* 16:9 Aspect Ratio */ }}> 
      <iframe
        className="absolute top-0 left-0 w-full h-full" // iframe fills the aspect ratio container
        src={`https://www.youtube.com/embed/${videoId}?rel=0`}
        title={title}
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowFullScreen
      ></iframe>
    </div>
  );
};

export default YouTubeEmbed;
