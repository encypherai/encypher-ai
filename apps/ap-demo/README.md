# AP Quote Integrity Demo

A canned demo application for presenting Encypher's cryptographic provenance capabilities to the Associated Press.

## Demo Overview

This demo showcases a 2-3 minute presentation flow:

### Step 1: Mark the Content (30 seconds)
- Display a real AP-style article
- Click "Embed Provenance" to mark with cryptographic signatures
- Show that the article looks identical but now carries invisible provenance

### Step 2: Simulate AI Use Case (45 seconds)
- Mock ChatGPT-style interface shows AI quoting the article
- Two scenarios available:
  - **Accurate Quote**: AI quotes AP content correctly
  - **Modified Quote**: AI alters the content (hallucination)

### Step 3: The Verification (45 seconds)
- Paste quoted text into Encypher decoder
- **Scenario A (Accurate)**: ✅ Green checkmark - provenance verified
- **Scenario B (Modified)**: ❌ Red flag - content mismatch detected

### Step 4: Downstream Survival (30 seconds)
- Copy marked content and paste elsewhere
- Demonstrate that provenance survives copy/paste operations
- Simulates scraping, syndication, or database storage

## Setup

### Prerequisites
- Node.js 18+
- npm or yarn
- Access to Encypher Enterprise API (hosted or local)

### Installation

```bash
cd apps/ap-demo
npm install
```

### Configuration

1. Copy the example environment file:
```bash
cp .env.example .env.local
```

2. Configure your API settings in `.env.local`:
```env
# Use hosted API
NEXT_PUBLIC_API_URL=https://api.encypherai.com
NEXT_PUBLIC_API_KEY=your_api_key_here

# Or use local API
NEXT_PUBLIC_API_URL=http://localhost:9000
NEXT_PUBLIC_API_KEY=your_local_api_key
```

### Running the Demo

```bash
npm run dev
```

Open [http://localhost:3050](http://localhost:3050) in your browser.

## Demo Mode

The demo includes fallback behavior when the API is unavailable:
- Content marking works with simulated provenance
- Verification shows accurate results based on the selected scenario
- All UI flows work correctly for presentation purposes

## Key Messages for AP

Based on Paul Cheung's concerns and priorities:

| AP Concern | Demo Element |
|------------|--------------|
| Brand association with fact-based journalism | Quote accuracy verification |
| Content available without going to apnews.com | Downstream survival test |
| 38% of traffic is bots / scraping | Marked content detectable regardless of acquisition |
| Attribution importance | Real-time proof of accurate vs. modified attribution |
| Microsoft PCM / usage-based model | Cryptographic proof enables pay-per-verified-use |

## Technical Architecture

- **Frontend**: Next.js 14 with React 18
- **Styling**: TailwindCSS
- **Icons**: Lucide React
- **API**: Encypher Enterprise API
  - `POST /api/v1/sign/advanced` - Embed provenance (Professional+ tier)
  - `POST /api/v1/verify` - Verify provenance

## Files Structure

```
apps/ap-demo/
├── src/
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/
│   │   ├── APArticle.tsx       # Step 1: Article display + marking
│   │   ├── AIChatSimulator.tsx # Step 2: Mock AI chat
│   │   ├── VerificationDecoder.tsx # Step 3: Verification
│   │   └── DownstreamSurvival.tsx  # Step 4: Copy/paste test
│   └── lib/
│       ├── api.ts              # API client
│       ├── demo-data.ts        # Pre-loaded content
│       └── utils.ts            # Utility functions
├── .env.example
├── package.json
├── tailwind.config.ts
└── README.md
```

## Presentation Tips

1. **Lead with outcomes, not technology**: "This proves it's yours", "This proves it wasn't changed"
2. **Don't over-explain cryptography**: Paul will ask technical questions if interested
3. **Focus on business impact**: Leverage for renegotiation, forensic evidence of usage
4. **Keep it flowing**: The demo is designed for ~2-3 minutes total
