'use client';

import {
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Input,
} from '@encypher/design-system';
import { useMutation } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import { Suspense, useCallback, useEffect, useRef, useState } from 'react';
import { Upload, Download, CheckCircle, XCircle, Image as ImageIcon, X, Loader2 } from 'lucide-react';
import { toast } from 'sonner';

import { DashboardLayout } from '../../components/layout/DashboardLayout';
import { useOrganization } from '../../contexts/OrganizationContext';
import { Switch } from '../../components/ui/switch';
import apiClient from '../../lib/api';

const ACCEPTED_TYPES = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp', 'image/tiff'];
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
const MAX_IMAGES = 20;

interface ImageFile {
  id: string;
  file: File;
  preview: string;
  b64: string;
}

interface SigningOptions {
  enableC2pa: boolean;
  enableTrustmark: boolean;
  documentTitle: string;
  imageQuality: number;
  indexForAttribution: boolean;
}

interface SignedImageData {
  image_id: string;
  filename: string;
  signed_image_b64: string;
  signed_image_hash: string;
  c2pa_manifest_instance_id: string;
  size_bytes: number;
  trustmark_applied: boolean;
  mime_type: string;
  c2pa_signed: boolean;
  phash?: string;
}

interface SigningResult {
  document_id: string;
  images: SignedImageData[];
  composite_manifest: {
    instance_id: string;
    ingredient_count: number;
    manifest_hash: string;
  };
  total_images: number;
  processing_time_ms: number;
}

function fileToBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const result = reader.result as string;
      // Strip the data:...;base64, prefix
      const b64 = result.split(',')[1];
      resolve(b64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function DropZone({
  images,
  onAdd,
  onRemove,
  disabled,
}: {
  images: ImageFile[];
  onAdd: (files: FileList) => void;
  onRemove: (id: string) => void;
  disabled: boolean;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      if (disabled) return;
      if (e.dataTransfer.files.length > 0) {
        onAdd(e.dataTransfer.files);
      }
    },
    [onAdd, disabled]
  );

  const handleDragOver = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      if (!disabled) setDragOver(true);
    },
    [disabled]
  );

  const handleDragLeave = useCallback(() => setDragOver(false), []);

  return (
    <div className="space-y-4">
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => !disabled && inputRef.current?.click()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${dragOver ? 'border-blue-ncs bg-blue-ncs/5' : 'border-border hover:border-blue-ncs/50'}
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
        `}
      >
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED_TYPES.join(',')}
          multiple
          onChange={(e) => e.target.files && onAdd(e.target.files)}
          className="hidden"
          disabled={disabled}
        />
        <Upload className="w-10 h-10 mx-auto text-muted-foreground mb-3" />
        <p className="text-sm font-medium">
          Drop images here or click to browse
        </p>
        <p className="text-xs text-muted-foreground mt-1">
          JPEG, PNG, WebP, TIFF -- up to 10MB each, {MAX_IMAGES} images max
        </p>
      </div>

      {images.length > 0 && (
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {images.map((img) => (
            <div key={img.id} className="relative group rounded-lg border border-border overflow-hidden">
              <img
                src={img.preview}
                alt={img.file.name}
                className="w-full h-32 object-cover"
              />
              <div className="absolute inset-0 bg-black/0 group-hover:bg-black/40 transition-colors" />
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onRemove(img.id);
                }}
                disabled={disabled}
                className="absolute top-1 right-1 p-1 rounded-full bg-black/60 text-white opacity-0 group-hover:opacity-100 transition-opacity hover:bg-black/80"
              >
                <X className="w-3 h-3" />
              </button>
              <div className="absolute bottom-0 left-0 right-0 bg-black/60 px-2 py-1">
                <p className="text-xs text-white truncate">{img.file.name}</p>
                <p className="text-xs text-white/70">{formatBytes(img.file.size)}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function SigningOptionsCard({
  options,
  onChange,
  disabled,
  isEnterprise,
}: {
  options: SigningOptions;
  onChange: (opts: SigningOptions) => void;
  disabled: boolean;
  isEnterprise: boolean;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Signing Options</CardTitle>
        <CardDescription>Configure how images will be signed.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Document Title</label>
          <Input
            value={options.documentTitle}
            onChange={(e) => onChange({ ...options, documentTitle: e.target.value })}
            placeholder="e.g. Product Photos - March 2026"
            disabled={disabled}
          />
        </div>

        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium">C2PA Manifest</p>
            <p className="text-xs text-muted-foreground">
              Embed Content Provenance and Authenticity manifest in each image.
            </p>
          </div>
          <Switch
            checked={options.enableC2pa}
            onCheckedChange={(v) => onChange({ ...options, enableC2pa: v })}
            disabled={disabled}
          />
        </div>

        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium">
              TrustMark Watermark
              {!isEnterprise && (
                <Badge className="ml-2 bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400">
                  Enterprise
                </Badge>
              )}
            </p>
            <p className="text-xs text-muted-foreground">
              Apply neural watermark that survives editing, cropping, and screenshots.
            </p>
          </div>
          <Switch
            checked={options.enableTrustmark}
            onCheckedChange={(v) => onChange({ ...options, enableTrustmark: v })}
            disabled={disabled || !isEnterprise}
          />
        </div>

        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium">Attribution Indexing</p>
            <p className="text-xs text-muted-foreground">
              Index image perceptual hash for AI detection and attribution.
            </p>
          </div>
          <Switch
            checked={options.indexForAttribution}
            onCheckedChange={(v) => onChange({ ...options, indexForAttribution: v })}
            disabled={disabled}
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">
            Image Quality: {options.imageQuality}%
          </label>
          <input
            type="range"
            min={50}
            max={100}
            value={options.imageQuality}
            onChange={(e) => onChange({ ...options, imageQuality: Number(e.target.value) })}
            disabled={disabled}
            className="w-full accent-blue-ncs"
          />
          <div className="flex justify-between text-xs text-muted-foreground mt-1">
            <span>Smaller file</span>
            <span>Higher quality</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function ResultCard({ result }: { result: SigningResult }) {
  const downloadImage = (img: SignedImageData) => {
    const byteChars = atob(img.signed_image_b64);
    const byteArray = new Uint8Array(byteChars.length);
    for (let i = 0; i < byteChars.length; i++) {
      byteArray[i] = byteChars.charCodeAt(i);
    }
    const blob = new Blob([byteArray], { type: img.mime_type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `signed-${img.filename}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const downloadAll = () => {
    result.images.forEach((img) => downloadImage(img));
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>Signing Complete</CardTitle>
            <CardDescription>
              {result.total_images} image{result.total_images !== 1 ? 's' : ''} signed in{' '}
              {(result.processing_time_ms / 1000).toFixed(1)}s
            </CardDescription>
          </div>
          <Button variant="primary" onClick={downloadAll}>
            <Download className="w-4 h-4 mr-2" />
            Download All
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Composite manifest summary */}
        <div className="rounded-lg border border-border p-4 space-y-2">
          <h4 className="text-sm font-semibold">Composite Manifest</h4>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span className="text-muted-foreground">Instance ID:</span>
              <p className="font-mono break-all">{result.composite_manifest.instance_id}</p>
            </div>
            <div>
              <span className="text-muted-foreground">Ingredients:</span>
              <p>{result.composite_manifest.ingredient_count}</p>
            </div>
            <div className="col-span-2">
              <span className="text-muted-foreground">Manifest Hash:</span>
              <p className="font-mono break-all">{result.composite_manifest.manifest_hash}</p>
            </div>
          </div>
        </div>

        {/* Individual images */}
        <div className="space-y-3">
          {result.images.map((img) => (
            <div
              key={img.image_id}
              className="flex items-center gap-4 rounded-lg border border-border p-3"
            >
              <div className="w-16 h-16 rounded bg-muted flex items-center justify-center shrink-0">
                <ImageIcon className="w-6 h-6 text-muted-foreground" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium truncate">{img.filename}</p>
                <div className="flex flex-wrap gap-2 mt-1">
                  {img.c2pa_signed ? (
                    <Badge className="bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      C2PA Signed
                    </Badge>
                  ) : (
                    <Badge className="bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400">
                      <XCircle className="w-3 h-3 mr-1" />
                      No C2PA
                    </Badge>
                  )}
                  {img.trustmark_applied && (
                    <Badge className="bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400">
                      Watermarked
                    </Badge>
                  )}
                  <span className="text-xs text-muted-foreground">
                    {formatBytes(img.size_bytes)}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground font-mono mt-1 truncate">
                  {img.signed_image_hash}
                </p>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => downloadImage(img)}
              >
                <Download className="w-4 h-4" />
              </Button>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function ImageSigningPageInner() {
  const { data: session } = useSession();
  const accessToken = (session?.user as any)?.accessToken as string | undefined;
  const { activeOrganization } = useOrganization();
  const isEnterprise = activeOrganization?.tier === 'enterprise';

  const [images, setImages] = useState<ImageFile[]>([]);
  const [options, setOptions] = useState<SigningOptions>({
    enableC2pa: true,
    enableTrustmark: false,
    documentTitle: '',
    imageQuality: 95,
    indexForAttribution: true,
  });
  const [result, setResult] = useState<SigningResult | null>(null);

  const addImages = useCallback(
    async (fileList: FileList) => {
      const remaining = MAX_IMAGES - images.length;

      const validFiles: { file: File; index: number }[] = [];
      for (let i = 0; i < Math.min(fileList.length, remaining); i++) {
        const file = fileList[i];
        if (!ACCEPTED_TYPES.includes(file.type)) {
          toast.error(`${file.name}: unsupported file type. Use JPEG, PNG, WebP, or TIFF.`);
          continue;
        }
        if (file.size > MAX_FILE_SIZE) {
          toast.error(`${file.name}: exceeds 10MB limit.`);
          continue;
        }
        validFiles.push({ file, index: i });
      }

      const results = await Promise.allSettled(
        validFiles.map(async ({ file, index }) => {
          const b64 = await fileToBase64(file);
          return {
            id: `${Date.now()}-${index}-${file.name}`,
            file,
            preview: URL.createObjectURL(file),
            b64,
          } as ImageFile;
        })
      );

      const newFiles: ImageFile[] = [];
      for (const result of results) {
        if (result.status === 'fulfilled') {
          newFiles.push(result.value);
        } else {
          toast.error('Failed to read a file.');
        }
      }

      if (fileList.length > remaining) {
        toast.error(`Only ${remaining} more image${remaining !== 1 ? 's' : ''} allowed (max ${MAX_IMAGES}).`);
      }

      setImages((prev) => [...prev, ...newFiles]);
    },
    [images.length]
  );

  // Clean up object URLs on unmount
  useEffect(() => {
    return () => {
      images.forEach((img) => URL.revokeObjectURL(img.preview));
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps -- cleanup only on unmount
  }, []);

  const removeImage = useCallback((id: string) => {
    setImages((prev) => {
      const removed = prev.find((img) => img.id === id);
      if (removed) URL.revokeObjectURL(removed.preview);
      return prev.filter((img) => img.id !== id);
    });
  }, []);

  const signMutation = useMutation({
    mutationFn: async () => {
      if (!accessToken) throw new Error('You must be signed in.');
      if (images.length === 0) throw new Error('Add at least one image.');

      const payload = {
        content: options.documentTitle || 'Image signing batch',
        content_format: 'plain' as const,
        document_title: options.documentTitle || undefined,
        images: images.map((img, idx) => ({
          data: img.b64,
          filename: img.file.name,
          mime_type: img.file.type,
          position: idx,
        })),
        options: {
          enable_trustmark: options.enableTrustmark,
          image_quality: options.imageQuality,
          index_for_attribution: options.indexForAttribution,
        },
      };

      return apiClient.signRichContent(accessToken, payload);
    },
    onSuccess: (data) => {
      setResult(data as unknown as SigningResult);
      toast.success('Images signed successfully.');
    },
    onError: (err: Error) => {
      toast.error(err.message || 'Signing failed.');
    },
  });

  const reset = () => {
    images.forEach((img) => URL.revokeObjectURL(img.preview));
    setImages([]);
    setResult(null);
    setOptions({
      enableC2pa: true,
      enableTrustmark: false,
      documentTitle: '',
      imageQuality: 95,
      indexForAttribution: true,
    });
  };

  const isSigning = signMutation.isPending;

  return (
    <DashboardLayout>
      <div className="mb-8">
        <div className="flex items-center gap-3">
          <ImageIcon className="w-6 h-6 text-blue-ncs" />
          <h1 className="text-2xl font-bold text-delft-blue dark:text-white">Image Signing</h1>
        </div>
        <p className="text-sm text-muted-foreground mt-1">
          Sign images with C2PA provenance manifests and optional neural watermarks.
        </p>
      </div>

      {result ? (
        <div className="space-y-6">
          <ResultCard result={result} />
          <div className="flex justify-center">
            <Button variant="outline" onClick={reset}>
              Sign More Images
            </Button>
          </div>
        </div>
      ) : (
        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Upload Images</CardTitle>
                <CardDescription>
                  Select images to sign with C2PA provenance.
                  {images.length > 0 && (
                    <span className="ml-2 font-medium">
                      {images.length}/{MAX_IMAGES} selected
                    </span>
                  )}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <DropZone
                  images={images}
                  onAdd={addImages}
                  onRemove={removeImage}
                  disabled={isSigning}
                />
              </CardContent>
            </Card>

            {/* Sign button */}
            <div className="flex gap-3">
              <Button
                variant="primary"
                onClick={() => signMutation.mutate()}
                disabled={isSigning || images.length === 0}
                className="flex-1"
              >
                {isSigning ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Signing {images.length} image{images.length !== 1 ? 's' : ''}...
                  </>
                ) : (
                  <>
                    Sign {images.length} Image{images.length !== 1 ? 's' : ''}
                  </>
                )}
              </Button>
              {images.length > 0 && !isSigning && (
                <Button variant="outline" onClick={reset}>
                  Clear
                </Button>
              )}
            </div>
          </div>

          <div className="space-y-6 order-first lg:order-last">
            <SigningOptionsCard
              options={options}
              onChange={setOptions}
              disabled={isSigning}
              isEnterprise={isEnterprise}
            />
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}

export default function ImageSigningPage() {
  return (
    <Suspense fallback={<div className="p-8 text-muted-foreground">Loading image signing...</div>}>
      <ImageSigningPageInner />
    </Suspense>
  );
}
