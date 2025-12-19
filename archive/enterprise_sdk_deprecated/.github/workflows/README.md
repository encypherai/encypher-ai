# CI/CD Workflows for Encypher Content Signing

This directory contains GitHub Actions workflows for automatically signing and verifying content in your repository.

## Available Workflows

### 1. Sign Content (`sign-content.yml`)

Automatically signs content when changes are pushed to main/master branches.

**Features:**
- Incremental signing (only signs changed files)
- Git metadata extraction (author, dates, contributors)
- Frontmatter parsing (YAML/TOML/JSON)
- Generates HTML signing report
- Auto-commits signed files

**Triggers:**
- Push to `main` or `master` branch
- Changes in `articles/`, `posts/`, `content/`, or `docs/` directories
- Manual workflow dispatch

### 2. Verify Content (`verify-content.yml`)

Verifies signed content integrity on pull requests and scheduled runs.

**Features:**
- Detects tampered files
- Generates verification report
- Comments on PRs with verification status
- Weekly scheduled verification

**Triggers:**
- Pull requests with signed file changes
- Weekly schedule (Sundays at midnight)
- Manual workflow dispatch

## Setup Instructions

### 1. Add API Key Secret

1. Go to your repository **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `ENCYPHER_API_KEY`
4. Value: Your Encypher API key (get from https://dashboard.encypherai.com)
5. Click **Add secret**

### 2. Enable Workflows

The workflows are automatically enabled when you add them to your repository. To customize:

1. Edit the workflow files in `.github/workflows/`
2. Adjust paths, branches, or options as needed
3. Commit and push changes

### 3. Customize Paths

Edit the `paths` section in `sign-content.yml` to match your content directories:

```yaml
paths:
  - 'articles/**'
  - 'posts/**'
  - 'your-custom-dir/**'
```

### 4. Customize Metadata

Edit the signing command in `sign-content.yml`:

```yaml
- name: Sign content
  run: |
    encypher sign-repo ./articles \
      --author "Your Name" \
      --publisher "Your Organization" \
      --license "CC-BY-4.0" \
      --incremental \
      --use-git-metadata \
      --report signing-report.json
```

## Workflow Options

### Sign Content Options

| Option | Description | Default |
|--------|-------------|---------|
| `--author` | Author name | `${{ github.actor }}` |
| `--publisher` | Publisher name | `${{ github.repository_owner }}` |
| `--license` | Content license | `CC-BY-4.0` |
| `--incremental` | Only sign changed files | Enabled |
| `--use-git-metadata` | Extract metadata from git | Enabled |
| `--use-frontmatter` | Parse YAML/TOML frontmatter | Enabled |
| `--report` | Report file path | `signing-report.json` |
| `--report-format` | Report format (json/html/markdown/csv) | `html` |

### Verify Content Options

| Option | Description | Default |
|--------|-------------|---------|
| `--fail-on-tampered` | Exit with error if tampered | Enabled |
| `--report` | Report file path | `verification-report.json` |
| `--report-format` | Report format | `html` |

## Artifacts

Both workflows upload artifacts that you can download from the Actions tab:

- **signing-report**: HTML report of signed files
- **verification-report**: HTML report of verification results

## Troubleshooting

### Workflow fails with "API key not found"

Make sure you've added the `ENCYPHER_API_KEY` secret to your repository settings.

### Workflow fails with "Permission denied"

The workflow needs write permissions to commit signed files. Check:
1. Repository **Settings** → **Actions** → **General**
2. Under "Workflow permissions", select "Read and write permissions"
3. Save changes

### Signed files not committed

Check the workflow logs for git errors. Common issues:
- Branch protection rules preventing commits
- Insufficient permissions
- Merge conflicts

### Verification fails on valid content

This could indicate:
- API key issues
- Network connectivity problems
- Actual content tampering

Check the verification report artifact for details.

## Advanced Configuration

### Skip CI on Signed Commits

The workflows use `[skip ci]` in commit messages to prevent infinite loops:

```yaml
git commit -m "Sign content [skip ci]"
```

### Custom Signing Patterns

To sign specific file types:

```yaml
- name: Sign content
  run: |
    encypher sign-repo ./articles \
      --pattern "*.md" \
      --pattern "*.txt" \
      --exclude "drafts/**" \
      --incremental
```

### Parallel Signing

For large repositories, use async signing:

```python
# In your custom script
from encypher_enterprise import AsyncEncypherClient, RepositorySigner

async with AsyncEncypherClient(api_key=api_key) as client:
    signer = RepositorySigner(client, max_concurrent=10)
    result = signer.sign_directory(...)
```

## GitLab CI/CD

For GitLab, use the `.gitlab-ci.yml.example` template in the repository root:

```bash
cp .gitlab-ci.yml.example .gitlab-ci.yml
```

Then add `ENCYPHER_API_KEY` as a CI/CD variable in your GitLab project settings.

## Support

For issues or questions:
- SDK Documentation: https://github.com/encypherai/enterprise-sdk
- API Documentation: https://docs.encypherai.com
- Support: sdk@encypherai.com
