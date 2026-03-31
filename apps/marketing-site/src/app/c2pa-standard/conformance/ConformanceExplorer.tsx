'use client';

import React, { useState, useEffect, useMemo, useCallback } from 'react';
import {
  Search,
  ChevronDown,
  ChevronUp,
  ExternalLink,
  SlidersHorizontal,
  X,
  ShieldCheck,
  FileKey,
  Clock,
} from 'lucide-react';

// ---------------------------------------------------------------------------
// Data URLs
// ---------------------------------------------------------------------------
const PRODUCTS_URL =
  'https://raw.githubusercontent.com/c2pa-org/conformance-public/main/conforming-products/conforming-products-list.json';
const TRUST_LIST_URL =
  'https://raw.githubusercontent.com/c2pa-org/conformance-public/main/trust-list/C2PA-TRUST-LIST.pem';
const TSA_TRUST_LIST_URL =
  'https://raw.githubusercontent.com/c2pa-org/conformance-public/main/trust-list/C2PA-TSA-TRUST-LIST.pem';

const ENCYPHER_MATCH = /encypher/i;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
interface ConformanceProduct {
  recordId: string;
  applicant: string;
  status: string;
  product: {
    productType: string;
    DN: { CN: string; O: string; OU: string; C: string };
    minVersion: string;
    assurance?: {
      maxAssuranceLevel: number;
      attestationMethods?: string[];
    };
  };
  specVersion: string[];
  conformanceProgramVersion: string;
  containers: {
    generate: Record<string, string[]>;
    validate: Record<string, string[]>;
  };
  dates: {
    creation: string;
    conformance: string;
    earliestPublicDisclosure: string;
    lastModification: string;
  };
}

interface CertInfo {
  subject: Record<string, string>;
  issuer: Record<string, string>;
  validFrom: string;
  validTo: string;
  pem: string;
}

type ActiveTab = 'products' | 'trust-list' | 'tsa-trust-list';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
function formatProductType(type: string): string {
  if (type === 'generatorProduct') return 'Generator';
  if (type === 'validatorProduct') return 'Validator';
  return type;
}

function getMediaCategories(containers: ConformanceProduct['containers']): string[] {
  const cats = new Set<string>();
  for (const cat of Object.keys(containers.generate || {})) cats.add(cat);
  for (const cat of Object.keys(containers.validate || {})) cats.add(cat);
  return Array.from(cats).sort();
}

function formatCapabilities(containers: ConformanceProduct['containers']) {
  const generates: string[] = [];
  const validates: string[] = [];
  for (const mimes of Object.values(containers.generate || {})) {
    for (const m of mimes) generates.push(m);
  }
  for (const mimes of Object.values(containers.validate || {})) {
    for (const m of mimes) validates.push(m);
  }
  return { generates, validates };
}

function isEncypher(p: ConformanceProduct): boolean {
  return ENCYPHER_MATCH.test(p.applicant) || ENCYPHER_MATCH.test(p.product.DN.O);
}

// ---------------------------------------------------------------------------
// Minimal X.509 DER parser (subject/issuer DN + validity)
// ---------------------------------------------------------------------------
const OID_MAP: Record<string, string> = {
  '2.5.4.3': 'CN',
  '2.5.4.6': 'C',
  '2.5.4.10': 'O',
  '2.5.4.11': 'OU',
  '2.5.4.7': 'L',
  '2.5.4.8': 'ST',
};

function readAsn1(data: Uint8Array, offset: number) {
  if (offset >= data.length) return null;
  const tag = data[offset];
  let len = data[offset + 1];
  let hdrLen = 2;
  if (len & 0x80) {
    const n = len & 0x7f;
    len = 0;
    for (let i = 0; i < n; i++) len = (len << 8) | data[offset + 2 + i];
    hdrLen = 2 + n;
  }
  return { tag, length: len, headerLength: hdrLen, totalLength: hdrLen + len, offset };
}

function parseOid(data: Uint8Array, off: number, len: number): string {
  const parts: number[] = [];
  parts.push(Math.floor(data[off] / 40));
  parts.push(data[off] % 40);
  let val = 0;
  for (let i = 1; i < len; i++) {
    val = (val << 7) | (data[off + i] & 0x7f);
    if (!(data[off + i] & 0x80)) {
      parts.push(val);
      val = 0;
    }
  }
  return parts.join('.');
}

