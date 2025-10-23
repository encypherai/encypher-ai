> **Note:** Legacy embedding targets (``whitespace``, ``punctuation`` and similar)
> remain available for the ``basic``, ``manifest``, and ``cbor_manifest`` formats.
> When ``metadata_format="c2pa"`` the library automatically appends a
> FEFF-prefixed ``C2PATextManifestWrapper`` to the end of the visible text so the
> manifest stays contiguous, satisfying the latest specification.

# Advanced C2PA Text Demo

This guide provides a comprehensive walkthrough of the C2PA text demo located in `demos/c2pa_demo/`. The demo showcases how to embed C2PA manifests into HTML articles and implement a verification UI with visual indicators.

## Demo Overview

The C2PA text demo demonstrates:

1. Embedding C2PA manifests into HTML articles
2. Verifying embedded metadata and content integrity
3. Displaying verification results in a user-friendly UI
4. Simulating and detecting tampering scenarios

## Setup Instructions

Before running the demo:

1. Navigate to the demo directory:
   ```bash
   cd demos/c2pa_demo
   ```

2. Install dependencies:
   ```bash
   uv pip install -r requirements.txt
   ```

3. Generate or use existing keys:
   ```bash
   uv run python generate_keys.py
   ```
   This will create a `demo_keys.json` file if it doesn't exist.

## Demo Components

### Key Files

- `article.html`: The original article template
- `embed_manifest_improved.py`: Script to embed C2PA manifest into the article
- `demo_dashboard.py`: Streamlit UI for displaying and verifying the article
- `temp_verify.py`: Script for verifying embedded metadata
- `temp_verify_tamper.py`: Script demonstrating tamper detection
- `enhanced_tamper_test.py`: Comprehensive tamper detection examples
- `prep_demo.py`: Script to prepare the demo (embedding and UI setup)

### Embedding Process

The embedding process uses BeautifulSoup for robust HTML parsing and appends the C2PA wrapper to the first paragraph of the article:

```python
# From embed_manifest_improved.py
from bs4 import BeautifulSoup
from encypher.core.unicode_metadata import UnicodeMetadata
from encypher.interop.c2pa import compute_normalized_hash, normalize_text

# Parse HTML
soup = BeautifulSoup(html_content, "html.parser")

# Find first paragraph within content column
first_p = soup.select_one(".content-column p")

# Prepare optional custom actions for the c2pa.actions.v1 assertion
custom_actions = [
    {
        "label": "c2pa.created",
        "when": datetime.now().isoformat(),
        "softwareAgent": "encypher-ai/demo",
    }
]

# Embed metadata into paragraph text (wrapper appended to the end)
paragraph_text = normalize_text(first_p.get_text())
embedded_text = UnicodeMetadata.embed_metadata(
    text=paragraph_text,
    private_key=private_key,
    signer_id=signer_id,
    metadata_format="c2pa",
    claim_generator="encypher-ai/demo",
    actions=custom_actions,
    add_hard_binding=True,
)

# Replace paragraph text with embedded text
first_p.string = embedded_text
```

### Content Hash Calculation

``UnicodeMetadata`` normalises the paragraph, appends the wrapper, and records the
wrapper's byte span in the ``c2pa.hash.data.v1`` assertion automatically. If you
need to pre-compute the digest for auditing or logging, use the shared helper:

```python
paragraph_hash = compute_normalized_hash(paragraph_text)
print("Pre-embed NFC hash:", paragraph_hash.hexdigest)
```

After embedding you can reproduce the recorded digest by removing the wrapper
bytes from the normalised text and re-running ``compute_normalized_hash`` (see
the basic tutorial for a standalone example).

### UI Integration

The demo includes a Streamlit dashboard that displays the article with verification indicators:

