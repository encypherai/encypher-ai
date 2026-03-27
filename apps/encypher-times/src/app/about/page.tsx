import type { Metadata } from "next";
import Link from "next/link";
import { EncypherMark } from "@encypher/icons";

export const metadata: Metadata = {
  title: "About -- The Encypher Times",
  description:
    "About The Encypher Times -- a demonstration of enterprise content provenance technology built on the C2PA open standard.",
};

export default function AboutPage() {
  return (
    <div className="py-8 max-w-[680px] mx-auto">
      <h1 className="font-[family-name:var(--font-headline)] text-3xl sm:text-4xl font-black text-ink mb-6">
        About The Encypher Times
      </h1>

      <div className="article-prose">
        <p>
          The Encypher Times demonstrates content provenance infrastructure
          built on the C2PA open standard -- the same specification adopted by
          Adobe, Microsoft, Google, and the BBC for authenticating digital
          content.
        </p>

        <p>
          Encypher&apos;s founder authored Section A.7 of the C2PA 2.3 text
          authentication specification, published January 8, 2026, and
          co-chairs the Text Provenance Task Force alongside Google, OpenAI,
          and the BBC. This site shows what that standard looks like when
          deployed across an entire news publication.
        </p>

        <p>
          Every article, image, audio clip, and video on this site has been
          cryptographically signed using Encypher&apos;s enterprise content
          provenance infrastructure. The publication is fictional. The bylines
          are fictional. The signatures are real.
        </p>

        <h2>What You Can Do Here</h2>

        <p>
          <strong>See what signed content looks like at publication scale.</strong>{" "}
          Browse eight articles across five sections. Every article carries
          invisible, tamper-proof signatures at the sentence level -- proof of
          origin that travels with the content, detectable at the point of
          ingestion into any system.
        </p>

        <p>
          <strong>Verify any sentence&apos;s origin and integrity.</strong>{" "}
          Select any sentence or paragraph from any article, copy it, and paste
          it into the{" "}
          <Link href="/verify" className="text-blue-ncs hover:underline">
            verification tool
          </Link>
          . Encypher will confirm who published it, when it was signed, and
          whether a single character has been changed.
        </p>

        <p>
          <strong>Test tamper detection.</strong> Copy a paragraph, modify even
          one word, and re-verify. The signature will fail -- proving the
          content was altered after publication. This is the capability that
          eliminates the &quot;we didn&apos;t know&quot; defense.
        </p>

        <p>
          <strong>Check image, audio, and video provenance.</strong> Media
          files on this site carry C2PA manifests embedded in the file
          metadata. Download any image and inspect it with{" "}
          <a
            href="https://opensource.contentauthenticity.org/docs/c2patool"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-ncs hover:underline"
          >
            c2patool
          </a>{" "}
          to see the full provenance manifest.
        </p>

        <h2>Automatic Verification with Encypher Verify</h2>

        <p>
          Install the{" "}
          <a
            href="https://encypher.com"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 text-blue-ncs hover:underline"
          >
            <EncypherMark className="w-3.5 h-3.5 inline-block" color="azure" />
            Encypher Verify
          </a>{" "}
          Chrome extension to see proof-of-origin badges appear automatically
          next to every signed article as you browse. No copy-paste required --
          the extension detects Encypher signatures in real time and displays
          verification status, publisher identity, and signing date inline on
          the page.
        </p>

        <h2>The Technology</h2>

        <p>
          Content on this site is signed using two complementary technologies:
        </p>

        <p>
          <strong>C2PA (Coalition for Content Provenance and Authenticity)</strong>{" "}
          is an open standard that embeds a cryptographic manifest into media
          files. The manifest records who created the content, what tools were
          used, and provides a tamper-evident hash. C2PA is used to sign
          images, audio, and video on this site.
        </p>

        <p>
          <strong>Sentence-level text signing</strong> is Encypher&apos;s
          implementation of the C2PA text authentication specification (Section
          A.7). Invisible Unicode characters are inserted into the text at the
          sentence level, each carrying a unique identifier and an HMAC
          signature bound to the sentence content. These markers are invisible
          to readers, survive copy-paste and most text processing, and can be
          verified cryptographically.
        </p>

        <h2>Built by Encypher</h2>

        <p>
          Encypher builds cryptographic content provenance infrastructure for
          publishers, news organizations, and content platforms. Our technology
          embeds invisible, tamper-proof proof of origin into text at the
          sentence level -- proof that survives copy-paste, B2B distribution,
          and syndication.
        </p>

        <p>
          When content enters an AI training pipeline, Encypher signatures are
          detectable at the point of ingestion. Combined with formal notice from
          a publisher, this creates a clear evidentiary record that the content
          was identified, attributed, and its terms communicated -- before any
          use occurred.
        </p>

        <p>
          Encypher co-chairs the C2PA Text Provenance Task Force and authored
          the text authentication standard (Section A.7, C2PA 2.3, published
          January 2026) alongside Google, BBC, OpenAI, Adobe, and Microsoft.
        </p>

        <p>
          Learn more at{" "}
          <a
            href="https://encypher.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-ncs hover:underline"
          >
            encypher.com
          </a>
        </p>
      </div>
    </div>
  );
}
