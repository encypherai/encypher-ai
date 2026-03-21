import Link from "next/link";
import { SECTIONS } from "@/lib/sections";

export function SectionNav() {
  return (
    <nav className="py-2 border-b border-rule-light">
      <ul className="flex items-center justify-center gap-4 sm:gap-8 flex-wrap">
        {SECTIONS.map((section) => (
          <li key={section.slug}>
            <Link
              href={`/section/${section.slug}`}
              className="section-label text-ink hover:text-blue-ncs transition-colors"
            >
              {section.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
