.PHONY: help install test lint lint-fix build clean check-release publish-test publish release run format

# Default target
help:
	@echo "🛠️  Gitlab Review MCP Development Commands"
	@echo ""
	@echo "📦 Setup & Dependencies:"
	@echo "  make install          Install dependencies"
	@echo "  make install-dev      Install with dev dependencies"
	@echo ""
	@echo "🧪 Testing & Quality:"
	@echo "  make test            Run tests"
	@echo "  make test-cov        Run tests with coverage"
	@echo "  make lint            Check code style"
	@echo "  make lint-fix        Fix code style issues"
	@echo ""
	@echo "📦 Building & Publishing:"
	@echo "  make build           Build package"
	@echo "  make clean           Clean build artifacts"
	@echo "  make check-release   Check if ready for release"
	@echo "  make publish-test    Publish to Test PyPI"
	@echo "  make publish         Publish to PyPI (production)"
	@echo "  make release         Full release process"
	@echo ""
	@echo "🚀 Development:"
	@echo "  make run             Run the MCP server (stdio)"
	@echo "  make run-http        Run with Streamable HTTP transport"
	@echo "  make run-sse         Run with SSE transport"
	@echo "  make dev-ui          Run FastMCP dev UI with environment variables"
	@echo "  make format          Format and lint code"

# Setup & Dependencies
install:
	uv sync
	@echo "✅ Dependencies installed!"

install-dev:
	uv sync --dev
	@echo "✅ Dev dependencies installed!"

# Testing & Quality
test:
	uv run --with pytest --with pytest-asyncio --with pytest-mock -- pytest tests -v
	@echo "✅ Tests passed!"

test-cov:
	uv run --with pytest --with pytest-asyncio --with pytest-mock --with pytest-cov -- pytest tests --cov=gitlab_review_mcp --cov-report=html --cov-report=term
	@echo "✅ Tests with coverage completed!"

lint:
	@echo "🔍 Checking code style..."
	uv run --with ruff -- ruff check src/ tests/
	uv run --with black -- black --check src/ tests/
	uv run --with mypy -- mypy src/ --ignore-missing-imports
	@echo "✅ Code style checks passed!"

lint-fix:
	@echo "🔧 Fixing code style..."
	uv run --with ruff -- ruff check src/ tests/ --fix
	uv run --with black -- black src tests
	uv run --with isort -- isort src tests --profile black
	@echo "✅ Code formatted and fixed!"

format: lint-fix

# Building & Publishing
build: clean
	@echo "📦 Building package..."
	uv build
	@echo "✅ Package built successfully!"

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	@echo "✅ Cleaned!"

check-release: lint test
	@echo "🔍 Checking if ready for release..."
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "❌ Working directory is not clean. Commit changes first."; \
		git status --short; \
		exit 1; \
	fi
	@if [ "$$(git branch --show-current)" != "main" ]; then \
		echo "❌ Must be on main branch to release. Current: $$(git branch --show-current)"; \
		exit 1; \
	fi
	@echo "✅ Ready for release!"

publish-test: build
	@echo "🚀 Publishing to Test PyPI..."
	uv publish --publish-url https://test.pypi.org/legacy/
	@echo "✅ Published to Test PyPI!"
	@echo "💡 Test installation: pip install -i https://test.pypi.org/simple/ gitlab-review-mcp"

publish: build
	@echo "🚀 Publishing to PyPI..."
	uv publish
	@echo "✅ Published to PyPI!"
	@echo "💡 Install with: uvx gitlab-review-mcp"

release: check-release
	@echo "🚀 Starting release process..."
	@current_version=$$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/'); \
	echo "📋 Current version: $$current_version"; \
	read -p "🔢 Enter new version: " new_version; \
	if [ -z "$$new_version" ]; then \
		echo "❌ Version cannot be empty"; \
		exit 1; \
	fi; \
	sed -i.bak "s/version = \"$$current_version\"/version = \"$$new_version\"/" pyproject.toml && rm pyproject.toml.bak; \
	echo "✅ Updated version to $$new_version"; \
	$(MAKE) test lint; \
	$(MAKE) build; \
	git add pyproject.toml; \
	git add uv.lock; \
	git commit -m "Bump version to $$new_version"; \
	git tag "v$$new_version"; \
	git push origin main; \
	git push origin "v$$new_version"; \
	echo "🎉 Release v$$new_version completed!"; \
	echo "📌 Create GitHub release at: https://github.com/midodimori/gitlab-review-mcp/releases"

# Development
run:
	@echo "🚀 Starting Gitlab Review MCP (stdio)..."
	uv run gitlab-review-mcp

run-http:
	@echo "🚀 Starting Gitlab Review MCP (Streamable HTTP on port 8000)..."
	uv run gitlab-review-mcp --transport streamable-http

run-sse:
	@echo "🚀 Starting Gitlab Review MCP (SSE on port 8000)..."
	uv run gitlab-review-mcp --transport sse

dev-ui:
	@echo "🚀 Starting FastMCP dev UI..."
	@if [ -f .env ]; then \
		set -a && . ./.env && set +a && \
		fastmcp dev src/gitlab_review_mcp/server.py; \
	else \
		echo "⚠️  No .env file found. Copy .env.example to .env and configure your environment variables."; \
		exit 1; \
	fi
# Quick development workflow
dev: install-dev lint-fix lint test
	@echo "🎉 Development setup complete!"