```python
# From demo_dashboard.py
def enhance_html_with_logo_and_popup(html_content, manifest_data):
    """Add EncypherAI logo badge and manifest popup to the HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find first paragraph (which contains embedded metadata)
    first_p = soup.select_one('.content-column p')
    if not first_p:
        return html_content

    # Create badge container
    badge_container = soup.new_tag('div')
    badge_container['class'] = 'badge-container'

    # Create badge image
    badge_img = soup.new_tag('img')
    badge_img['src'] = 'icon-logo-nobg.png'
    badge_img['class'] = 'encypher-badge'
    badge_img['alt'] = 'EncypherAI Verified'
    badge_img['title'] = 'Click to view provenance information'
    badge_img['onclick'] = 'toggleManifestPopup()'

    # Add badge to container
    badge_container.append(badge_img)

    # Create paragraph wrapper
    paragraph_wrapper = soup.new_tag('div')
    paragraph_wrapper['class'] = 'paragraph-wrapper'

    # Move paragraph into wrapper
    first_p_copy = first_p.extract()
    paragraph_wrapper.append(first_p_copy)

    # Create column container
    column_container = soup.new_tag('div')
    column_container['class'] = 'column-container'

    # Add badge and paragraph to column container
    column_container.append(badge_container)

    # Create content column
    content_column = soup.new_tag('div')
    content_column['class'] = 'content-column'
    content_column.append(paragraph_wrapper)

    # Add content column to container
    column_container.append(content_column)

    # Create blank column
    blank_column = soup.new_tag('div')
    blank_column['class'] = 'blank-column'
    column_container.append(blank_column)

    # Add manifest popup
    manifest_popup = create_manifest_popup(soup, manifest_data)

    # Insert column container and popup where the paragraph was
    first_p.insert_before(column_container)
    first_p.insert_before(manifest_popup)

    # Add verification notice under author line
    add_verification_notice(soup)

    # Add required CSS and JavaScript
    add_css_and_js(soup)

    return str(soup)
```

### Tamper Detection

The demo includes scripts to simulate and detect tampering:

```python
# From enhanced_tamper_test.py
def test_content_tampering():
    """Test tampering with the article content."""
    print("SCENARIO 1: CONTENT TAMPERING TEST")
    print("==================================")

    # Load the encoded article
    with open('encoded_article.html', 'r', encoding='utf-8') as f:
        encoded_html = f.read()

    # Extract text content for hashing
    soup = BeautifulSoup(encoded_html, 'html.parser')
    paragraphs = soup.find_all('p')
    article_text = '\n'.join([p.get_text() for p in paragraphs])

    print("1. Original content hash calculation:")
    original_hash = compute_normalized_hash(article_text).hexdigest
    print(f"   Original hash: {original_hash[:10]}...{original_hash[-10:]}")

    # Tamper with content (change second paragraph)
    print("\n2. Simulating content tampering...")
    second_p = paragraphs[1]
    original_text = second_p.get_text()
    tampered_text = original_text.replace("artificial intelligence", "TAMPERED TEXT")
    second_p.string = tampered_text

    # Save tampered article
    with open('tampered_content_article.html', 'w', encoding='utf-8') as f:
        f.write(str(soup))
    print("   Tampered article saved as 'tampered_content_article.html'")

    # Calculate new hash
    tampered_paragraphs = soup.find_all('p')
    tampered_article_text = '\n'.join([p.get_text() for p in tampered_paragraphs])
    tampered_hash = compute_normalized_hash(tampered_article_text).hexdigest

    print("\n3. New content hash after tampering:")
    print(f"   Tampered hash: {tampered_hash[:10]}...{tampered_hash[-10:]}")

    # Verify the tampered article
    print("\n4. Verifying tampered article...")
    verify_result = verify_article('tampered_content_article.html')

    print("\n5. Tampering detection result:")
    if verify_result['verified']:
        print("   [FAIL] Signature verification passed (expected)")
        if verify_result['content_hash_verified']:
            print("   [FAIL] Content hash verification passed (unexpected!)")
        else:
            print("   [PASS] Content hash verification failed (tampering detected)")
            print(f"   Stored hash: {verify_result['stored_hash'][:10]}...{verify_result['stored_hash'][-10:]}")
            print(f"   Current hash: {verify_result['current_hash'][:10]}...{verify_result['current_hash'][-10:]}")
    else:
        print("   [FAIL] Signature verification failed (unexpected)")
```

## Running the Demo

To run the complete demo:

1. Prepare the demo files:
   ```bash
   uv run prep_demo.py
   ```

2. Launch the Streamlit UI:
   ```bash
   uv run prep_demo.py --ui
   ```

3. Test tamper detection:
   ```bash
   uv run enhanced_tamper_test.py
   ```

## Demo Walkthrough

### Step 1: View the Original Article

The original `article.html` is a simple HTML article with a title, author, and multiple paragraphs. It uses a column-based layout with CSS grid:

```html
<!DOCTYPE html>
<html>
<head>
    <title>The Future of AI</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            max-width: 800px;
            margin: 0 auto;
        }
        h1 {
            color: #333;
        }
        .author {
            font-style: italic;
            color: #666;
            margin-bottom: 20px;
        }
        .column-container {
            display: grid;
            grid-template-columns: 40px 1fr 40px;
            gap: 10px;
        }
        .badge-container {
            grid-column: 1;
        }
        .content-column {
            grid-column: 2;
        }
        .blank-column {
            grid-column: 3;
        }
    </style>
</head>
<body>
    <h1>The Future of AI</h1>
    <div class="author">By Dr. Jane Smith | June 15, 2025</div>

    <div class="column-container">
        <div class="badge-container"></div>
        <div class="content-column">
            <p>Artificial intelligence has evolved dramatically over the past decade...</p>
        </div>
        <div class="blank-column"></div>
    </div>

    <!-- More paragraphs in column containers -->
</body>
</html>
```

