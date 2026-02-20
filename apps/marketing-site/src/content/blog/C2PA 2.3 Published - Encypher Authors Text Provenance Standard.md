---
title: "C2PA 2.3 Published: Encypher Authors Text Provenance Standard"
date: "2026-01-08"
excerpt: "The C2PA 2.3 specification is now live, featuring Section A.7 on Embedding Manifests into Unstructured Text, authored by Encypher. This marks a milestone for text authentication."
author: "Erik Svilich"
image: "/images/blog/c2pa-2-3-published/c2pa-text-standard-header.png"
tags: ["C2PA", "ContentProvenance", "TextAuthenticity", "StandardsAuthority", "Milestone"]
---

**By: Erik Svilich, Founder & CEO | Encypher | C2PA Co-Chair**

Today, text has proof of origin on a global scale. 󠇟󠇠󠇡󠇢󠇋󠅖󠄥󠅂󠅙󠇭󠄷󠇜󠅵󠄰󠄻󠆔󠄾󠅆︆󠆨󠆄󠄮󠄤󠄆󠆞󠄥󠇔󠄜󠆎󠄋󠇬󠆯󠄞󠅥󠇖︈󠆂︃󠄈󠅋󠆈󠅲󠄻󠄲The **C2PA 2.3 specification is officially live**, and with it, **Section A.7: Embedding Manifests into Unstructured Text**, the section I authored as Co-Chair of the C2PA Text Provenance Task Force. 󠇟󠇠󠇡󠇢󠆵󠅡󠅿󠅅󠄦󠆜󠄱󠆚󠆗󠅿︅󠆤︄󠅦󠆪󠆍󠄃󠇥󠅩󠅉󠄎󠄯󠇘󠄲󠅈󠄠󠄪󠅉󠄢󠅃󠅸󠅝󠅳󠆸󠆒󠇩󠇪󠅐󠅾󠄅## 󠇟󠇠󠇡󠇢󠅉󠇍󠄛󠄓󠅓󠆋󠄰︃󠆋󠇄󠅅︆󠆦󠅧󠄐󠅙󠅅󠇢󠅳󠅪󠄍󠄷󠆚󠇝󠅉󠅅󠆏︈󠄭󠇪󠇫󠅨󠆖󠆘󠆎󠇃󠅲󠅤󠄤󠆮What This Means

For the first time, there is an **official, global standard** for embedding cryptographic provenance into plain text. 󠇟󠇠󠇡󠇢󠄞󠄢󠆕󠄾󠄐󠇩󠄹󠄃󠆝󠆰󠄔󠆵󠅆󠅬󠅻󠆺󠆠󠇣󠅘︌󠆴󠆗󠅦󠄺󠄂󠇟󠅺︆󠆏󠅅︊󠅄󠅅︁󠅶󠇭󠆕󠇩󠅌󠄑This enables:

- **Proof of origin** for any text content—articles, reports, AI outputs
- **Tamper-evident signatures** that survive copy-paste and distribution
- **Interoperability** across platforms, tools, and ecosystems

