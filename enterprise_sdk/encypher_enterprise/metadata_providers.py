"""
Metadata providers for extracting file metadata from various sources.

Includes providers for:
- Git history
- YAML/TOML/JSON frontmatter
- File system metadata
"""
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime
import re

from .batch import FileMetadata


class GitMetadataProvider:
    """
    Extract metadata from git history.
    
    Requires gitpython: uv add gitpython
    
    Example:
        >>> from encypher_enterprise import RepositorySigner, GitMetadataProvider
        >>> 
        >>> provider = GitMetadataProvider()
        >>> signer = RepositorySigner(client)
        >>> result = signer.sign_directory(
        ...     directory=Path("."),
        ...     metadata_fn=provider.get_metadata
        ... )
    """
    
    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize git metadata provider.
        
        Args:
            repo_path: Path to git repository (default: current directory)
        """
        try:
            from git import Repo, InvalidGitRepositoryError
            self.Repo = Repo
            self.InvalidGitRepositoryError = InvalidGitRepositoryError
        except ImportError:
            raise ImportError(
                "gitpython is required for GitMetadataProvider. "
                "Install with: uv add gitpython"
            )
        
        self.repo_path = repo_path or Path(".")
        try:
            self.repo = self.Repo(self.repo_path, search_parent_directories=True)
        except self.InvalidGitRepositoryError:
            self.repo = None
    
    def get_metadata(self, file_path: Path) -> FileMetadata:
        """
        Get metadata for a file from git history.
        
        Args:
            file_path: Path to file
        
        Returns:
            FileMetadata with git-extracted information
        """
        if not self.repo:
            # Not a git repository, return basic metadata
            return FileMetadata(
                title=file_path.stem,
                created=datetime.fromtimestamp(file_path.stat().st_ctime),
                modified=datetime.fromtimestamp(file_path.stat().st_mtime)
            )
        
        try:
            # Get relative path from repo root
            rel_path = file_path.relative_to(self.repo.working_dir)
            
            # Get first commit (creation)
            first_commit = None
            last_commit = None
            contributors = set()
            
            for commit in self.repo.iter_commits(paths=str(rel_path)):
                last_commit = commit
                contributors.add(commit.author.name)
                first_commit = commit  # Will be the oldest
            
            if not first_commit:
                # File not in git history yet
                return FileMetadata(
                    title=file_path.stem,
                    created=datetime.fromtimestamp(file_path.stat().st_ctime),
                    modified=datetime.fromtimestamp(file_path.stat().st_mtime)
                )
            
            return FileMetadata(
                title=file_path.stem,
                author=last_commit.author.name,
                created=datetime.fromtimestamp(first_commit.authored_date),
                modified=datetime.fromtimestamp(last_commit.authored_date),
                custom={
                    "git_commit": last_commit.hexsha,
                    "git_branch": self.repo.active_branch.name if not self.repo.head.is_detached else "detached",
                    "git_contributors": list(contributors),
                    "git_first_commit": first_commit.hexsha,
                    "git_commit_count": sum(1 for _ in self.repo.iter_commits(paths=str(rel_path)))
                }
            )
        
        except Exception as e:
            # Fallback to file system metadata
            return FileMetadata(
                title=file_path.stem,
                created=datetime.fromtimestamp(file_path.stat().st_ctime),
                modified=datetime.fromtimestamp(file_path.stat().st_mtime),
                custom={"git_error": str(e)}
            )


class FrontmatterMetadataProvider:
    """
    Extract metadata from YAML/TOML/JSON frontmatter.
    
    Supports formats used by:
    - Hugo (YAML/TOML)
    - Jekyll (YAML)
    - Next.js (YAML/JSON)
    - Astro (YAML/TOML)
    
    Example:
        >>> provider = FrontmatterMetadataProvider()
        >>> metadata = provider.get_metadata(Path("article.md"))
    """
    
    def __init__(
        self,
        field_mapping: Optional[Dict[str, str]] = None,
        fallback_author: Optional[str] = None,
        fallback_publisher: Optional[str] = None
    ):
        """
        Initialize frontmatter metadata provider.
        
        Args:
            field_mapping: Custom field name mappings (e.g., {"author": "writer"})
            fallback_author: Default author if not in frontmatter
            fallback_publisher: Default publisher if not in frontmatter
        """
        self.field_mapping = field_mapping or {}
        self.fallback_author = fallback_author
        self.fallback_publisher = fallback_publisher
        
        # Try to import parsers
        self.yaml = None
        self.toml = None
        self.json = None
        
        try:
            import yaml
            self.yaml = yaml
        except ImportError:
            pass
        
        try:
            import tomllib  # Python 3.11+
            self.toml = tomllib
        except ImportError:
            try:
                import toml
                self.toml = toml
            except ImportError:
                pass
        
        try:
            import json
            self.json = json
        except ImportError:
            pass
    
    def get_metadata(self, file_path: Path) -> FileMetadata:
        """
        Get metadata from file frontmatter.
        
        Args:
            file_path: Path to file
        
        Returns:
            FileMetadata with frontmatter-extracted information
        """
        try:
            content = file_path.read_text(encoding='utf-8')
        except Exception:
            return self._fallback_metadata(file_path)
        
        # Try to parse frontmatter
        frontmatter = self._parse_frontmatter(content)
        
        if not frontmatter:
            return self._fallback_metadata(file_path)
        
        # Map fields
        return self._frontmatter_to_metadata(frontmatter, file_path)
    
    def _parse_frontmatter(self, content: str) -> Optional[Dict[str, Any]]:
        """Parse frontmatter from content."""
        # YAML frontmatter (---)
        if content.startswith('---\n') or content.startswith('---\r\n'):
            if not self.yaml:
                return None
            
            parts = re.split(r'^---\s*$', content, maxsplit=2, flags=re.MULTILINE)
            if len(parts) >= 3:
                try:
                    return self.yaml.safe_load(parts[1])
                except Exception:
                    pass
        
        # TOML frontmatter (+++  )
        if content.startswith('+++\n') or content.startswith('+++\r\n'):
            if not self.toml:
                return None
            
            parts = re.split(r'^\+\+\+\s*$', content, maxsplit=2, flags=re.MULTILINE)
            if len(parts) >= 3:
                try:
                    if hasattr(self.toml, 'loads'):
                        return self.toml.loads(parts[1])
                    else:
                        return self.toml.load(parts[1])
                except Exception:
                    pass
        
        # JSON frontmatter ({)
        if content.strip().startswith('{'):
            if not self.json:
                return None
            
            # Find end of JSON object
            brace_count = 0
            end_pos = 0
            for i, char in enumerate(content):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = i + 1
                        break
            
            if end_pos > 0:
                try:
                    return self.json.loads(content[:end_pos])
                except Exception:
                    pass
        
        return None
    
    def _frontmatter_to_metadata(
        self,
        frontmatter: Dict[str, Any],
        file_path: Path
    ) -> FileMetadata:
        """Convert frontmatter dict to FileMetadata."""
        # Apply field mapping
        mapped = {}
        for key, value in frontmatter.items():
            mapped_key = self.field_mapping.get(key, key)
            mapped[mapped_key] = value
        
        # Extract common fields
        title = mapped.get('title', file_path.stem)
        author = mapped.get('author', self.fallback_author)
        
        # Handle date fields
        created = self._parse_date(mapped.get('date') or mapped.get('created'))
        modified = self._parse_date(mapped.get('modified') or mapped.get('updated'))
        
        # Handle tags/categories
        tags = mapped.get('tags', [])
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',')]
        
        category = mapped.get('category')
        
        return FileMetadata(
            title=title,
            author=author,
            created=created,
            modified=modified,
            publisher=mapped.get('publisher', self.fallback_publisher),
            license=mapped.get('license'),
            copyright=mapped.get('copyright'),
            category=category,
            tags=tags,
            language=mapped.get('language', 'en'),
            ai_generated=mapped.get('ai_generated', False),
            ai_model=mapped.get('ai_model'),
            custom={k: v for k, v in mapped.items() if k not in [
                'title', 'author', 'date', 'created', 'modified', 'updated',
                'publisher', 'license', 'copyright', 'category', 'tags',
                'language', 'ai_generated', 'ai_model'
            ]}
        )
    
    def _parse_date(self, date_value: Any) -> Optional[datetime]:
        """Parse date from various formats."""
        if not date_value:
            return None
        
        if isinstance(date_value, datetime):
            return date_value
        
        if isinstance(date_value, str):
            # Try common formats
            formats = [
                '%Y-%m-%d',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S',
                '%Y/%m/%d',
                '%d-%m-%Y',
                '%m/%d/%Y',
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_value, fmt)
                except ValueError:
                    continue
        
        return None
    
    def _fallback_metadata(self, file_path: Path) -> FileMetadata:
        """Fallback metadata when frontmatter parsing fails."""
        return FileMetadata(
            title=file_path.stem,
            author=self.fallback_author,
            publisher=self.fallback_publisher,
            created=datetime.fromtimestamp(file_path.stat().st_ctime),
            modified=datetime.fromtimestamp(file_path.stat().st_mtime)
        )


class CombinedMetadataProvider:
    """
    Combine multiple metadata providers with priority.
    
    Example:
        >>> git_provider = GitMetadataProvider()
        >>> frontmatter_provider = FrontmatterMetadataProvider()
        >>> combined = CombinedMetadataProvider([frontmatter_provider, git_provider])
        >>> 
        >>> # Frontmatter takes priority, git fills in gaps
        >>> metadata = combined.get_metadata(Path("article.md"))
    """
    
    def __init__(self, providers: List):
        """
        Initialize combined provider.
        
        Args:
            providers: List of providers in priority order (first = highest priority)
        """
        self.providers = providers
    
    def get_metadata(self, file_path: Path) -> FileMetadata:
        """
        Get metadata from multiple providers.
        
        Merges metadata from all providers, with earlier providers taking priority.
        
        Args:
            file_path: Path to file
        
        Returns:
            FileMetadata merged from all providers
        """
        # Get metadata from all providers
        all_metadata = [p.get_metadata(file_path) for p in self.providers]
        
        # Merge with priority (first provider wins for each field)
        merged = FileMetadata()
        
        for metadata in reversed(all_metadata):
            # Update fields if not None
            if metadata.title:
                merged.title = metadata.title
            if metadata.author:
                merged.author = metadata.author
            if metadata.created:
                merged.created = metadata.created
            if metadata.modified:
                merged.modified = metadata.modified
            if metadata.publisher:
                merged.publisher = metadata.publisher
            if metadata.license:
                merged.license = metadata.license
            if metadata.copyright:
                merged.copyright = metadata.copyright
            if metadata.category:
                merged.category = metadata.category
            if metadata.tags:
                merged.tags = metadata.tags
            if metadata.language:
                merged.language = metadata.language
            if metadata.ai_generated:
                merged.ai_generated = metadata.ai_generated
            if metadata.ai_model:
                merged.ai_model = metadata.ai_model
            
            # Merge custom fields
            merged.custom.update(metadata.custom)
        
        return merged
