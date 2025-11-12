#!/usr/bin/env python3
"""
Test Documentation Generator

Automatically generates HTML documentation pages from markdown source files.
This script converts test markdown files into styled HTML pages with navigation,
search, and responsive design.

Usage:
    python generate_test_docs.py               # Generate all pages
    python generate_test_docs.py --page test-results  # Generate specific page
    python generate_test_docs.py --help        # Show help

Author: Generated with Claude Code
Date: 2025-11-11
Version: 1.0
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class TestDocsGenerator:
    """Generate HTML documentation from markdown source files."""

    def __init__(self, base_dir: Path = None):
        """Initialize the generator.

        Args:
            base_dir: Base directory containing source markdown files
        """
        self.base_dir = base_dir or Path(__file__).parent
        self.docs_dir = self.base_dir / "test-documentation"

        # Mapping of output HTML files to source markdown files
        self.page_mappings = {
            "test-results": {
                "source": self.base_dir / "test_results.md",
                "output": self.docs_dir / "test-results.html",
                "title": "Test Results",
                "icon": "📄",
                "description": "Comprehensive test results report"
            },
            "recommendations": {
                "source": self.base_dir / "test_recommendations.md",
                "output": self.docs_dir / "recommendations.html",
                "title": "Recommendations",
                "icon": "💡",
                "description": "Improvement recommendations and priorities"
            },
            "test-plan": {
                "source": self.base_dir / "test_plan.md",
                "output": self.docs_dir / "test-plan.html",
                "title": "Test Plan",
                "icon": "📋",
                "description": "Comprehensive testing plan"
            },
            "summary": {
                "source": self.base_dir / "TESTING_SUMMARY.md",
                "output": self.docs_dir / "summary.html",
                "title": "Executive Summary",
                "icon": "📊",
                "description": "Executive summary and overview"
            }
        }

    def read_markdown_file(self, filepath: Path) -> str:
        """Read markdown file contents.

        Args:
            filepath: Path to markdown file

        Returns:
            File contents as string

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not filepath.exists():
            raise FileNotFoundError(f"Markdown file not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def convert_markdown_to_html(self, markdown: str) -> Tuple[List[Dict], str]:
        """Convert markdown to HTML sections.

        This is a simplified converter that handles common markdown patterns.
        For production use, consider using a library like markdown2 or mistune.

        Args:
            markdown: Markdown content

        Returns:
            Tuple of (sections, html_content)
        """
        html_parts = []
        sections = []
        current_section_id = None
        current_section_title = None

        lines = markdown.split('\n')
        in_code_block = False
        in_table = False

        for line in lines:
            # Handle code blocks
            if line.strip().startswith('```'):
                if in_code_block:
                    html_parts.append('</code></pre>')
                    in_code_block = False
                else:
                    html_parts.append('<pre><code>')
                    in_code_block = True
                continue

            if in_code_block:
                html_parts.append(line)
                continue

            # Handle headers
            h1_match = re.match(r'^# (.+)$', line)
            h2_match = re.match(r'^## (.+)$', line)
            h3_match = re.match(r'^### (.+)$', line)
            h4_match = re.match(r'^#### (.+)$', line)

            if h1_match:
                title = h1_match.group(1)
                section_id = self._make_id(title)
                html_parts.append(f'<h1>{self._inline_formatting(title)}</h1>')
                if current_section_id:
                    sections.append({"id": current_section_id, "title": current_section_title})
                current_section_id = section_id
                current_section_title = title
            elif h2_match:
                title = h2_match.group(1)
                section_id = self._make_id(title)
                html_parts.append(f'<h2 id="{section_id}">{self._inline_formatting(title)}</h2>')
                if section_id not in [s["id"] for s in sections]:
                    sections.append({"id": section_id, "title": title})
            elif h3_match:
                title = h3_match.group(1)
                html_parts.append(f'<h3>{self._inline_formatting(title)}</h3>')
            elif h4_match:
                title = h4_match.group(1)
                html_parts.append(f'<h4>{self._inline_formatting(title)}</h4>')
            # Handle table headers
            elif re.match(r'^\|(.+)\|$', line) and not in_table:
                in_table = True
                html_parts.append('<table><thead><tr>')
                cells = [cell.strip() for cell in line.strip('|').split('|')]
                for cell in cells:
                    html_parts.append(f'<th>{self._inline_formatting(cell)}</th>')
                html_parts.append('</tr></thead>')
            # Handle table separator
            elif re.match(r'^\|[-:\s|]+\|$', line) and in_table:
                html_parts.append('<tbody>')
            # Handle table rows
            elif re.match(r'^\|(.+)\|$', line) and in_table:
                html_parts.append('<tr>')
                cells = [cell.strip() for cell in line.strip('|').split('|')]
                for cell in cells:
                    html_parts.append(f'<td>{self._inline_formatting(cell)}</td>')
                html_parts.append('</tr>')
            # Handle end of table
            elif not re.match(r'^\|(.+)\|$', line) and in_table:
                html_parts.append('</tbody></table>')
                in_table = False
                html_parts.append(f'<p>{self._inline_formatting(line)}</p>')
            # Handle unordered lists
            elif re.match(r'^[-*+] (.+)$', line):
                list_match = re.match(r'^[-*+] (.+)$', line)
                if list_match:
                    if not html_parts or not html_parts[-1].startswith('<ul'):
                        html_parts.append('<ul>')
                    html_parts.append(f'<li>{self._inline_formatting(list_match.group(1))}</li>')
            # Handle ordered lists
            elif re.match(r'^\d+\. (.+)$', line):
                list_match = re.match(r'^\d+\. (.+)$', line)
                if list_match:
                    if not html_parts or not html_parts[-1].startswith('<ol'):
                        html_parts.append('<ol>')
                    html_parts.append(f'<li>{self._inline_formatting(list_match.group(1))}</li>')
            # Handle horizontal rules
            elif re.match(r'^---+$', line):
                html_parts.append('<hr>')
            # Handle blockquotes
            elif line.startswith('>'):
                quote_text = line[1:].strip()
                html_parts.append(f'<blockquote>{self._inline_formatting(quote_text)}</blockquote>')
            # Handle empty lines
            elif not line.strip():
                # Close open lists
                if html_parts and html_parts[-1].startswith('<li>'):
                    if '<ul>' in html_parts:
                        html_parts.append('</ul>')
                    elif '<ol>' in html_parts:
                        html_parts.append('</ol>')
                continue
            # Handle paragraphs
            else:
                html_parts.append(f'<p>{self._inline_formatting(line)}</p>')

        # Close any open tags
        if in_code_block:
            html_parts.append('</code></pre>')
        if in_table:
            html_parts.append('</tbody></table>')

        html_content = '\n'.join(html_parts)
        return sections, html_content

    def _make_id(self, text: str) -> str:
        """Convert text to HTML id."""
        # Remove emojis and special chars
        text = re.sub(r'[^\w\s-]', '', text)
        # Convert to lowercase and replace spaces with hyphens
        return text.lower().replace(' ', '-').strip('-')

    def _inline_formatting(self, text: str) -> str:
        """Apply inline markdown formatting (bold, italic, code, links)."""
        # Code blocks
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        # Bold
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        # Italic
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        # Links
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        # Badges (custom pattern)
        text = self._convert_badges(text)
        return text

    def _convert_badges(self, text: str) -> str:
        """Convert badge patterns to HTML badges."""
        badge_map = {
            'HIGH': 'badge-danger',
            'MEDIUM': 'badge-warning',
            'LOW': 'badge-info',
            'PASS': 'badge-success',
            'FAIL': 'badge-danger',
            'SUCCESS': 'badge-success',
            'EXCELLENT': 'badge-success',
            '100%': 'badge-success',
        }

        for keyword, badge_class in badge_map.items():
            # Simple pattern matching for common badge cases
            if keyword in text:
                text = text.replace(f'**{keyword}**', f'<span class="badge {badge_class}">{keyword}</span>')

        return text

    def generate_html_page(self, page_key: str) -> str:
        """Generate complete HTML page from markdown source.

        Args:
            page_key: Key from page_mappings

        Returns:
            Complete HTML page as string
        """
        if page_key not in self.page_mappings:
            raise ValueError(f"Unknown page key: {page_key}")

        page_info = self.page_mappings[page_key]

        # Read markdown source
        markdown_content = self.read_markdown_file(page_info["source"])

        # Convert to HTML
        sections, html_content = self.convert_markdown_to_html(markdown_content)

        # Generate complete HTML page
        html = self._generate_html_template(
            title=page_info["title"],
            icon=page_info["icon"],
            active_page=page_key,
            content=html_content,
            sections=sections
        )

        return html

    def _generate_html_template(self, title: str, icon: str, active_page: str,
                                  content: str, sections: List[Dict]) -> str:
        """Generate complete HTML template with navigation and structure.

        Args:
            title: Page title
            icon: Page icon emoji
            active_page: Current active page key
            content: Main content HTML
            sections: List of sections for TOC

        Returns:
            Complete HTML page
        """
        # Generate navigation links
        nav_links = []
        for key, info in self.page_mappings.items():
            active_class = ' active' if key == active_page else ''
            nav_links.append(
                f'            <li><a href="{key}.html" class="nav-link{active_class}">{info["title"]}</a></li>'
            )
        nav_html = '\n'.join(nav_links)

        # Generate page HTML
        html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Documentation - {title}</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <!-- Navigation -->
    <nav class="nav">
        <a href="index.html" class="nav-logo">
            ✅ Test Documentation
        </a>
        <ul class="nav-links">
            <li><a href="index.html" class="nav-link">Dashboard</a></li>
{nav_html}
        </ul>
        <button id="search-trigger" class="search-trigger">
            🔍 Search (⌘K)
        </button>
    </nav>

    <!-- Layout -->
    <div class="layout">
        <!-- Sidebar TOC -->
        <aside class="sidebar">
            <div class="toc-title">On This Page</div>
            <ul id="toc-list" class="toc-list"></ul>
        </aside>

        <!-- Main Content -->
        <main class="main-content">
            {content}
        </main>
    </div>

    <!-- Search Modal -->
    <div id="search-modal" class="search-modal">
        <div class="search-container">
            <input type="text" id="search-input" class="search-input" placeholder="Search documentation..." />
            <div id="search-results" class="search-results">
                <div class="search-result text-muted">Start typing to search...</div>
            </div>
        </div>
    </div>

    <script src="js/main.js"></script>
</body>
</html>'''

        return html

    def save_html_page(self, page_key: str, html: str) -> None:
        """Save HTML page to file.

        Args:
            page_key: Page key from mappings
            html: HTML content to save
        """
        page_info = self.page_mappings[page_key]
        output_path = page_info["output"]

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write HTML file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"✅ Generated: {output_path}")

    def generate_all(self) -> None:
        """Generate all HTML pages from markdown sources."""
        print("🚀 Generating test documentation HTML pages...")
        print()

        for page_key, page_info in self.page_mappings.items():
            try:
                print(f"📝 Processing: {page_info['title']}")
                print(f"   Source: {page_info['source']}")
                html = self.generate_html_page(page_key)
                self.save_html_page(page_key, html)
                print()
            except Exception as e:
                print(f"❌ Error generating {page_key}: {e}")
                print()

        print("✨ All pages generated successfully!")
        print(f"📂 Output directory: {self.docs_dir}")

    def generate_single(self, page_key: str) -> None:
        """Generate a single HTML page.

        Args:
            page_key: Page key to generate
        """
        if page_key not in self.page_mappings:
            print(f"❌ Error: Unknown page '{page_key}'")
            print(f"   Available pages: {', '.join(self.page_mappings.keys())}")
            return

        page_info = self.page_mappings[page_key]

        try:
            print(f"📝 Generating: {page_info['title']}")
            print(f"   Source: {page_info['source']}")
            html = self.generate_html_page(page_key)
            self.save_html_page(page_key, html)
            print("✅ Done!")
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate test documentation HTML pages from markdown sources",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_test_docs.py                    # Generate all pages
  python generate_test_docs.py --page test-results  # Generate single page
  python generate_test_docs.py --list            # List available pages

Available pages:
  test-results      - Comprehensive test results
  recommendations   - Improvement recommendations
  test-plan         - Testing plan and procedures
  summary           - Executive summary
"""
    )

    parser.add_argument(
        '--page',
        type=str,
        help='Generate a specific page only'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List available pages'
    )

    args = parser.parse_args()

    # Initialize generator
    generator = TestDocsGenerator()

    # List pages if requested
    if args.list:
        print("Available pages:")
        for key, info in generator.page_mappings.items():
            print(f"  {key:20s} - {info['description']}")
        return

    # Generate specific page or all pages
    if args.page:
        generator.generate_single(args.page)
    else:
        generator.generate_all()


if __name__ == "__main__":
    main()
