'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { Search, Filter, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';

const DATA_URL =
  'https://raw.githubusercontent.com/c2pa-org/conformance-public/main/conforming-products/conforming-products-list.json';

interface ConformanceProduct {
  recordId: string;
  applicant: string;
  status: string;
  product: {
    productType: string;
    DN: {
      CN: string;
      O: string;
      OU: string;
      C: string;
    };
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

function formatProductType(type: string): string {
  if (type === 'generatorProduct') return 'Generator';
  if (type === 'validatorProduct') return 'Validator';
  return type;
}

function getAllMimeTypes(containers: ConformanceProduct['containers']): string[] {
  const mimes = new Set<string>();
  for (const category of Object.values(containers.generate || {})) {
    for (const mime of category) mimes.add(mime);
  }
  for (const category of Object.values(containers.validate || {})) {
    for (const mime of category) mimes.add(mime);
  }
  return Array.from(mimes).sort();
}

function getMediaCategories(containers: ConformanceProduct['containers']): string[] {
  const cats = new Set<string>();
  for (const cat of Object.keys(containers.generate || {})) cats.add(cat);
  for (const cat of Object.keys(containers.validate || {})) cats.add(cat);
  return Array.from(cats).sort();
}

function formatCapabilities(containers: ConformanceProduct['containers']): {
  generates: string[];
  validates: string[];
} {
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

function MimeTag({ mime }: { mime: string }) {
  const short = mime.replace(/^(image|audio|video|application|font)\//, '');
  return (
    <span className="inline-block px-1.5 py-0.5 text-xs bg-muted rounded font-mono">
      {short}
    </span>
  );
}

function ProductRow({ product }: { product: ConformanceProduct }) {
  const [expanded, setExpanded] = useState(false);
  const { generates, validates } = formatCapabilities(product.containers);

  return (
    <>
      <tr
        className="border-b border-border hover:bg-muted/30 cursor-pointer transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <td className="py-3 px-4">
          <div className="font-medium">{product.product.DN.CN}</div>
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
                className="inline-block px-2 py-0.5 text-xs bg-muted rounded capitalize"
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
          {expanded ? (
            <ChevronUp className="h-4 w-4 text-muted-foreground" />
          ) : (
            <ChevronDown className="h-4 w-4 text-muted-foreground" />
          )}
        </td>
      </tr>
      {expanded && (
        <tr className="border-b border-border bg-muted/20">
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
                        <dt className="text-muted-foreground w-32 flex-shrink-0">
                          Assurance Level
                        </dt>
                        <dd>Level {product.product.assurance.maxAssuranceLevel}</dd>
                      </div>
                      {product.product.assurance.attestationMethods &&
                        product.product.assurance.attestationMethods.length > 0 && (
                          <div className="flex gap-2">
                            <dt className="text-muted-foreground w-32 flex-shrink-0">
                              Attestation
                            </dt>
                            <dd>
                              {product.product.assurance.attestationMethods.join(', ')}
                            </dd>
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
                  <div className="text-muted-foreground text-xs uppercase tracking-wider mb-1">
                    Dates
                  </div>
                  <div className="text-xs space-y-0.5">
                    <div>
                      Conformance: {product.dates.conformance}
                    </div>
                    <div>
                      Created: {product.dates.creation}
                    </div>
                    <div>
                      Last Modified: {product.dates.lastModification}
                    </div>
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

type SortField = 'product' | 'type' | 'date';
type SortDir = 'asc' | 'desc';

export function ConformanceExplorer() {
  const [products, setProducts] = useState<ConformanceProduct[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [sortField, setSortField] = useState<SortField>('product');
  const [sortDir, setSortDir] = useState<SortDir>('asc');

  useEffect(() => {
    fetch(DATA_URL)
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to fetch: ${res.status}`);
        return res.json();
      })
      .then((data: ConformanceProduct[]) => {
        setProducts(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const allCategories = useMemo(() => {
    const cats = new Set<string>();
    for (const p of products) {
      for (const c of getMediaCategories(p.containers)) cats.add(c);
    }
    return Array.from(cats).sort();
  }, [products]);

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

    if (typeFilter !== 'all') {
      result = result.filter((p) => p.product.productType === typeFilter);
    }

    if (categoryFilter !== 'all') {
      result = result.filter((p) =>
        getMediaCategories(p.containers).includes(categoryFilter)
      );
    }

    result = [...result].sort((a, b) => {
      let cmp = 0;
      if (sortField === 'product') {
        cmp = a.product.DN.CN.localeCompare(b.product.DN.CN);
      } else if (sortField === 'type') {
        cmp = a.product.productType.localeCompare(b.product.productType);
      } else if (sortField === 'date') {
        cmp = a.dates.conformance.localeCompare(b.dates.conformance);
      }
      return sortDir === 'asc' ? cmp : -cmp;
    });

    return result;
  }, [products, search, typeFilter, categoryFilter, sortField, sortDir]);

  function toggleSort(field: SortField) {
    if (sortField === field) {
      setSortDir(sortDir === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDir('asc');
    }
  }

  const generatorCount = products.filter(
    (p) => p.product.productType === 'generatorProduct'
  ).length;
  const validatorCount = products.filter(
    (p) => p.product.productType === 'validatorProduct'
  ).length;
  const uniqueApplicants = new Set(products.map((p) => p.applicant)).size;

  if (loading) {
    return (
      <div className="flex items-center justify-center py-16">
        <div className="text-muted-foreground">Loading conformance data...</div>
      </div>
    );
  }

  if (error) {
    return (
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
    );
  }

  return (
    <div>
      {/* Stats bar */}
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

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search by company or product name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 border border-border rounded-md bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-[#2a87c4]/50"
          />
        </div>
        <div className="flex gap-3">
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="pl-9 pr-8 py-2 border border-border rounded-md bg-background text-foreground appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-[#2a87c4]/50"
            >
              <option value="all">All Types</option>
              <option value="generatorProduct">Generators</option>
              <option value="validatorProduct">Validators</option>
            </select>
          </div>
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="px-3 py-2 border border-border rounded-md bg-background text-foreground appearance-none cursor-pointer focus:outline-none focus:ring-2 focus:ring-[#2a87c4]/50"
          >
            <option value="all">All Media</option>
            {allCategories.map((cat) => (
              <option key={cat} value={cat} className="capitalize">
                {cat.charAt(0).toUpperCase() + cat.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

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
                Conformance Date{' '}
                {sortField === 'date' && (sortDir === 'asc' ? '\u25B2' : '\u25BC')}
              </th>
              <th className="py-3 px-4 w-10"></th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((p) => (
              <ProductRow key={p.recordId} product={p} />
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
        <p>
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
          . The conformance list is maintained by the C2PA standards body and updated as
          new products complete conformance testing.
        </p>
      </div>
    </div>
  );
}

export default ConformanceExplorer;
