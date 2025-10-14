# Publishing Guide for Gitlab Review MCP

This guide walks you through publishing your MCP server to PyPI.

Choose your publishing method:
- **[Automated Publishing (Recommended)](#automated-publishing-with-github-actions)** - Publish via GitHub Actions with Trusted Publishing (no API tokens!)
- **[Manual Publishing](#manual-publishing)** - Publish directly from your local machine

---

## Automated Publishing with GitHub Actions (Recommended)

### Prerequisites

1. **GitHub Repository**: Your project must be on GitHub
2. **PyPI Account**: Create an account on [PyPI](https://pypi.org/account/register/)
3. **No API tokens needed!** - Uses Trusted Publishing via OpenID Connect (OIDC)

### Step 1: Configure Trusted Publishing on PyPI

1. Go to [PyPI Publishing Settings](https://pypi.org/manage/account/publishing/)
2. Click **"Add a new pending publisher"**
3. Fill in the form:
   - **PyPI Project Name**: `gitlab-review-mcp`
   - **Owner**: Your GitHub username (e.g., `midodimori`)
   - **Repository name**: `gitlab-review-mcp`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`
4. Click **"Add"**

**Note**: You can configure this **before** your package exists on PyPI. After the first successful publish, it automatically becomes an active publisher.

### Step 2: GitHub Actions Workflow (Already Included)

This template includes `.github/workflows/publish.yml` which:
- ✅ Runs tests on multiple platforms (Ubuntu, macOS, Windows)
- ✅ Builds the package
- ✅ Publishes to PyPI using Trusted Publishing
- ✅ Can be triggered manually or automatically on release

### Step 3: Publishing Workflow

1. **Run the release command**:
   ```bash
   make release
   ```

   This will:
   - Run tests and linting
   - Verify git status is clean
   - Prompt for new version number
   - Update `pyproject.toml`
   - Build the package
   - Create git commit and tag
   - Push to GitHub

2. **Create a GitHub release**:
   - Go to your repository's releases page
   - Click **"Draft a new release"**
   - Select the tag created by `make release` (e.g., `v0.2.0`)
   - Set release title (e.g., `Release v0.2.0`)
   - Add release notes describing changes
   - Click **"Publish release"**

3. **Automated publishing**:
   - GitHub Actions automatically triggers when you publish the release
   - Runs tests on all platforms (Ubuntu, macOS, Windows)
   - Builds the package
   - Publishes to PyPI using Trusted Publishing
   - Check Actions tab to monitor progress

4. **Verify installation**:
   ```bash
   uvx gitlab-review-mcp
   ```

### Advantages of Automated + Trusted Publishing

- ✅ **No API tokens to manage** - Uses short-lived OIDC tokens
- ✅ **More secure** - Tokens expire automatically after use
- ✅ **No secrets to configure** - Just one-time PyPI setup
- ✅ **Multi-platform testing** - Verifies on Ubuntu, macOS, Windows
- ✅ **Consistent build environment**
- ✅ **Publishing tied to GitHub releases**
- ✅ **Audit trail via GitHub Actions logs**

---

## Manual Publishing

### Prerequisites

1. **PyPI Account**: Create an account on [PyPI](https://pypi.org/account/register/)
2. **API Token**: Generate an API token for PyPI
3. **uv**: Install [uv](https://github.com/astral-sh/uv) package manager

### Setting Up API Token

1. Go to [PyPI Account Settings](https://pypi.org/manage/account/)
2. Scroll to "API tokens" section
3. Click "Add API token"
4. Set scope to "Entire account" (or specific project after first publish)
5. Copy the token (starts with `pypi-`)

### Configure uv with Token

Create or edit `~/.config/uv/uv.toml`:

```toml
[publish]
username = "__token__"
password = "pypi-..."
```

Or use environment variables:

```bash
export UV_PUBLISH_USERNAME="__token__"
export UV_PUBLISH_PASSWORD="pypi-..."
```

### Publishing Process

1. **Run the release command**:
   ```bash
   make release
   ```

   This will:
   - Run tests and linting
   - Verify git status is clean
   - Prompt for new version number
   - Update `pyproject.toml`
   - Build the package
   - Create git commit and tag
   - Push to GitHub

2. **Publish to PyPI**:
   ```bash
   make publish
   ```

3. **Verify installation**:
   ```bash
   uvx gitlab-review-mcp
   ```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.1.0): New features, backwards compatible
- **PATCH** (0.0.1): Bug fixes, backwards compatible

Examples:
- Initial development: `0.1.0`
- First stable release: `1.0.0`
- New feature: `1.1.0`
- Bug fix: `1.1.1`
- Breaking change: `2.0.0`

## Troubleshooting

### "File already exists" Error

If you see this error when publishing:

```
HTTPError: 400 Bad Request from https://upload.pypi.org/legacy/
File already exists
```

This means:
1. You're trying to upload the same version again
2. Bump the version in `pyproject.toml`
3. Build and publish again

### Authentication Errors

If authentication fails:

```bash
# Check your configuration
cat ~/.config/uv/uv.toml

# Or set environment variables
export UV_PUBLISH_USERNAME="__token__"
export UV_PUBLISH_PASSWORD="pypi-..."

# Try publishing again
make publish
```

### Build Errors

If the build fails:

```bash
# Clean build artifacts
make clean

# Try building again
make build

# Check for missing dependencies
uv sync --dev
```

## Post-Publishing

After successful publication:

1. **Create GitHub Release**:
   - Go to your repository's releases page
   - Click "Create a new release"
   - Select the version tag
   - Add release notes
   - Attach built artifacts (optional)

2. **Update Documentation**:
   - Update README with new features
   - Update examples if needed
   - Update Claude Desktop configuration examples

3. **Announce**:
   - Tweet about the release
   - Post in relevant communities
   - Update project website/blog

4. **Monitor**:
   - Check PyPI download statistics
   - Monitor GitHub issues
   - Respond to user feedback

## Maintaining Your Package

### Regular Updates

```bash
# Update dependencies
uv sync --upgrade

# Run tests
make test

# Bump version
# Edit pyproject.toml

# Release
make release
make publish
```

### Security Updates

If a security vulnerability is found:

1. Fix the issue immediately
2. Bump the PATCH version
3. Publish quickly: `make release && make publish`
4. Notify users through GitHub security advisories

## Additional Resources

- [PyPI Publishing Guide](https://packaging.python.org/tutorials/packaging-projects/)
- [uv Documentation](https://github.com/astral-sh/uv)
- [Semantic Versioning](https://semver.org/)
- [Python Packaging Guide](https://packaging.python.org/)