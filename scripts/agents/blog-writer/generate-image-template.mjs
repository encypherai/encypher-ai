// Blog header image generation template.
// Placeholder tokens (__TOKEN__) are substituted by run.sh before execution.
// Do NOT edit the system prompt here without also updating .windsurf/workflows/generate-image.md.
import https from 'https';
import fs from 'fs';

const apiKey = process.env.GEMINI_API_KEY;
if (!apiKey) { console.error('ERROR: GEMINI_API_KEY not set in .env.skills'); process.exit(1); }

const outputPath = '__OUTPUT_PATH__';

const systemPrompt = `You are an expert technical illustrator for Encypher, a deep-tech infrastructure company. You create high-fidelity, institutional-grade visuals for a B2B audience of publisher General Counsels, CLOs, and C-suite executives. Your images look like they belong in a high-end security whitepaper or Bloomberg Terminal interface.

MANDATORY STYLE: Protocol Modernism. Flat, isometric, or 2D technical schematic. All imagery is clearly readable at a glance.
VIBE: "Verified Reality." Clean, precise, data-dense but not cluttered. Architectural Blueprint meets Cybersecurity Dashboard.
FINISH: Matte, non-reflective surfaces. No glossy glassmorphism. No 3D cartoonish rendering.
LIGHTING: Soft, diffuse, studio lighting. No dramatic cinematic shadows.
COMPOSITION: Structured, grid-based. Thin precise lines (1-2px) for connections.

MANDATORY COLOR PALETTE — dark mode first, strict adherence:
- Background: Deep Navy #1B2F50 — every image uses this
- Primary Elements: Azure Blue #2A87C4 — main nodes, active connections, key UI elements
- Secondary Elements: Light Sky Blue #B7D5ED — background graphs, grids, passive containers
- The Signal: Cyber Teal #00CED1 — MAX 5% of composition — verified/confirmed states only
- Text/Lines: Neutral Gray #A7AFBC — connecting lines, secondary labels
- Title Text: Pure White #FFFFFF — all title/header text in the image
- Subtitle Text: Light Sky Blue #B7D5ED — all subtitle/subheader text in the image
- Error State: Muted Coral #E07A5F — ONLY for failed/unverified states, max 10%
- Warning: Amber #F2CC8F — ONLY for pending/uncertain states, max 5%

FORBIDDEN: pure black #000000, bright red #FF0000, neon gradients, matrix green, gold/bronze/warm metallics, neon purple, any unlisted color.

TYPOGRAPHY RULES — critical, follow exactly:
- Title font: Roboto Bold or equivalent geometric sans-serif. Pure White (#FFFFFF). Large, dominant, highly legible. Minimum effective size for someone with impaired vision.
- Subtitle font: Roboto Regular or equivalent. Light Sky Blue (#B7D5ED). Clearly readable, positioned directly below the title.
- Technical labels: Roboto Mono. Neutral Gray or Light Sky Blue. Used for hash strings, timestamps, document IDs, status labels.
- Realistic technical data examples: hash 0x4A1F6E8D2C9B5A7F, timestamp 2026-02-05 14:30:00 UTC, doc ID DOC-5548-AF9B, status CRYPTOGRAPHIC SIGNATURE: VALID.
- ALL text must be large enough to read comfortably without squinting. Err on the side of larger text.

HUMAN FIGURES: Avoid entirely. Use abstract nodes, icons, interface panels. Stylized silhouettes only if absolutely necessary — no faces, no realistic proportions.

NO LOGOS: Do not attempt to render any company logos, wordmarks, or brand symbols. No Encypher logo. No C2PA logo. No third-party logos.

ENCYPHER MARK (for verified/confirmed states only): When a verification badge or certified checkmark is needed, render a circular badge with an organic/wavy outer border ring (not a perfect circle — the border has subtle irregular curves at regular intervals around the circumference), a smooth inner concentric circle ring, and a bold wide checkmark inside. The outer border is the most distinctive element — it reads as a circle but with a slightly irregular, hand-drawn quality to the edge. Fill in Cyber Teal (#00CED1). Use sparingly — max 5% of composition.

PROVEN STYLE: The clearest blog headers use a 2-3 stage left-to-right pipeline as the scene. Each stage is a distinct labeled node (document stack, cylinder, terminal, window panel). Muted Coral badges name the problem at each stage. Azure Blue arrows connect stages with direction. Roboto Mono labels below nodes provide technical detail. Title in the top third is very large and dominant over the scene. Scene fills the bottom two-thirds. Keep scenes simple and readable: 3-5 elements max, no overlapping labels, generous spacing. Prefer this style for any article with a clear process or mechanism to illustrate.

CRITICAL RULES — never violate:
1. Never render font names ("Roboto", "Roboto Mono", "Roboto Bold", or any font name) as visible text anywhere in the image. Font names are rendering instructions only.
2. Never render revenue percentages, split ratios, or revenue language ("60/40", "80/20", "majority", "you keep more", "revenue share") anywhere in the image.
3. Never render layout instruction text ("LAYOUT:", "TOP THIRD:", "BOTTOM TWO-THIRDS:", "1.9:1", "wide format") as visible text. These are composition instructions only.

NEGATIVE CONSTRAINTS: no stock photography, no photorealism, no human faces, no detailed cartoons, no 3D characters, no grunge textures, no bright red, no neon purple, no gold, no bronze, no warm metallics, no gradients, no lens flare, no glossy surfaces, no dramatic shadows, no pure black backgrounds, no logos of any kind, no font names as visible text, no revenue splits or percentages.`;