function parseTime(data: Uint8Array, off: number, len: number, tag: number): string {
  const s = new TextDecoder().decode(data.slice(off, off + len));
  if (tag === 0x17) {
    // UTCTime: YYMMDDHHMMSSZ
    const y = parseInt(s.slice(0, 2), 10);
    const year = y >= 50 ? 1900 + y : 2000 + y;
    return `${year}-${s.slice(2, 4)}-${s.slice(4, 6)}`;
  }
  // GeneralizedTime: YYYYMMDDHHMMSSZ
  return `${s.slice(0, 4)}-${s.slice(4, 6)}-${s.slice(6, 8)}`;
}

function parseDnFields(data: Uint8Array, start: number, end: number): Record<string, string> {
  const fields: Record<string, string> = {};
  let pos = start;
  while (pos < end) {
    const set = readAsn1(data, pos);
    if (!set || set.tag !== 0x31) break;
    let inner = pos + set.headerLength;
    const setEnd = pos + set.totalLength;
    while (inner < setEnd) {
      const seq = readAsn1(data, inner);
      if (!seq || seq.tag !== 0x30) break;
      const oid = readAsn1(data, inner + seq.headerLength);
      if (oid && oid.tag === 0x06) {
        const oidStr = parseOid(data, inner + seq.headerLength + oid.headerLength, oid.length);
        const valNode = readAsn1(data, inner + seq.headerLength + oid.totalLength);
        if (valNode) {
          const valOff = inner + seq.headerLength + oid.totalLength + valNode.headerLength;
          const val = new TextDecoder().decode(data.slice(valOff, valOff + valNode.length));
          const label = OID_MAP[oidStr] || oidStr;
          fields[label] = val;
        }
      }
      inner += seq.totalLength;
    }
    pos += set.totalLength;
  }
  return fields;
}

function parseCert(der: Uint8Array): Partial<CertInfo> {
  try {
    // Certificate SEQUENCE
    const cert = readAsn1(der, 0);
    if (!cert || cert.tag !== 0x30) return {};
    // TBSCertificate SEQUENCE
    const tbs = readAsn1(der, cert.headerLength);
    if (!tbs || tbs.tag !== 0x30) return {};
    let pos = cert.headerLength + tbs.headerLength;
    const tbsEnd = cert.headerLength + tbs.totalLength;

    // version [0] EXPLICIT (optional)
    let node = readAsn1(der, pos);
    if (node && node.tag === 0xa0) {
      pos += node.totalLength;
      node = readAsn1(der, pos);
    }
    // serialNumber INTEGER
    if (!node) return {};
    pos += node.totalLength;
    // signature AlgorithmIdentifier SEQUENCE
    node = readAsn1(der, pos);
    if (!node) return {};
    pos += node.totalLength;
    // issuer Name SEQUENCE
    const issuerNode = readAsn1(der, pos);
    if (!issuerNode) return {};
    const issuer = parseDnFields(der, pos + issuerNode.headerLength, pos + issuerNode.totalLength);
    pos += issuerNode.totalLength;
    // validity SEQUENCE
    const valSeq = readAsn1(der, pos);
    if (!valSeq || valSeq.tag !== 0x30) return { issuer, subject: {} };
    const t1 = readAsn1(der, pos + valSeq.headerLength);
    let validFrom = '';
    let validTo = '';
    if (t1) {
      validFrom = parseTime(der, pos + valSeq.headerLength + t1.headerLength, t1.length, t1.tag);
      const t2 = readAsn1(der, pos + valSeq.headerLength + t1.totalLength);
      if (t2) {
        validTo = parseTime(
          der,
          pos + valSeq.headerLength + t1.totalLength + t2.headerLength,
          t2.length,
          t2.tag
        );
      }
    }
    pos += valSeq.totalLength;
    // subject Name SEQUENCE
    if (pos >= tbsEnd) return { issuer, validFrom, validTo, subject: {} };
    const subjectNode = readAsn1(der, pos);
    if (!subjectNode) return { issuer, validFrom, validTo, subject: {} };
    const subject = parseDnFields(
      der,
      pos + subjectNode.headerLength,
      pos + subjectNode.totalLength
    );
    return { subject, issuer, validFrom, validTo };
  } catch {
    return {};
  }
}

function parsePemCerts(pem: string): CertInfo[] {
  const certs: CertInfo[] = [];
  const re = /-----BEGIN CERTIFICATE-----\s*([\s\S]*?)\s*-----END CERTIFICATE-----/g;
  let match;
  while ((match = re.exec(pem)) !== null) {
    const b64 = match[1].replace(/\s/g, '');
    const bin = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
    const parsed = parseCert(bin);
    certs.push({
      subject: parsed.subject || {},
      issuer: parsed.issuer || {},
      validFrom: parsed.validFrom || '',
      validTo: parsed.validTo || '',
      pem: match[0],
    });
  }
  return certs;
}

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

