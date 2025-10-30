"""
Verification report generation for batch signing operations.

Generates reports in multiple formats:
- HTML (for web publishing)
- Markdown (for documentation)
- JSON (for programmatic access)
- CSV (for spreadsheet analysis)
"""
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import json
import csv

from .batch import BatchSigningResult, SigningResult


class ReportGenerator:
    """
    Generate verification reports from batch signing results.
    
    Example:
        >>> result = signer.sign_directory(...)
        >>> generator = ReportGenerator()
        >>> generator.generate_html(result, Path("report.html"))
    """
    
    def generate_html(
        self,
        result: BatchSigningResult,
        output_path: Path,
        title: str = "Content Verification Report",
        publisher: Optional[str] = None
    ) -> None:
        """
        Generate HTML verification report.
        
        Args:
            result: Batch signing result
            output_path: Path to save HTML file
            title: Report title
            publisher: Publisher name for header
        """
        html = self._generate_html_content(result, title, publisher)
        output_path.write_text(html, encoding='utf-8')
    
    def generate_markdown(
        self,
        result: BatchSigningResult,
        output_path: Path,
        title: str = "Content Verification Report"
    ) -> None:
        """
        Generate Markdown verification report.
        
        Args:
            result: Batch signing result
            output_path: Path to save Markdown file
            title: Report title
        """
        md = self._generate_markdown_content(result, title)
        output_path.write_text(md, encoding='utf-8')
    
    def generate_csv(
        self,
        result: BatchSigningResult,
        output_path: Path
    ) -> None:
        """
        Generate CSV verification report.
        
        Args:
            result: Batch signing result
            output_path: Path to save CSV file
        """
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'File Path',
                'Status',
                'Document ID',
                'Verification URL',
                'Processing Time (s)',
                'Error'
            ])
            
            # Data rows
            for r in result.results:
                writer.writerow([
                    str(r.file_path),
                    'Success' if r.success else 'Failed',
                    r.document_id or '',
                    r.verification_url or '',
                    f"{r.processing_time:.3f}" if r.processing_time else '',
                    r.error or ''
                ])
    
    def _generate_html_content(
        self,
        result: BatchSigningResult,
        title: str,
        publisher: Optional[str]
    ) -> str:
        """Generate HTML content."""
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Generate file list
        file_rows = []
        for r in result.results:
            if r.success:
                status_badge = '<span class="badge success">✓ Verified</span>'
                row_class = 'success'
            else:
                status_badge = '<span class="badge error">✗ Failed</span>'
                row_class = 'error'
            
            verification_link = ''
            if r.verification_url:
                verification_link = f'<a href="{r.verification_url}" target="_blank" class="verify-link">Verify</a>'
            
            file_rows.append(f'''
                <tr class="{row_class}">
                    <td>{r.file_path.name}</td>
                    <td>{status_badge}</td>
                    <td><code>{r.document_id or 'N/A'}</code></td>
                    <td>{verification_link}</td>
                    <td>{r.processing_time:.3f}s</td>
                </tr>
            ''')
        
        files_html = '\n'.join(file_rows)
        
        # Calculate stats
        success_rate = (result.successful / result.total_files * 100) if result.total_files > 0 else 0
        
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #fafafa;
        }}
        
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .content {{
            padding: 40px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th {{
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #555;
            border-bottom: 2px solid #dee2e6;
        }}
        
        td {{
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        tr.success {{
            background: rgba(40, 167, 69, 0.05);
        }}
        
        tr.error {{
            background: rgba(220, 53, 69, 0.05);
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        
        .badge.success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .badge.error {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .verify-link {{
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }}
        
        .verify-link:hover {{
            text-decoration: underline;
        }}
        
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        
        footer {{
            padding: 20px 40px;
            background: #f8f9fa;
            color: #666;
            text-align: center;
            font-size: 0.9em;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e9ecef;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 10px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }}
        
        @media (max-width: 768px) {{
            .stats {{
                grid-template-columns: 1fr;
            }}
            
            header h1 {{
                font-size: 1.8em;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            table {{
                font-size: 0.9em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{title}</h1>
            {f'<p>{publisher}</p>' if publisher else ''}
            <p>Generated on {timestamp}</p>
        </header>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{result.total_files}</div>
                <div class="stat-label">Total Files</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{result.successful}</div>
                <div class="stat-label">Verified</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{result.failed}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{success_rate:.1f}%</div>
                <div class="stat-label">Success Rate</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {success_rate}%"></div>
                </div>
            </div>
            {('<div class="stat-card"><div class="stat-value">' + str(result.skipped) + '</div><div class="stat-label">Skipped</div></div>') if result.skipped > 0 else ''}
            <div class="stat-card">
                <div class="stat-value">{result.total_time:.2f}s</div>
                <div class="stat-label">Total Time</div>
            </div>
        </div>
        
        <div class="content">
            <h2>Verified Content</h2>
            <p>All content below has been cryptographically signed and can be independently verified.</p>
            
            <table>
                <thead>
                    <tr>
                        <th>File</th>
                        <th>Status</th>
                        <th>Document ID</th>
                        <th>Verification</th>
                        <th>Time</th>
                    </tr>
                </thead>
                <tbody>
                    {files_html}
                </tbody>
            </table>
        </div>
        
        <footer>
            <p>Powered by <strong>Encypher Enterprise SDK</strong></p>
            <p>Content authenticity verified using C2PA standards</p>
        </footer>
    </div>
</body>
</html>'''
        
        return html
    
    def _generate_markdown_content(
        self,
        result: BatchSigningResult,
        title: str
    ) -> str:
        """Generate Markdown content."""
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        
        # Generate file list
        file_rows = []
        for r in result.results:
            status = '✓' if r.success else '✗'
            doc_id = r.document_id or 'N/A'
            verify_link = f"[Verify]({r.verification_url})" if r.verification_url else 'N/A'
            
            file_rows.append(
                f"| {r.file_path.name} | {status} | `{doc_id}` | {verify_link} | {r.processing_time:.3f}s |"
            )
        
        files_md = '\n'.join(file_rows)
        
        # Calculate stats
        success_rate = (result.successful / result.total_files * 100) if result.total_files > 0 else 0
        
        md = f'''# {title}

**Generated:** {timestamp}

## Summary

- **Total Files:** {result.total_files}
- **Verified:** {result.successful}
- **Failed:** {result.failed}
- **Success Rate:** {success_rate:.1f}%
'''
        
        if result.skipped > 0:
            md += f"- **Skipped:** {result.skipped}\n"
        
        md += f"- **Total Time:** {result.total_time:.2f}s\n\n"
        
        md += f'''## Verified Content

All content below has been cryptographically signed and can be independently verified.

| File | Status | Document ID | Verification | Time |
|------|--------|-------------|--------------|------|
{files_md}

---

*Powered by **Encypher Enterprise SDK** - Content authenticity verified using C2PA standards*
'''
        
        return md


def generate_verification_badge(
    document_id: str,
    verification_url: str,
    output_path: Optional[Path] = None
) -> str:
    """
    Generate an SVG verification badge.
    
    Args:
        document_id: Document ID
        verification_url: Verification URL
        output_path: Optional path to save SVG file
    
    Returns:
        SVG content as string
    """
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="180" height="20">
    <linearGradient id="b" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <clipPath id="a">
        <rect width="180" height="20" rx="3" fill="#fff"/>
    </clipPath>
    <g clip-path="url(#a)">
        <path fill="#555" d="M0 0h75v20H0z"/>
        <path fill="#4c1" d="M75 0h105v20H75z"/>
        <path fill="url(#b)" d="M0 0h180v20H0z"/>
    </g>
    <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
        <text x="37.5" y="15" fill="#010101" fill-opacity=".3">Encypher</text>
        <text x="37.5" y="14">Encypher</text>
        <text x="127.5" y="15" fill="#010101" fill-opacity=".3">Verified</text>
        <text x="127.5" y="14">Verified</text>
    </g>
    <a href="{verification_url}" target="_blank">
        <rect width="180" height="20" fill="transparent"/>
    </a>
</svg>'''
    
    if output_path:
        output_path.write_text(svg, encoding='utf-8')
    
    return svg
