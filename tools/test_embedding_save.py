"""Test that embeddings are actually saved to files."""
import asyncio
from pathlib import Path

import httpx


async def test():
    # Read the first article
    path = Path('../outputs/wikipedia_prepared/part_00000/article_0000000.txt')
    text = path.read_text(encoding='utf-8')
    
    # Call API
    data = {
        'document_id': path.stem,
        'text': text,
        'segmentation_level': 'sentence'
    }
    headers = {'Authorization': 'Bearer demo-key-local'}
    url = 'http://127.0.0.1:9000/api/v1/enterprise/embeddings/encode-with-embeddings'
    
    async with httpx.AsyncClient(timeout=60.0, headers=headers) as client:
        r = await client.post(url, json=data)
        r.raise_for_status()
        
        response_json = r.json()
        embedded = response_json.get('embedded_content')
        
        if embedded:
            out = path.parent / f'{path.stem}.embedded{path.suffix}'
            out.write_text(embedded, encoding='utf-8')
            print(f'✓ Saved to: {out.name}')
            print(f'  File exists: {out.exists()}')
            print(f'  Absolute path: {out.resolve()}')
            print(f'  File size: {out.stat().st_size} bytes')
            print(f'  Original size: {path.stat().st_size} bytes')
            
            # Verify it exists
            if out.exists():
                print(f'\n✓ SUCCESS! File verified at: {out.resolve()}')
            else:
                print('\n✗ ERROR! File does not exist after write!')
        else:
            print('✗ No embedded_content in response')

asyncio.run(test())