const MEDIA_CATEGORIES = ['image', 'video', 'audio', 'document', 'font', 'ml_model'] as const;
const MEDIA_LABELS: Record<string, string> = {
  image: 'Image',
  video: 'Video',
  audio: 'Audio',
  document: 'Documents',
  font: 'Fonts',
  ml_model: 'ML Model',
};

const MEDIA_COLORS: Record<string, string> = {
  image: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
  video: 'bg-rose-100 text-rose-800 dark:bg-rose-900/30 dark:text-rose-300',
  audio: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300',
  document: 'bg-sky-100 text-sky-800 dark:bg-sky-900/30 dark:text-sky-300',
  font: 'bg-teal-100 text-teal-800 dark:bg-teal-900/30 dark:text-teal-300',
  ml_model: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300',
};

function MediaMultiSelect({
  selected,
  onToggle,
}: {
  selected: Set<string>;
  onToggle: (cat: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = React.useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-3 py-2 border border-border rounded-md bg-background text-sm cursor-pointer focus:outline-none focus:ring-2 focus:ring-[#2a87c4]/50"
      >
        <span className={selected.size === 0 ? 'text-muted-foreground' : 'text-foreground'}>
          {selected.size === 0
            ? 'All Media Types'
            : `${selected.size} selected`}
        </span>
        <ChevronDown className={`h-4 w-4 text-muted-foreground transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      {selected.size > 0 && (
        <div className="flex flex-wrap gap-1 mt-1.5">
          {MEDIA_CATEGORIES.filter((c) => selected.has(c)).map((cat) => (
            <button
              key={cat}
              onClick={() => onToggle(cat)}
              className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded-full font-medium ${MEDIA_COLORS[cat] || 'bg-muted text-muted-foreground'}`}
            >
              {MEDIA_LABELS[cat]}
              <X className="h-3 w-3" />
            </button>
          ))}
        </div>
      )}
      {open && (
        <div className="absolute z-20 mt-1 w-full bg-background border border-border rounded-md shadow-lg py-1">
          {MEDIA_CATEGORIES.map((cat) => (
            <label
              key={cat}
              className="flex items-center gap-2.5 px-3 py-2 text-sm cursor-pointer hover:bg-muted/50 transition-colors"
            >
              <input
                type="checkbox"
                checked={selected.has(cat)}
                onChange={() => onToggle(cat)}
                className="rounded border-border accent-[#2a87c4]"
              />
              <span className={`inline-block w-2 h-2 rounded-full ${MEDIA_COLORS[cat]?.split(' ')[0] || 'bg-muted'}`} />
              {MEDIA_LABELS[cat] || cat}
            </label>
          ))}
        </div>
      )}
    </div>
  );
}

