export interface SignedImageRef {
  filename: string;
  alt: string;
  credit: string;
  caption: string;
  width: number;
  height: number;
  documentId: string;
  c2paSigned: boolean;
  signedAt: string;
}

export interface SignedAudioRef {
  filename: string;
  title: string;
  duration: number;
  credit: string;
  documentId: string;
  c2paSigned: boolean;
  signedAt: string;
}

export interface SignedVideoRef {
  filename: string;
  title: string;
  duration: number;
  credit: string;
  poster: string;
  documentId: string;
  c2paSigned: boolean;
  signedAt: string;
}

export type SectionSlug =
  | "technology"
  | "policy"
  | "media"
  | "analysis"
  | "opinion";

export interface SignedArticle {
  slug: string;
  section: SectionSlug;
  headline: string;
  deck: string;
  byline: string;
  dateline: string;
  publishedAt: string;
  updatedAt?: string;
  signedAt: string;
  documentId: string;
  merkleRoot?: string;
  signedText: string;
  paragraphs: string[];
  heroImage?: SignedImageRef;
  inlineImages: SignedImageRef[];
  audio?: SignedAudioRef;
  video?: SignedVideoRef;
  tags: string[];
  wordCount: number;
  featured: boolean;
  teaser: string;
}

export interface ContentManifest {
  generatedAt: string;
  articleCount: number;
  imageCount: number;
  audioCount: number;
  videoCount: number;
  articles: SignedArticle[];
}
