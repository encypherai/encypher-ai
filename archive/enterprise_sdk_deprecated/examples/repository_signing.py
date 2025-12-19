"""
Example: Sign entire repository with C2PA-compliant metadata.

Demonstrates how publishers can recursively sign all files in a repository
with proper C2PA manifest metadata and optional sentence-level tracking.
"""
import os
from pathlib import Path
from datetime import datetime

from encypher_enterprise import EncypherClient
from encypher_enterprise.batch import RepositorySigner, FileMetadata


def main():
    """Sign all markdown and text files in a repository."""
    
    # Initialize client
    api_key = os.getenv("ENCYPHER_API_KEY")
    if not api_key:
        raise ValueError("ENCYPHER_API_KEY environment variable not set")
    
    client = EncypherClient(api_key=api_key)
    
    # Define repository to sign
    repo_path = Path("./my-articles")  # Change to your repository path
    
    # Define metadata function
    # This function is called for each file to generate C2PA-compliant metadata
    def get_metadata(file_path: Path) -> FileMetadata:
        """
        Generate C2PA metadata for each file.
        
        You can customize this based on your needs:
        - Read metadata from frontmatter (YAML/TOML)
        - Parse filename for metadata
        - Use git history for author/date
        - Apply organization-wide defaults
        """
        return FileMetadata(
            # Core metadata
            title=file_path.stem.replace("-", " ").replace("_", " ").title(),
            author="Jane Doe",  # Could read from git or frontmatter
            created=datetime.fromtimestamp(file_path.stat().st_ctime),
            modified=datetime.fromtimestamp(file_path.stat().st_mtime),
            
            # Publisher metadata
            publisher="Acme News Corp",
            publisher_url="https://acmenews.com",
            license="CC-BY-4.0",
            copyright="© 2025 Acme News Corp",
            
            # Content classification
            category="news",
            tags=["journalism", "verified"],
            language="en",
            
            # AI metadata (if applicable)
            ai_generated=False,  # Set to True if AI-generated
            
            # Custom metadata
            custom={
                "department": "Editorial",
                "editor": "John Smith",
                "version": "1.0"
            }
        )
    
    # Create repository signer
    signer = RepositorySigner(
        client=client,
        use_sentence_tracking=True,  # Enable sentence-level tracking (Enterprise tier)
        max_concurrent=5  # Sign up to 5 files concurrently
    )
    
    print(f"Signing repository: {repo_path}")
    print("This may take a few minutes for large repositories...\n")
    
    # Sign all files in repository
    result = signer.sign_directory(
        directory=repo_path,
        patterns=["*.md", "*.txt", "*.html"],  # File patterns to match
        exclude_patterns=[
            "node_modules/**",
            ".git/**",
            "**/__pycache__/**",
            "**/dist/**",
            "**/build/**"
        ],
        metadata_fn=get_metadata,
        recursive=True,  # Recursively scan subdirectories
        output_dir=None,  # None = save alongside original with .signed suffix
        save_manifest=True  # Save C2PA manifest as .c2pa.json files
    )
    
    # Display results
    print("\n" + "="*60)
    print(result.summary())
    print("="*60 + "\n")
    
    # Show detailed results
    print("Detailed Results:")
    print("-" * 60)
    for r in result.results:
        status = "✓" if r.success else "✗"
        print(f"{status} {r.file_path.name}")
        if r.success:
            print(f"  Document ID: {r.document_id}")
            print(f"  Verification: {r.verification_url}")
            print(f"  Time: {r.processing_time:.2f}s")
        else:
            print(f"  Error: {r.error}")
        print()
    
    # Save JSON report
    report_path = Path("./signing-report.json")
    result.to_json(report_path)
    print(f"\nFull report saved to: {report_path}")
    
    # Example: Access individual results
    successful_files = [r for r in result.results if r.success]
    failed_files = [r for r in result.results if not r.success]
    
    if failed_files:
        print(f"\n⚠️  {len(failed_files)} file(s) failed to sign:")
        for r in failed_files:
            print(f"  - {r.file_path}: {r.error}")