function MimeTag({ mime }: { mime: string }) {
  const short = mime.replace(/^(image|audio|video|application|font)\//, '');
  return (
    <span className="inline-block px-1.5 py-0.5 text-xs bg-muted rounded font-mono">
      {short}
    </span>
  );
}

function ProductRow({
  product,
  highlight,
}: {
  product: ConformanceProduct;
  highlight: boolean;
}) {
  const [expanded, setExpanded] = useState(false);
  const { generates, validates } = formatCapabilities(product.containers);

  return (
    <>
      <tr
        className={`border-b border-border cursor-pointer transition-colors ${
          highlight
            ? 'bg-[#2a87c4]/5 hover:bg-[#2a87c4]/10'
            : 'hover:bg-muted/30'
        }`}
        onClick={() => setExpanded(!expanded)}
      >
        <td className="py-3 px-4">
          <div className="flex items-center gap-2">
            <span className="font-medium">{product.product.DN.CN}</span>
            {highlight && (
              <span className="px-1.5 py-0.5 text-[10px] font-bold rounded bg-[#2a87c4] text-white uppercase tracking-wider">
                Encypher
              </span>
            )}
          </div>
          <div className="text-sm text-muted-foreground">{product.applicant}</div>
        </td>
        <td className="py-3 px-4">
          <span
            className={`inline-block px-2 py-0.5 text-xs rounded-full font-medium ${
              product.product.productType === 'generatorProduct'
                ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                : 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
            }`}
          >
            {formatProductType(product.product.productType)}
          </span>
        </td>
        <td className="py-3 px-4">
          <div className="flex flex-wrap gap-1">
            {getMediaCategories(product.containers).map((cat) => (
              <span
                key={cat}
                className={`inline-block px-2 py-0.5 text-xs rounded capitalize font-medium ${
                  MEDIA_COLORS[cat] || 'bg-muted text-muted-foreground'
                }`}
              >
                {cat}
              </span>
            ))}
          </div>
        </td>
        <td className="py-3 px-4 text-sm">{product.specVersion.join(', ')}</td>
        <td className="py-3 px-4 text-sm text-muted-foreground">
          {product.dates.conformance}
        </td>
        <td className="py-3 px-4">
          <div className="p-1 rounded hover:bg-muted/50 transition-colors inline-flex">
            {expanded ? (
              <ChevronUp className="h-4 w-4 text-muted-foreground" />
            ) : (
              <ChevronDown className="h-4 w-4 text-muted-foreground" />
            )}
          </div>
        </td>
      </tr>
      {expanded && (
        <tr
          className={`border-b border-border ${
            highlight ? 'bg-[#2a87c4]/5' : 'bg-muted/20'
          }`}
        >
          <td colSpan={6} className="py-4 px-4">
            <div className="grid md:grid-cols-2 gap-6 text-sm">
              <div>
                <h4 className="font-medium mb-2">Product Details</h4>
                <dl className="space-y-1">
                  <div className="flex gap-2">
                    <dt className="text-muted-foreground w-32 flex-shrink-0">Organization</dt>
                    <dd>{product.product.DN.O}</dd>
                  </div>
                  {product.product.DN.OU && (
                    <div className="flex gap-2">
                      <dt className="text-muted-foreground w-32 flex-shrink-0">Unit</dt>
                      <dd>{product.product.DN.OU}</dd>
                    </div>
                  )}
                  <div className="flex gap-2">
                    <dt className="text-muted-foreground w-32 flex-shrink-0">Country</dt>
                    <dd>{product.product.DN.C}</dd>
                  </div>
                  <div className="flex gap-2">
                    <dt className="text-muted-foreground w-32 flex-shrink-0">Min Version</dt>
                    <dd className="font-mono">{product.product.minVersion}</dd>
                  </div>
                  {product.product.assurance && (
                    <>
                      <div className="flex gap-2">
                        <dt className="text-muted-foreground w-32 flex-shrink-0">Assurance Level</dt>
                        <dd>Level {product.product.assurance.maxAssuranceLevel}</dd>
                      </div>
                      {product.product.assurance.attestationMethods &&
                        product.product.assurance.attestationMethods.length > 0 && (
                          <div className="flex gap-2">
                            <dt className="text-muted-foreground w-32 flex-shrink-0">Attestation</dt>
                            <dd>{product.product.assurance.attestationMethods.join(', ')}</dd>
                          </div>
                        )}
                    </>
                  )}
                  <div className="flex gap-2">
                    <dt className="text-muted-foreground w-32 flex-shrink-0">Status</dt>
                    <dd className="capitalize">{product.status}</dd>
                  </div>
                </dl>
              </div>
              <div>
                <h4 className="font-medium mb-2">Supported Formats</h4>
                {generates.length > 0 && (
                  <div className="mb-3">
                    <div className="text-muted-foreground text-xs uppercase tracking-wider mb-1">
                      Generates
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {generates.map((m) => (
                        <MimeTag key={`gen-${m}`} mime={m} />
                      ))}
                    </div>
                  </div>
                )}
                {validates.length > 0 && (
                  <div>
                    <div className="text-muted-foreground text-xs uppercase tracking-wider mb-1">
                      Validates
                    </div>
                    <div className="flex flex-wrap gap-1">
                      {validates.map((m) => (
                        <MimeTag key={`val-${m}`} mime={m} />
                      ))}
                    </div>
                  </div>
                )}
                <div className="mt-3">
                  <div className="text-muted-foreground text-xs uppercase tracking-wider mb-1">Dates</div>
                  <div className="text-xs space-y-0.5">
                    <div>Conformance: {product.dates.conformance}</div>
                    <div>Created: {product.dates.creation}</div>
                    <div>Last Modified: {product.dates.lastModification}</div>
                  </div>
                </div>
              </div>
            </div>
          </td>
        </tr>
      )}
    </>
  );
}

function CertificateList({
  url,
  description,
}: {
  url: string;
  description: string;
}) {
  const [certs, setCerts] = useState<CertInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedIdx, setExpandedIdx] = useState<number | null>(null);

  useEffect(() => {
    fetch(url)
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.text();
      })
      .then((pem) => {
        setCerts(parsePemCerts(pem));
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, [url]);

  if (loading) {
    return <div className="py-12 text-center text-muted-foreground">Loading certificates...</div>;
  }
  if (error) {
    return (
      <div className="py-8 text-muted-foreground">
        Unable to load the trust list.{' '}
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-[#2a87c4] hover:underline"
        >
          View raw PEM file
        </a>
      </div>
    );
  }

  return (
    <div>
      <p className="text-muted-foreground mb-6">{description}</p>
      <div className="text-sm text-muted-foreground mb-3">
        {certs.length} certificate{certs.length !== 1 ? 's' : ''}
      </div>
      <div className="border border-border rounded-lg overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border bg-muted/30">
              <th className="text-left py-3 px-4 font-medium">Subject</th>
              <th className="text-left py-3 px-4 font-medium">Issuer</th>
              <th className="text-left py-3 px-4 font-medium">Valid From</th>
              <th className="text-left py-3 px-4 font-medium">Valid To</th>
              <th className="py-3 px-4 w-10"></th>
            </tr>
          </thead>
          <tbody>
            {certs.map((cert, idx) => {
              const isExpanded = expandedIdx === idx;
              const subjectLabel = cert.subject.CN || cert.subject.O || `Certificate ${idx + 1}`;
              const isEnc =
                ENCYPHER_MATCH.test(subjectLabel) ||
                ENCYPHER_MATCH.test(cert.subject.O || '');
              return (
                <React.Fragment key={idx}>
                  <tr
                    className={`border-b border-border cursor-pointer transition-colors ${
                      isEnc ? 'bg-[#2a87c4]/5 hover:bg-[#2a87c4]/10' : 'hover:bg-muted/30'
                    }`}
                    onClick={() => setExpandedIdx(isExpanded ? null : idx)}
                  >
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{subjectLabel}</span>
                        {isEnc && (
                          <span className="px-1.5 py-0.5 text-[10px] font-bold rounded bg-[#2a87c4] text-white uppercase tracking-wider">
                            Encypher
                          </span>
                        )}
                      </div>
                      {cert.subject.O && cert.subject.O !== subjectLabel && (
                        <div className="text-sm text-muted-foreground">{cert.subject.O}</div>
                      )}
                    </td>
                    <td className="py-3 px-4 text-sm">
                      {cert.issuer.CN || cert.issuer.O || '-'}
                    </td>
                    <td className="py-3 px-4 text-sm text-muted-foreground">
                      {cert.validFrom || '-'}
                    </td>
                    <td className="py-3 px-4 text-sm text-muted-foreground">
                      {cert.validTo || '-'}
                    </td>
                    <td className="py-3 px-4">
                      {isExpanded ? (
                        <ChevronUp className="h-4 w-4 text-muted-foreground" />
                      ) : (
                        <ChevronDown className="h-4 w-4 text-muted-foreground" />
                      )}
                    </td>
                  </tr>
                  {isExpanded && (
                    <tr className="border-b border-border bg-muted/20">
                      <td colSpan={5} className="py-4 px-4">
                        <div className="grid md:grid-cols-2 gap-6 text-sm mb-4">
                          <div>
                            <h4 className="font-medium mb-2">Subject</h4>
                            <dl className="space-y-1">
                              {Object.entries(cert.subject).map(([k, v]) => (
                                <div key={k} className="flex gap-2">
                                  <dt className="text-muted-foreground w-12 flex-shrink-0 font-mono">
                                    {k}
                                  </dt>
                                  <dd>{v}</dd>
                                </div>
                              ))}
                            </dl>
                          </div>
                          <div>
                            <h4 className="font-medium mb-2">Issuer</h4>
                            <dl className="space-y-1">
                              {Object.entries(cert.issuer).map(([k, v]) => (
                                <div key={k} className="flex gap-2">
                                  <dt className="text-muted-foreground w-12 flex-shrink-0 font-mono">
                                    {k}
                                  </dt>
                                  <dd>{v}</dd>
                                </div>
                              ))}
                            </dl>
                          </div>
                        </div>
                        <details className="text-xs">
                          <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
                            PEM Certificate
                          </summary>
                          <pre className="mt-2 p-3 bg-muted rounded overflow-x-auto font-mono whitespace-pre-wrap break-all">
                            {cert.pem}
                          </pre>
                        </details>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
      <div className="mt-4 text-sm text-muted-foreground">
        Source:{' '}
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-[#2a87c4] hover:underline inline-flex items-center gap-0.5"
        >
          View raw PEM <ExternalLink className="h-3 w-3" />
        </a>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

type SortField = 'product' | 'type' | 'date';
type SortDir = 'asc' | 'desc';

export function ConformanceExplorer() {
  const [activeTab, setActiveTab] = useState<ActiveTab>('products');
  const [products, setProducts] = useState<ConformanceProduct[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filters
  const [search, setSearch] = useState('');
  const [vendorFilter, setVendorFilter] = useState('all');
  const [typeFilter, setTypeFilter] = useState('all');
  const [assuranceFilter, setAssuranceFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [mediaFilters, setMediaFilters] = useState<Set<string>>(new Set());
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Sort
  const [sortField, setSortField] = useState<SortField>('product');
  const [sortDir, setSortDir] = useState<SortDir>('asc');

  useEffect(() => {
    fetch(PRODUCTS_URL)
      .then((r) => {
        if (!r.ok) throw new Error(`Failed to fetch: ${r.status}`);
        return r.json();
      })
      .then((data: ConformanceProduct[]) => {
        setProducts(data);
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, []);

  // Derived filter options from data
  const vendorOptions = useMemo(() => {
    const set = new Set(products.map((p) => p.applicant));
    return Array.from(set).sort();
  }, [products]);

  const assuranceLevels = useMemo(() => {
    const set = new Set<number>();
    for (const p of products) {
      if (p.product.assurance) set.add(p.product.assurance.maxAssuranceLevel);
    }
    return Array.from(set).sort();
  }, [products]);

  const statusOptions = useMemo(() => {
    const set = new Set(products.map((p) => p.status));
    return Array.from(set).sort();
  }, [products]);

  const toggleMedia = useCallback((cat: string) => {
    setMediaFilters((prev) => {
      const next = new Set(prev);
      if (next.has(cat)) next.delete(cat);
      else next.add(cat);
      return next;
    });
  }, []);

  const hasActiveFilters =
    search !== '' ||
    vendorFilter !== 'all' ||
    typeFilter !== 'all' ||
    assuranceFilter !== 'all' ||
    statusFilter !== 'all' ||
    mediaFilters.size > 0;

  const resetFilters = useCallback(() => {
    setSearch('');
    setVendorFilter('all');
    setTypeFilter('all');
    setAssuranceFilter('all');
    setStatusFilter('all');
    setMediaFilters(new Set());
  }, []);

  const filtered = useMemo(() => {
    let result = products;

    if (search) {
      const q = search.toLowerCase();
      result = result.filter(
        (p) =>
          p.applicant.toLowerCase().includes(q) ||
          p.product.DN.CN.toLowerCase().includes(q) ||
          (p.product.DN.OU && p.product.DN.OU.toLowerCase().includes(q))
      );
    }
    if (vendorFilter !== 'all') {
      result = result.filter((p) => p.applicant === vendorFilter);
    }
    if (typeFilter !== 'all') {
      result = result.filter((p) => p.product.productType === typeFilter);
    }
    if (assuranceFilter !== 'all') {
      const lvl = parseInt(assuranceFilter, 10);
      result = result.filter(
        (p) => p.product.assurance && p.product.assurance.maxAssuranceLevel === lvl
      );
    }
    if (statusFilter !== 'all') {
      result = result.filter((p) => p.status === statusFilter);
    }
    if (mediaFilters.size > 0) {
      result = result.filter((p) => {
        const cats = getMediaCategories(p.containers);
        return Array.from(mediaFilters).some((f) => cats.includes(f));
      });
    }

    // Sort, but pin Encypher products to top
    result = [...result].sort((a, b) => {
      const aEnc = isEncypher(a);
      const bEnc = isEncypher(b);
      if (aEnc && !bEnc) return -1;
      if (!aEnc && bEnc) return 1;
      let cmp = 0;
      if (sortField === 'product') cmp = a.product.DN.CN.localeCompare(b.product.DN.CN);
      else if (sortField === 'type') cmp = a.product.productType.localeCompare(b.product.productType);
      else if (sortField === 'date') cmp = a.dates.conformance.localeCompare(b.dates.conformance);
      return sortDir === 'asc' ? cmp : -cmp;
    });

    return result;
  }, [products, search, vendorFilter, typeFilter, assuranceFilter, statusFilter, mediaFilters, sortField, sortDir]);

  function toggleSort(field: SortField) {
    if (sortField === field) setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    else {
      setSortField(field);
      setSortDir('asc');
    }
  }

  const generatorCount = products.filter((p) => p.product.productType === 'generatorProduct').length;
  const validatorCount = products.filter((p) => p.product.productType === 'validatorProduct').length;
  const uniqueApplicants = new Set(products.map((p) => p.applicant)).size;

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  const tabs: { id: ActiveTab; label: string; icon: React.ReactNode }[] = [
    { id: 'products', label: 'Conforming Products', icon: <ShieldCheck className="h-4 w-4" /> },
    { id: 'trust-list', label: 'Trust List', icon: <FileKey className="h-4 w-4" /> },
    { id: 'tsa-trust-list', label: 'TSA Trust List', icon: <Clock className="h-4 w-4" /> },
  ];

  return (
    <div>
      {/* Tab bar */}
      <div className="flex gap-1 mb-8 border-b border-border overflow-x-auto">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
              activeTab === tab.id
                ? 'border-[#2a87c4] text-foreground'
                : 'border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Products tab */}
      {activeTab === 'products' && (
        <>
          {loading ? (
            <div className="flex items-center justify-center py-16">
              <div className="text-muted-foreground">Loading conformance data...</div>
            </div>
          ) : error ? (
            <div className="py-8">
              <p className="text-muted-foreground mb-4">
                Unable to load the conformance list. View the official list at:
              </p>
              <a
                href="https://spec.c2pa.org/conformance-explorer/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-[#2a87c4] hover:underline inline-flex items-center gap-1"
              >
                C2PA Conformance Explorer <ExternalLink className="h-4 w-4" />
              </a>
            </div>
          ) : (
            <>
              {/* Stats */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-8">
                <div className="bg-muted/50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold">{products.length}</div>
                  <div className="text-sm text-muted-foreground">Conformant Products</div>
                </div>
                <div className="bg-muted/50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold">{uniqueApplicants}</div>
                  <div className="text-sm text-muted-foreground">Organizations</div>
                </div>
                <div className="bg-muted/50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold">{generatorCount}</div>
                  <div className="text-sm text-muted-foreground">Generators</div>
                </div>
                <div className="bg-muted/50 rounded-lg p-4 text-center">
                  <div className="text-2xl font-bold">{validatorCount}</div>
                  <div className="text-sm text-muted-foreground">Validators</div>
                </div>
              </div>

              {/* Search + Advanced Filters toggle */}
              <div className="flex flex-col sm:flex-row gap-3 mb-3">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Search anything..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="w-full pl-9 pr-4 py-2 border border-border rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-[#2a87c4]/50"
                  />
                </div>
                <button
                  onClick={() => setShowAdvanced(!showAdvanced)}
                  className={`flex items-center gap-2 px-4 py-2 border rounded-md text-sm font-medium transition-colors ${
                    showAdvanced || hasActiveFilters
                      ? 'border-[#2a87c4] text-[#2a87c4] bg-[#2a87c4]/5'
                      : 'border-border text-muted-foreground hover:text-foreground'
                  }`}
                >
                  <SlidersHorizontal className="h-4 w-4" />
                  Advanced Filters
                  {hasActiveFilters && (
                    <span className="ml-1 px-1.5 py-0.5 text-[10px] rounded-full bg-[#2a87c4] text-white">
                      {
                        [
                          vendorFilter !== 'all',
                          typeFilter !== 'all',
                          assuranceFilter !== 'all',
                          statusFilter !== 'all',
                          mediaFilters.size > 0,
                        ].filter(Boolean).length
                      }
                    </span>
                  )}
                </button>
              </div>

              {/* Advanced filters panel */}
              {showAdvanced && (
                <div className="mb-6 p-5 border border-border rounded-lg bg-muted/10 shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-sm font-medium">Filters</span>
                    {hasActiveFilters && (
                      <button
                        onClick={resetFilters}
                        className="flex items-center gap-1.5 text-xs text-[#2a87c4] hover:text-[#2a87c4]/80 font-medium transition-colors"
                      >
                        <X className="h-3 w-3" />
                        Clear all
                      </button>
                    )}
                  </div>
                  <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4">
                    {/* Vendor */}
                    <div>
                      <label className="block text-xs font-medium text-muted-foreground mb-1">
                        Vendor
                      </label>
                      <select
                        value={vendorFilter}
                        onChange={(e) => setVendorFilter(e.target.value)}
                        className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-[#2a87c4]/50"
                      >
                        <option value="all">All Vendors</option>
                        {vendorOptions.map((v) => (
                          <option key={v} value={v}>
                            {v}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Product Type */}
                    <div>
                      <label className="block text-xs font-medium text-muted-foreground mb-1">
                        Product Type
                      </label>
                      <select
                        value={typeFilter}
                        onChange={(e) => setTypeFilter(e.target.value)}
                        className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-[#2a87c4]/50"
                      >
                        <option value="all">All Types</option>
                        <option value="generatorProduct">Generators</option>
                        <option value="validatorProduct">Validators</option>
                      </select>
                    </div>

                    {/* Assurance Level */}
                    <div>
                      <label className="block text-xs font-medium text-muted-foreground mb-1">
                        Assurance Level
                      </label>
                      <select
                        value={assuranceFilter}
                        onChange={(e) => setAssuranceFilter(e.target.value)}
                        className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-[#2a87c4]/50"
                      >
                        <option value="all">All Levels</option>
                        {assuranceLevels.map((lvl) => (
                          <option key={lvl} value={String(lvl)}>
                            Level {lvl}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Status */}
                    <div>
                      <label className="block text-xs font-medium text-muted-foreground mb-1">
                        Status
                      </label>
                      <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                        className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-[#2a87c4]/50"
                      >
                        <option value="all">All Statuses</option>
                        {statusOptions.map((s) => (
                          <option key={s} value={s} className="capitalize">
                            {s.charAt(0).toUpperCase() + s.slice(1)}
                          </option>
                        ))}
                      </select>
                    </div>

                    {/* Media Types multi-select */}
                    <div>
                      <label className="block text-xs font-medium text-muted-foreground mb-1">
                        Media Types
                      </label>
                      <MediaMultiSelect selected={mediaFilters} onToggle={toggleMedia} />
                    </div>
                  </div>
                </div>
              )}

              {/* Results count */}
              <div className="text-sm text-muted-foreground mb-3">
                {filtered.length} of {products.length} products
              </div>

              {/* Table */}
              <div className="overflow-x-auto border border-border rounded-lg">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-border bg-muted/30">
                      <th
                        className="text-left py-3 px-4 font-medium cursor-pointer hover:text-foreground transition-colors"
                        onClick={() => toggleSort('product')}
                      >
                        Product{' '}
                        {sortField === 'product' && (sortDir === 'asc' ? '\u25B2' : '\u25BC')}
                      </th>
                      <th
                        className="text-left py-3 px-4 font-medium cursor-pointer hover:text-foreground transition-colors"
                        onClick={() => toggleSort('type')}
                      >
                        Type{' '}
                        {sortField === 'type' && (sortDir === 'asc' ? '\u25B2' : '\u25BC')}
                      </th>
                      <th className="text-left py-3 px-4 font-medium">Media</th>
                      <th className="text-left py-3 px-4 font-medium">Spec</th>
                      <th
                        className="text-left py-3 px-4 font-medium cursor-pointer hover:text-foreground transition-colors"
                        onClick={() => toggleSort('date')}
                      >
                        Conformance{' '}
                        {sortField === 'date' && (sortDir === 'asc' ? '\u25B2' : '\u25BC')}
                      </th>
                      <th className="py-3 px-4 w-10"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {filtered.map((p) => (
                      <ProductRow
                        key={p.recordId}
                        product={p}
                        highlight={isEncypher(p)}
                      />
                    ))}
                  </tbody>
                </table>
              </div>

              {filtered.length === 0 && (
                <div className="text-center py-8 text-muted-foreground">
                  No products match your filters.
                </div>
              )}

              {/* Source attribution */}
              <div className="mt-6 text-sm text-muted-foreground">
                Data sourced live from the{' '}
                <a
                  href="https://spec.c2pa.org/conformance-explorer/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[#2a87c4] hover:underline inline-flex items-center gap-0.5"
                >
                  C2PA Conformance Explorer
                  <ExternalLink className="h-3 w-3" />
                </a>
                . Updated as new products complete conformance testing.
              </div>
            </>
          )}
        </>
      )}

      {/* Trust List tab */}
      {activeTab === 'trust-list' && (
        <CertificateList
          url={TRUST_LIST_URL}
          description="The C2PA Trust List contains the root and intermediate certificates used to validate C2PA manifest signatures. A manifest signed by a certificate that chains to one of these roots is considered trustworthy by conformant validators."
        />
      )}

      {/* TSA Trust List tab */}
      {activeTab === 'tsa-trust-list' && (
        <CertificateList
          url={TSA_TRUST_LIST_URL}
          description="The C2PA TSA (Time Stamp Authority) Trust List contains the certificates of trusted time-stamping services. These TSAs provide RFC 3161 timestamps that prove when a C2PA manifest was created, independent of the signer's clock."
        />
      )}
    </div>
  );
}

export default ConformanceExplorer;