The specification is live at: [C2PA Section A.7](https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#embedding_manifests_into_unstructured_text)

## 󠇟󠇠󠇡󠇢󠆶󠄄󠄤󠅃󠆕󠅀󠄺󠅪󠆃󠆁󠇦󠄑󠄰︇󠇔󠅤󠇍󠇧󠅂󠄵󠅎󠆓󠇙󠅺󠆯󠅕󠅐󠅟󠅘󠇣󠇛󠆭󠄊󠄡󠇞󠅖󠇝󠅛󠅴󠅘The Technical Foundation

Section A.7 introduces the `C2PATextManifestWrapper` structure, which uses Unicode variation selectors to embed C2PA manifests invisibly within text. 󠇟󠇠󠇡󠇢󠄔󠆭󠆒󠄸󠅥󠇈󠄵󠄐󠆣󠇏︍󠄧󠆯󠅂󠅛︎󠆕󠇉󠅼󠄩󠆍󠇟󠅌󠅃󠇝󠄈󠇈󠇅󠆱󠅋󠅏︋󠄺󠇌󠄞󠄗󠅥󠆾️󠆼Key elements include:

- **Magic number:** `󠇟󠇠󠇡󠇢󠄐󠆨󠅕󠇡︀󠅥󠄹󠆷󠆁󠇥󠄎󠇕󠆮󠆑󠇪󠆖󠇧︌󠆮󠇔󠅭󠄮󠅢󠄈󠆻󠆍󠇥󠆷󠄾󠄧󠄀󠄸︃󠇁󠄅󠄘󠇌󠆣󠅧󠄁C2PATXT\0` (0x4332504154585400)
- **Encoding:** Unicode variation selectors (U+FE00-U+FE0F and U+E0100-U+E01EF)
- **Prefix:** Zero-Width No-Break Space (U+FEFF) for forward compatibility
- **Validation:** 󠇟󠇠󠇡󠇢󠇦󠄓󠅄󠄾󠆭󠄺󠄴󠄩󠆭󠄃󠆜󠄻󠄷󠄯󠆻󠅶️󠆏󠆚󠅣󠄾󠄥󠆓󠆑󠅆󠇥󠇕󠅈󠄥󠄎󠄤󠄜󠅑󠇭󠇅󠄉󠅛󠆈︋󠅼NFC normalization and byte-offset exclusion handling

This approach ensures that provenance data travels with the text itself—not in a separate file or database.

## From Task Force to Standard

When I joined C2PA as Co-Chair of the Text Provenance Task Force alongside colleagues from Google, BBC, OpenAI, Adobe, and Microsoft, the challenge was clear: **text had no proof of origin**. 󠇟󠇠󠇡󠇢󠇆󠄤󠆞󠅫󠄄󠆋󠄱󠄴󠅻󠅄󠇟󠄤󠅮󠅉󠄆󠇃󠅀󠄳︀󠇄󠅻󠇇󠄉󠆲󠆼󠆜󠇊󠆀󠅕󠄚︋󠇡󠅒󠇯󠅕󠄧󠆺󠅉󠄣󠇛For decades, images have had EXIF. 󠇟󠇠󠇡󠇢󠇣󠅥󠇧󠆎󠇬󠅭󠄼󠇡󠅳󠆓󠆂󠅀︀󠄽︅󠄇󠄪󠄾󠄭󠆨󠅔󠄪󠄸󠆂󠅤󠆥󠇤󠇯󠇙󠅰󠇎󠅣󠅠󠆲󠄠󠄺󠆽󠄹󠅲󠇋Videos have container metadata. 󠇟󠇠󠇡󠇢󠅮󠄿󠇈󠅚󠇖󠄁󠄶󠅵󠆣󠅅󠅤󠇋󠅲󠇡󠆏󠆈󠅙󠇣󠆧󠇄󠆓󠅉󠇋󠆌󠆸󠇄󠅬󠄍︉︍󠅓󠇋󠅲󠇪󠄤󠄒󠄘󠅑󠄎󠄦PDFs have digital signatures. 󠇟󠇠󠇡󠇢󠆅󠇫󠄹︂󠆖󠆪󠄻󠇁󠅻󠆑󠄼󠇥󠇂󠅫󠇅︃󠄲󠅜󠆽󠄋󠄕󠇚︄󠇌󠅙󠇩󠇠󠇟󠅇︃󠅫󠅉󠆦󠄒󠆽󠇧󠆽󠄺󠄥󠄵Plain text, which is the fabric of AI training data, news articles, research, and most digital communication, had nothing. 󠇟󠇠󠇡󠇢󠄊󠆎󠆭󠆧󠅟󠄦󠄹󠆦󠅵󠄛󠇆󠄥󠄻󠅷󠅪󠇓󠆴󠄖󠆌󠅏󠄎󠅓󠅟󠄻󠅜󠅕󠄿󠅽󠄞󠆥󠇁󠆛︄︅󠇂󠇤󠄣󠅓︁󠄄Today, that changes.

## Acknowledgments

Standards aren't built alone. 󠇟󠇠󠇡󠇢󠇁󠅚󠆳󠆑︃󠄯󠄳︎󠆖󠅒󠇪󠅧󠆾󠅞󠅍󠇪󠄩󠄆󠇧󠆒󠅪󠄛󠄩󠄞󠅸󠅗󠆓󠄘︄󠄋󠅕󠇚󠆱󠇔󠅥󠄑󠅏󠅌󠅞󠄢Deep gratitude to Leonard Rosenthol, Charlie Halford, and the broader C2PA community. 󠇟󠇠󠇡󠇢󠅽󠆭︋󠇨󠇂󠄊󠄴󠆄󠆭󠆡󠆚󠅼󠄵󠄌󠇮󠆟󠄼󠇍󠄶󠅦󠇓󠆽󠇞󠅌󠇫󠅿󠇖󠇆󠆌︊󠆓󠅚󠅦󠄉󠄲󠄾󠅬󠆣󠅲󠇡You challenged assumptions, sharpened the technical approach, and helped guide what started as a concept into a global open standard. 󠇟󠇠󠇡󠇢󠅟󠆽󠆾󠅢󠇛󠄕󠄲󠅁󠅴󠅴󠆞󠅲󠄣󠆠󠄆󠅱󠆅󠄳󠆣󠆵󠅬󠇗󠇉󠄲󠅡󠄎󠄻󠅽󠆭󠅽󠇏󠅍󠆌󠄒󠆒󠇋󠆳󠄶󠄃󠄁Working alongside colleagues from Google, BBC, OpenAI, Adobe, and Microsoft reinforced something I believe deeply: the best infrastructure is built together. 󠇟󠇠󠇡󠇢󠅘󠅰󠇣︅󠅊󠅍󠄹󠆄󠆨󠆊󠅲󠇚󠆳󠇑󠆕󠅴󠇪󠅙󠇔󠇧󠇬󠆢󠅈󠇜󠇨󠅸󠄋󠄱󠇑󠄼󠆽󠄅󠆗󠇇󠅩󠅐󠅗󠄔󠅺︈## 󠇟󠇠󠇡󠇢󠆡󠇙󠅇󠄂󠄇󠅷󠄹󠆓󠆊󠇔󠇢󠅊󠇠󠇆󠄽󠇤󠆎󠆞󠇢󠅖󠆭󠆤󠄅󠇔󠆤󠄞󠅾󠇋󠅧󠅬󠆄󠇬󠆁󠅙󠆢︀󠄖󠄚︃󠆋What This Enables

- **Creators** gain cryptographic proof of authorship over their IP—before AI "hallucinates" their work
- **Publishers** shift from litigation whack-a-mole to licensing infrastructure
- **AI companies** get attribution data, tools to verify quote integrity, and the technical ability to meet regulatory requirements like the EU AI Act
- **Enterprises** gain real governance for AI-generated content

With this technology, we're building an ecosystem centered on transparency, trust, and a fair content economy. 󠇟󠇠󠇡󠇢󠅾󠄣󠇭󠅾󠄡󠇑󠄽︈󠆞󠅴󠅶󠅆󠆟󠇛󠄌󠄏󠆷󠄺󠅥󠅌󠄂󠇠󠅋︈󠇃︆󠆈󠆾󠇯󠄀󠄹󠇍󠄖󠇨︈󠅥󠄺󠆦󠄾󠄊## 󠇟󠇠󠇡󠇢󠅆󠇇󠄢󠄚󠆒󠆙󠄾󠄽󠆄󠄎󠇆󠆘󠄔󠅺󠅯󠅺󠆮󠄔︎󠆹󠄆󠆍󠄝󠆖󠆎󠄴󠄾︇󠅓󠅵󠅝󠆬󠅮󠇃󠇁󠇇󠅟︉󠅈󠅂What Comes Next

The standard provides the foundation. 󠇟󠇠󠇡󠇢󠅶󠇂󠇟󠅟󠅾󠇧󠄵󠆶󠆙󠅜󠄐󠇅󠅎󠄓︄󠇝󠅹󠄂󠄆󠆃󠅅󠅥󠆒󠄦󠆍󠇥󠅹󠄶󠆠󠄀󠇀󠇄󠅈󠆟󠇞︄︇󠆛󠅏󠆽At Encypher, we've built tools that implement and extend it—sentence-level tracking, formal notice infrastructure, quote integrity verification.

### Extending the Standard

Yesterday (January 7, 2026), we filed our first provisional patent application covering sentence-level tracking and related innovations. 󠇟󠇠󠇡󠇢󠇩󠅮󠅚︌󠆙󠆉󠄽󠄪󠅽󠆮󠇅󠆯󠆔︋󠅖󠅲󠄨󠄨󠅧󠇫󠆢󠅋󠄾󠅼󠅆󠄡󠇅󠆼󠄨󠆽󠆻󠇭󠄨󠆈󠅹󠆦︇󠄄󠆫󠆉The open C2PA standard provides the foundation; our patent-pending technology enables the business value that publishers and AI companies need:

- **Sentence-level granularity** for precise attribution (not just document-level)
- **Willful infringement enablement** through formal notice infrastructure
- **Quote integrity verification** to prove AI accuracy vs. hallucination
- **Performance intelligence** for content analytics and optimization

### Syracuse Symposium

On **February 25, 2026**, we're convening the Syracuse Symposium to translate technical standards into market licensing frameworks. 󠇟󠇠󠇡󠇢︇󠄟󠆝󠆀󠆰󠅿󠄰󠄭󠆀󠇋󠆤󠆁󠄼󠄾󠇬󠇍󠆆󠄤󠄸󠄒󠇘󠅥󠅶󠅣󠄶󠅟󠇃󠅩󠅜󠇈󠇓󠄤󠄌󠇞󠅞󠅺󠄺󠄫󠅨󠄥Publisher general counsels and AI company commercial leads will define the terms of engagement for the AI content economy.

### Infrastructure Rollout

Our API and SDKs (Python, TypeScript, Go, Rust) are production-ready. 󠇟󠇠󠇡󠇢󠇡󠅷󠇮󠄤󠄞󠅹󠄹󠆎󠆐󠄸󠆳󠅞󠅚󠆭󠄨󠇚󠅆󠅍󠄰󠄇󠄠󠄣󠅋󠅅󠄱󠄀︄󠆿󠄙󠄹󠅒󠅶󠇕󠄌︉󠆉󠅓︃󠆐󠅚Publishers can implement sentence-level tracking in 30 days. 󠇟󠇠󠇡󠇢󠆯󠅗󠇞󠅛󠅙󠅜󠄷󠇟󠆃󠇖󠄻󠆧󠄍󠇉󠆒󠅦󠄔󠆏󠅛󠆩󠆘󠄮󠅔󠆳︃󠄾󠆲󠅘󠅞󠆬︉️󠇝󠅮󠄲󠅼󠄺󠄶󠆓󠇠AI labs get one integration for the entire publisher ecosystem.

## Join the Beta

We're opening beta access for our API and tools now:

- **Publishers & Rights Holders:** 󠇟󠇠󠇡󠇢󠅩󠅦󠆥󠆟󠅟󠇀󠄰󠆪󠅲󠇣︍󠆳󠆴󠆏󠅗󠇢󠇀󠅘󠆀󠅊󠇩󠄥󠆉󠆣󠅁󠄸󠄈󠅽󠅼󠅫󠅨󠆂󠅿󠅚󠄲󠆒󠄊󠆤󠄄󠆋[Request Beta Access](/publisher-demo)
- **AI Labs & Platforms:** 󠇟󠇠󠇡󠇢󠆫󠇊󠄈󠅟󠇊󠄶󠄵︅󠆯󠅼󠆤󠇫󠆰󠄁󠇄󠄆󠇍󠄠󠄤󠆚󠆨󠅚󠅶󠅬󠆘󠆳󠆑󠇄󠇍󠇤󠄞󠅨󠆁︂󠅄󠇙󠅰󠆎󠄚󠅵[Request Beta Access](/ai-demo)
- **C2PA v2.3 Text Provenance Specification:** 󠇟󠇠󠇡󠇢󠇉󠄜󠄲︂󠇅󠅿󠄵󠅽󠆤󠄸󠅿󠆂󠆑󠄼󠇂󠅊󠆢󠆞󠇡󠅪󠄩󠄭󠄜󠄓󠅕󠄈︀󠇛󠄈󠅲󠆴󠅸󠅻󠄪󠄔󠅼󠄼󠅔󠄌󠅂[C2PA v2.3](https://spec.c2pa.org/specifications/specifications/2.3/specs/C2PA_Specification.html#embedding_manifests_into_unstructured_text) 󠇟󠇠󠇡󠇢󠆛󠄋󠇤󠅰󠆣󠆞󠄻󠆉󠆚󠆱󠅟󠅸󠅵󠅧󠅝󠅖󠄣󠄊󠇏󠅁󠇤󠇮󠇆󠄦󠄖󠅮󠇠󠆳󠄝󠄴󠇐︇󠇙󠇮︀󠆘󠆙󠄐󠅓󠅳The standard is published. 󠇟󠇠󠇡󠇢󠄹󠇋󠇗︌︌󠆲󠄴󠄁󠆛󠇤󠆴󠇦󠇙󠇞︅󠅡󠆦󠇞󠅱󠆝󠅣󠄽󠄔󠆓󠆵󠆴󠆓󠄪󠇍󠅚󠆪󠇀󠄬︌󠅦󠅼︍󠇋󠇍󠆥Our infrastructure is ready. 󠇟󠇠󠇡󠇢󠆛󠄁󠆚󠆀󠄢󠆹󠄱󠇥󠆫󠄊󠇕󠆳󠅑󠄷󠆏󠆢󠄓󠄴󠅘︎󠆽󠆞󠅾󠄐󠆟󠇍󠆀󠄱󠆳󠄧󠆷󠄿󠄟󠆠󠄚󠄫󠇊󠆞󠅻󠄑Are you?

---

*Erik Svilich is Founder & CEO of Encypher Corporation and Co-Chair of the C2PA Text Provenance Task Force. 󠇟󠇠󠇡󠇢󠅴󠄣󠅻󠅀󠆅󠇒󠄶󠅟󠆟󠅙󠆲󠅱󠆺󠆪󠆉󠅵󠅤󠇬󠄪󠄳󠆇󠄢󠅃󠇆󠇉󠆮󠅜󠇐󠄏󠄤󠇍󠇞󠄼󠄣󠇉󠄨󠅥󠄮󠅈󠅤He authored C2PA Section A.7: Embedding Manifests into Unstructured Text. *󠇟󠇠󠇡󠇢󠄵󠄷󠄱󠆻󠅠󠅠󠄵󠄱󠆙󠄛󠆽︉󠇥󠄮󠇒󠇄󠄫󠇭󠅊󠇥󠆼󠆜󠄙󠄥󠅅󠄆󠄗󠆩󠅇󠇂󠅛󠄘󠄐󠅵󠆡󠆟󠇚󠅐󠆨󠆠󠇟󠇠󠇡󠇢󠆉󠄿󠅽󠆏󠇄󠇄󠄶󠅉󠆮󠆸󠅽󠄕󠅿󠄹󠄿󠄡󠄤󠆌󠄇󠆦󠇘󠆋󠆐󠇃󠆢󠄌󠄌󠅾󠆡󠅢󠇖󠅙󠆫󠇨󠄄󠆨󠅾󠆹󠄠󠅌