const articlePrompt = `LAYOUT: Blog header image, 1.9:1 wide format.
TOP THIRD: Title text (Roboto Bold, Pure White, very large — dominant element of the composition) with subtitle directly below it (Roboto Regular, Light Sky Blue, clearly readable). Both left-aligned or centered, with generous padding from edges (minimum 80px safe zone).
BOTTOM TWO-THIRDS: The visual scene fills this area and bleeds behind the text area with enough contrast that white text remains legible. Use a subtle dark overlay or deep navy gradient behind the text area only if needed for legibility. No logos anywhere.

TITLE TEXT TO RENDER IN THE IMAGE (Roboto Bold, Pure White #FFFFFF, large and dominant):
"__TITLE__"

SUBTITLE TEXT TO RENDER IN THE IMAGE (Roboto Regular, Light Sky Blue #B7D5ED, clearly readable, directly below title):
"__SUBTITLE__"

IMAGE SCENE (render below/behind the text, filling the composition):
__IMAGE_DESCRIPTION__`;

const fullPrompt = systemPrompt + '\n\n---\n\nGenerate this image now:\n\n' + articlePrompt;

const body = JSON.stringify({
  contents: [{ parts: [{ text: fullPrompt }] }],
  generationConfig: {
    responseModalities: ['IMAGE'],
    imageConfig: {
      aspectRatio: '16:9',
      image_size: '2K'
    }
  }
});

const options = {
  hostname: 'generativelanguage.googleapis.com',
  path: '/v1beta/models/gemini-3.1-flash-image-preview:generateContent',
  method: 'POST',
  headers: {
    'x-goog-api-key': apiKey,
    'Content-Type': 'application/json',
    'Content-Length': Buffer.byteLength(body)
  }
};

const req = https.request(options, (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => {
    try {
      const json = JSON.parse(data);
      if (json.error) { console.error('API error:', JSON.stringify(json.error, null, 2)); process.exit(1); }
      const parts = json.candidates?.[0]?.content?.parts ?? [];
      const imgPart = parts.find(p => p.inlineData);
      if (!imgPart) { console.error('No image in response:\n', data.slice(0, 500)); process.exit(1); }
      const buf = Buffer.from(imgPart.inlineData.data, 'base64');
      fs.writeFileSync(outputPath, buf);
      console.log('Saved:', outputPath, `(${(buf.length / 1024).toFixed(0)} KB)`);
    } catch (e) {
      console.error('Parse error:', e.message, '\nRaw:', data.slice(0, 500));
      process.exit(1);
    }
  });
});
req.on('error', e => { console.error('Request error:', e.message); process.exit(1); });
req.write(body);
req.end();