def example_with_frontmatter():
    """
    Example: Read metadata from YAML frontmatter in markdown files.
    
    Assumes files have frontmatter like:
    ---
    title: My Article
    author: Jane Doe
    date: 2025-01-15
    tags: [news, politics]
    ---
    """
    import yaml
    
    api_key = os.getenv("ENCYPHER_API_KEY")
    client = EncypherClient(api_key=api_key)
    
    def get_metadata_from_frontmatter(file_path: Path) -> FileMetadata:
        """Parse YAML frontmatter for metadata."""
        content = file_path.read_text(encoding='utf-8')
        
        # Extract frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                frontmatter = yaml.safe_load(parts[1])
                
                return FileMetadata(
                    title=frontmatter.get('title'),
                    author=frontmatter.get('author'),
                    created=frontmatter.get('date'),
                    tags=frontmatter.get('tags', []),
                    license=frontmatter.get('license'),
                    category=frontmatter.get('category'),
                    publisher="Acme News Corp",
                    publisher_url="https://acmenews.com"
                )
        
        # Fallback to defaults
        return FileMetadata(
            title=file_path.stem,
            publisher="Acme News Corp"
        )
    
    signer = RepositorySigner(client)
    result = signer.sign_directory(
        directory=Path("./articles"),
        patterns=["*.md"],
        metadata_fn=get_metadata_from_frontmatter
    )
    
    print(result.summary())


def example_with_git_history():
    """
    Example: Use git history for author and date metadata.
    
    Requires gitpython: pip install gitpython
    """
    try:
        from git import Repo
    except ImportError:
        print("gitpython not installed. Run: pip install gitpython")
        return
    
    api_key = os.getenv("ENCYPHER_API_KEY")
    client = EncypherClient(api_key=api_key)
    
    repo = Repo(".")  # Current git repository
    
    def get_metadata_from_git(file_path: Path) -> FileMetadata:
        """Get author and date from git history."""
        try:
            # Get last commit for this file
            commits = list(repo.iter_commits(paths=str(file_path), max_count=1))
            if commits:
                commit = commits[0]
                return FileMetadata(
                    title=file_path.stem,
                    author=commit.author.name,
                    created=datetime.fromtimestamp(commit.authored_date),
                    publisher="Acme News Corp",
                    custom={
                        "git_commit": commit.hexsha,
                        "git_message": commit.message.strip()
                    }
                )
        except Exception as e:
            print(f"Warning: Could not get git history for {file_path}: {e}")
        
        # Fallback
        return FileMetadata(
            title=file_path.stem,
            publisher="Acme News Corp"
        )
    
    signer = RepositorySigner(client)
    result = signer.sign_directory(
        directory=Path("."),
        patterns=["*.md"],
        metadata_fn=get_metadata_from_git
    )
    
    print(result.summary())


def example_async():
    """
    Example: Async repository signing for better performance.
    """
    import asyncio
    from encypher_enterprise import AsyncEncypherClient
    
    async def sign_async():
        api_key = os.getenv("ENCYPHER_API_KEY")
        
        async with AsyncEncypherClient(api_key=api_key) as client:
            signer = RepositorySigner(
                client=client,
                use_sentence_tracking=True,
                max_concurrent=10  # Higher concurrency with async
            )
            
            result = signer.sign_directory(
                directory=Path("./articles"),
                patterns=["*.md", "*.txt"],
                metadata_fn=lambda p: FileMetadata(
                    author="Jane Doe",
                    publisher="Acme News"
                )
            )
            
            print(result.summary())
    
    asyncio.run(sign_async())


if __name__ == "__main__":
    # Run basic example
    main()
    
    # Uncomment to try other examples:
    # example_with_frontmatter()
    # example_with_git_history()
    # example_async()
