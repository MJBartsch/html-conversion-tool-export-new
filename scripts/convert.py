#!/usr/bin/env python3
"""
HTML Conversion Tool
Converts Word-exported HTML files into styled HTML using templates and config.
"""

import re
import json
import os
import sys
from pathlib import Path
from datetime import datetime

class HTMLConverter:
    def __init__(self, config_dir="../config", templates_dir="../templates"):
        """Initialize the converter with config and template directories."""
        self.config_dir = Path(__file__).parent / config_dir
        self.templates_dir = Path(__file__).parent / templates_dir

        # Load configurations
        self.affiliate_links = self.load_json("affiliate-links.json")
        self.platform_metadata = self.load_json("platform-metadata.json")
        self.image_config = self.load_json("image-urls.json")

    def load_json(self, filename):
        """Load a JSON configuration file."""
        filepath = self.config_dir / filename
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file {filename} not found")
            return {}

    def load_template(self, template_name):
        """Load an HTML template file."""
        filepath = self.templates_dir / template_name
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: Template {template_name} not found")
            return ""

    def load_component(self, component_name):
        """Load a component template."""
        filepath = self.templates_dir / "components" / component_name
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: Component {component_name} not found")
            return ""

    def extract_headings(self, html):
        """Extract all headings (h1, h2, h3) from HTML."""
        headings = []

        for level in ['h1', 'h2', 'h3']:
            pattern = f'<{level}[^>]*>(.*?)</{level}>'
            matches = re.finditer(pattern, html, re.IGNORECASE | re.DOTALL)

            for match in matches:
                text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                headings.append({
                    'level': level,
                    'text': text,
                    'position': match.start()
                })

        return sorted(headings, key=lambda x: x['position'])

    def extract_paragraphs(self, html):
        """Extract all paragraphs from HTML."""
        paragraphs = []
        pattern = r'<p[^>]*>(.*?)</p>'
        matches = re.finditer(pattern, html, re.IGNORECASE | re.DOTALL)

        for match in matches:
            text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
            if text and len(text) > 10:  # Only meaningful paragraphs
                paragraphs.append(text)

        return paragraphs

    def extract_tables(self, html):
        """Extract all tables from HTML."""
        tables = []
        table_pattern = r'<table[^>]*>(.*?)</table>'
        table_matches = re.finditer(table_pattern, html, re.IGNORECASE | re.DOTALL)

        for table_match in table_matches:
            table_html = table_match.group(0)
            rows = []

            row_pattern = r'<tr[^>]*>(.*?)</tr>'
            row_matches = re.finditer(row_pattern, table_html, re.IGNORECASE | re.DOTALL)

            for row_match in row_matches:
                cells = []
                cell_pattern = r'<t[dh][^>]*>(.*?)</t[dh]>'
                cell_matches = re.finditer(cell_pattern, row_match.group(1), re.IGNORECASE)

                for cell_match in cell_matches:
                    cell_text = re.sub(r'<[^>]+>', '', cell_match.group(1)).strip()
                    cells.append(cell_text)

                if cells:
                    rows.append(cells)

            if rows:
                tables.append({
                    'rows': rows,
                    'columns': len(rows[0]) if rows else 0,
                    'position': table_match.start()
                })

        return tables

    def extract_pros_cons(self, html):
        """Extract pros and cons lists from HTML."""
        pros = []
        cons = []

        # Look for pros section
        pros_pattern = r'<strong>Pros:?</strong>[\s\S]*?<ul>([\s\S]*?)</ul>'
        pros_match = re.search(pros_pattern, html, re.IGNORECASE)

        if pros_match:
            li_pattern = r'<li>(.*?)</li>'
            li_matches = re.finditer(li_pattern, pros_match.group(1), re.IGNORECASE)
            for li_match in li_matches:
                text = re.sub(r'<[^>]+>', '', li_match.group(1)).strip()
                pros.append(text)

        # Look for cons section
        cons_pattern = r'<strong>Cons:?</strong>[\s\S]*?<ul>([\s\S]*?)</ul>'
        cons_match = re.search(cons_pattern, html, re.IGNORECASE)

        if cons_match:
            li_pattern = r'<li>(.*?)</li>'
            li_matches = re.finditer(li_pattern, cons_match.group(1), re.IGNORECASE)
            for li_match in li_matches:
                text = re.sub(r'<[^>]+>', '', li_match.group(1)).strip()
                cons.append(text)

        return pros, cons

    def detect_platform(self, html):
        """Detect which platform this document is about."""
        html_lower = html.lower()

        # Check against known platforms
        for platform_key, metadata in self.platform_metadata.items():
            platform_name = metadata['name'].lower()
            if platform_name in html_lower or platform_key in html_lower:
                return platform_key

        return None

    def detect_page_type(self, html, headings):
        """Detect the type of page (casino review, sportsbook review, comparison)."""
        html_lower = html.lower()
        heading_text = ' '.join([h['text'].lower() for h in headings])

        # Detection keywords
        if 'casino' in html_lower and 'review' in html_lower:
            return 'casino-review'
        elif 'sportsbook' in html_lower or 'betting' in html_lower and 'review' in heading_text:
            return 'sportsbook-review'
        elif 'best' in heading_text and ('crypto' in html_lower or 'comparison' in html_lower):
            return 'crypto-comparison'

        return 'casino-review'  # Default

    def extract_rating(self, html):
        """Extract rating from text like '6.9/10' or '5 out of 5'."""
        patterns = [
            r'(\d+(?:\.\d+)?)\s*\/\s*(\d+)',
            r'(\d+(?:\.\d+)?)\s+out of\s+(\d+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                return {
                    'rating_num': float(match.group(1)),
                    'rating_total': int(match.group(2))
                }

        return None

    def generate_stars(self, rating_num, rating_total):
        """Generate star HTML for a rating."""
        filled = int(rating_num)
        empty = rating_total - filled

        stars_html = ''
        for _ in range(filled):
            stars_html += '<span class="star" aria-hidden="true">★</span>'
        for _ in range(empty):
            stars_html += '<span class="star empty" aria-hidden="true">☆</span>'

        return stars_html

    def build_pros_cons_html(self, pros, cons):
        """Build the pros/cons grid HTML."""
        template = self.load_component("pros-cons.html")

        pros_items = '\n            '.join([f'<li>{pro}</li>' for pro in pros])
        cons_items = '\n            '.join([f'<li>{con}</li>' for con in cons])

        return template.replace('{{pros_items}}', pros_items).replace('{{cons_items}}', cons_items)

    def build_table_html(self, table_data):
        """Build a 2-column table HTML."""
        template = self.load_component("platform-table-2col.html")

        rows_html = []
        for row in table_data['rows']:
            if len(row) >= 2:
                # Check if value should be highlighted
                is_highlighted = '<strong>' in str(row[1]) or 'free' in str(row[1]).lower()
                highlight_class = ' class="highlight"' if is_highlighted else ''

                row_html = f'''            <tr>
                <td>{row[0]}</td>
                <td{highlight_class}>{row[1]}</td>
            </tr>'''
                rows_html.append(row_html)

        table_rows = '\n'.join(rows_html)

        return (template
                .replace('{{table_caption}}', 'Quick Facts')
                .replace('{{col1_header}}', 'Attribute')
                .replace('{{col2_header}}', 'Details')
                .replace('{{table_rows}}', table_rows))

    def build_cta_button(self, platform_key):
        """Build a CTA button for the platform."""
        if platform_key not in self.affiliate_links:
            return ""

        template = self.load_component("cta-button.html")
        metadata = self.platform_metadata.get(platform_key, {})
        platform_name = metadata.get('name', platform_key.title())

        return (template
                .replace('{{cta_url}}', self.affiliate_links[platform_key])
                .replace('{{cta_text}}', f'Visit {platform_name}')
                .replace('{{aria_label}}', f'Visit {platform_name} website (opens in new window)')
                .replace('{{cta_note}}', '18+ Only • BeGambleAware.org • T&Cs Apply'))

    def render_template(self, template_html, data):
        """Replace all {{placeholders}} in template with data."""
        result = template_html
        for key, value in data.items():
            placeholder = f'{{{{{key}}}}}'
            result = result.replace(placeholder, str(value))

        # Remove any remaining unfilled placeholders
        result = re.sub(r'\{\{[^}]+\}\}', '', result)

        return result

    def convert(self, input_file, output_file=None):
        """Convert a Word HTML file to styled HTML."""
        print(f"Converting: {input_file}")

        # Read input file
        with open(input_file, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Extract content
        headings = self.extract_headings(html_content)
        paragraphs = self.extract_paragraphs(html_content)
        tables = self.extract_tables(html_content)
        pros, cons = self.extract_pros_cons(html_content)

        # Detect page type and platform
        page_type = self.detect_page_type(html_content, headings)
        platform_key = self.detect_platform(html_content)
        rating = self.extract_rating(html_content)

        print(f"  Page type: {page_type}")
        print(f"  Platform: {platform_key}")
        print(f"  Headings: {len(headings)}")
        print(f"  Paragraphs: {len(paragraphs)}")
        print(f"  Tables: {len(tables)}")
        print(f"  Pros: {len(pros)}, Cons: {len(cons)}")

        # Load appropriate template
        template = self.load_template(f"{page_type}.html")

        # Get platform metadata
        platform_metadata = self.platform_metadata.get(platform_key, {}) if platform_key else {}
        platform_name = platform_metadata.get('name', 'Platform')

        # Get title
        h1 = next((h for h in headings if h['level'] == 'h1'), None)
        title = h1['text'] if h1 else f"{platform_name} Review"

        # Build components
        pros_cons_html = self.build_pros_cons_html(pros, cons) if pros or cons else '<p>Coming soon...</p>'
        quick_facts_html = self.build_table_html(tables[0]) if tables and tables[0]['columns'] == 2 else '<p>Coming soon...</p>'
        cta_button_html = self.build_cta_button(platform_key) if platform_key else ''

        # Prepare template data
        template_data = {
            'title': title,
            'meta_description': paragraphs[0][:155] if paragraphs else '',
            'year': datetime.now().year,
            'platform_name': platform_name,
            'intro_paragraph_1': paragraphs[0] if len(paragraphs) > 0 else '',
            'intro_paragraph_2': paragraphs[1] if len(paragraphs) > 1 else '',
            'pros_cons_grid': pros_cons_html,
            'quick_facts_table': quick_facts_html,
            'cta_button': cta_button_html,
            'disclaimer': self.image_config.get('disclaimers', {}).get('gambling_warning', ''),
            # Placeholder sections
            'quick_verdict_section': '<!-- Quick verdict coming soon -->',
            'bonuses_content': '<p>Content coming soon...</p>',
            'games_content': '<p>Content coming soon...</p>',
            'payment_methods_content': '<p>Content coming soon...</p>',
            'mobile_content': '<p>Content coming soon...</p>',
            'customer_support_content': '<p>Content coming soon...</p>',
            'security_content': '<p>Content coming soon...</p>',
        }

        # Render final HTML
        final_html = self.render_template(template, template_data)

        # Determine output file
        if not output_file:
            input_path = Path(input_file)
            output_file = Path(__file__).parent.parent / "output" / f"{input_path.stem}-converted.html"

        # Ensure output directory exists
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)

        # Write output
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_html)

        print(f"  ✓ Converted successfully to: {output_file}")
        return output_file


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: python convert.py <input_file> [output_file]")
        print("\nExample:")
        print("  python convert.py ../input/888-casino.html")
        print("  python convert.py ../input/888-casino.html ../output/result.html")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    converter = HTMLConverter()
    converter.convert(input_file, output_file)


if __name__ == "__main__":
    main()