### Step 2: Embed the C2PA Manifest

Running `embed_manifest_improved.py` appends a C2PA text wrapper to the article:

1. The script extracts and normalises the text content of the article.
2. Calculates a SHA-256 hash of the normalised content.
3. Creates a C2PA manifest with the content hash and metadata (including the wrapper exclusion offsets).
4. Packages the manifest store into a JUMBF box and encodes it as a FEFF-prefixed block of variation selectors.
5. Appends the wrapper block to the end of the visible text and saves the result as `encoded_article.html`.

### Step 3: View the Encoded Article

The encoded article looks visually identical to the original, but it now terminates with an invisible block of Unicode variation selectors that contains the C2PA manifest.

### Step 4: Verify the Encoded Article

Running `temp_verify.py` verifies the embedded metadata and content hash:

1. Locates the FEFF-prefixed wrapper at the end of the text and decodes the JUMBF manifest store.
2. Verifies the COSE signature using the public key.
3. Reads the recorded exclusion offsets and removes the wrapper bytes from the normalised text.
4. Calculates the current content hash.
5. Compares the stored and current hashes.

If the verification is successful, you'll see:

```
Signature verification: PASSED
Content hash verification: PASSED
```

### Step 5: Test Tamper Detection

Running `enhanced_tamper_test.py` demonstrates two tamper scenarios:

1. **Content Tampering**: Modifies the article text after embedding
   - The signature verification passes
   - The content hash verification fails

2. **Metadata Tampering**: Modifies the embedded manifest itself
   - The signature verification fails
   - The tampered manifest is detected

### Step 6: View the UI Dashboard

The Streamlit dashboard displays:

1. The encoded article with an EncypherAI badge next to the first paragraph
2. A verification notice under the author line
3. A popup that shows the manifest details when clicking the badge
4. Verification results showing the signature and content hash status

## Customization Options

### Embedding Location

C2PA manifests always append a FEFF-prefixed wrapper to the end of the text.
The ``target`` parameter is ignored for ``metadata_format="c2pa"`` because the
specification requires the wrapper to remain contiguous.

### Manifest Content

Customise the manifest by adjusting the ``claim_generator`` string, providing
pre-existing action entries, or toggling ``add_hard_binding``. The library
constructs the remaining assertions automatically.

```python
custom_actions = [
    {
        "label": "c2pa.created",
        "softwareAgent": "YourApp/1.0.0",
        "when": datetime.now().isoformat(),
    },
    {
        "label": "c2pa.captured",
        "softwareAgent": "YourApp/1.0.0",
        "description": "Article prepared with EncypherAI",
    },
]

embedded_text = UnicodeMetadata.embed_metadata(
    text=first_p.get_text(),
    private_key=private_key,
    signer_id=signer_id,
    metadata_format="c2pa",
    claim_generator="YourApp/1.0.0",
    actions=custom_actions,
    add_hard_binding=True,
)
```

### UI Customization

You can customize the verification UI by modifying the CSS and HTML in `demo_dashboard.py`:

```python
def add_css_and_js(soup):
    """Add required CSS and JavaScript to the soup."""
    # Customize CSS here
    css = """
    .encypher-badge {
        width: 30px;
        height: 30px;
        cursor: pointer;
    }
    .manifest-popup {
        display: none;
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 0 20px rgba(0,0,0,0.3);
        z-index: 1000;
        max-width: 80%;
        max-height: 80%;
        overflow-y: auto;
    }
    /* Add your custom CSS here */
    """

    # Add the CSS to the head
    style_tag = soup.new_tag('style')
    style_tag.string = css
    soup.head.append(style_tag)

    # Add JavaScript for popup functionality
    js = """
    function toggleManifestPopup() {
        var popup = document.getElementById('manifestPopup');
        if (popup.style.display === 'block') {
            popup.style.display = 'none';
        } else {
            popup.style.display = 'block';
        }
    }

    function closeManifestPopup() {
        document.getElementById('manifestPopup').style.display = 'none';
    }

    // Add your custom JavaScript here
    """

    script_tag = soup.new_tag('script')
    script_tag.string = js
    soup.body.append(script_tag)
```

## Conclusion

The C2PA text demo showcases a complete implementation of text provenance using EncypherAI's Unicode variation selector approach. It demonstrates:

1. How to embed C2PA manifests into HTML articles
2. How to verify embedded metadata and detect tampering
3. How to create a user-friendly verification UI

This implementation provides a robust foundation for adding provenance to text content in real-world applications.
