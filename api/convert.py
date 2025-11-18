from http.server import BaseHTTPRequestHandler
import json
import os
import sys
from pathlib import Path
import re

# Add parent directory to path to import our conversion module
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from scripts.convert import HTMLConverter


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST requests for HTML conversion"""
        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))

            # Read the request body
            body = self.rfile.read(content_length)

            # Parse multipart/form-data
            boundary = self.headers.get('Content-Type', '').split('boundary=')[-1]

            if not boundary:
                self.send_error_response(400, "No boundary found in Content-Type")
                return

            # Parse form data
            form_data = self.parse_multipart(body, boundary)

            if 'file' not in form_data:
                self.send_error_response(400, "No file uploaded")
                return

            html_content = form_data['file']
            template_type = form_data.get('template_type', 'casino-review')
            platform = form_data.get('platform', '')

            # Check if Anthropic API key is available
            api_key = os.environ.get('ANTHROPIC_API_KEY')

            if api_key and ANTHROPIC_AVAILABLE:
                # Use AI-powered conversion
                converted_html = self.convert_with_ai(
                    html_content,
                    template_type,
                    platform,
                    api_key
                )
            else:
                # Fall back to rule-based conversion
                converted_html = self.convert_with_rules(
                    html_content,
                    template_type,
                    platform
                )

            # Send success response
            self.send_json_response({
                'success': True,
                'html': converted_html,
                'method': 'ai' if (api_key and ANTHROPIC_AVAILABLE) else 'rules'
            })

        except Exception as e:
            self.send_error_response(500, str(e))

    def convert_with_ai(self, html_content, template_type, platform, api_key):
        """Convert HTML using AI (Claude API)"""
        try:
            client = Anthropic(api_key=api_key)

            # Load template
            converter = HTMLConverter(
                config_dir="../config",
                templates_dir="../templates"
            )

            template_path = Path(__file__).parent.parent / "templates" / f"{template_type}.html"
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()

            # Load config
            config_path = Path(__file__).parent.parent / "config"
            with open(config_path / "platform-metadata.json", 'r', encoding='utf-8') as f:
                platform_metadata = json.load(f)

            with open(config_path / "affiliate-links.json", 'r', encoding='utf-8') as f:
                affiliate_links = json.load(f)

            # Create AI prompt
            prompt = f"""You are an expert HTML converter. Convert the following Word-exported HTML into a properly structured web page using the provided template.

INPUT HTML:
{html_content[:5000]}  # Limit to avoid token limits

TEMPLATE TO FILL:
{template[:3000]}

AVAILABLE PLATFORMS:
{json.dumps(list(platform_metadata.keys()))}

AFFILIATE LINKS:
{json.dumps(affiliate_links, indent=2)}

INSTRUCTIONS:
1. Extract all content from the input HTML (headings, paragraphs, tables, lists)
2. Identify the platform being reviewed (or use: {platform if platform else 'auto-detect'})
3. Map content to the template's {{placeholder}} variables
4. Extract pros/cons lists and format them properly
5. Convert tables to 2-column format if needed
6. Generate appropriate section content
7. Include the correct affiliate link for the platform
8. Fill ALL template placeholders with appropriate content
9. Return ONLY the final HTML, no explanations

Return the complete, valid HTML document."""

            # Call Claude API
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Extract HTML from response
            response_text = message.content[0].text

            # Try to extract just the HTML if there's explanatory text
            html_match = re.search(r'<!DOCTYPE html>.*</html>', response_text, re.DOTALL | re.IGNORECASE)
            if html_match:
                return html_match.group(0)

            return response_text

        except Exception as e:
            print(f"AI conversion error: {e}")
            # Fall back to rule-based
            return self.convert_with_rules(html_content, template_type, platform)

    def convert_with_rules(self, html_content, template_type, platform):
        """Convert HTML using existing rule-based converter"""
        # Save temp file
        temp_input = Path('/tmp') / 'input.html'
        temp_output = Path('/tmp') / 'output.html'

        with open(temp_input, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Run converter
        converter = HTMLConverter(
            config_dir=str(Path(__file__).parent.parent / "config"),
            templates_dir=str(Path(__file__).parent.parent / "templates")
        )

        converter.convert(str(temp_input), str(temp_output))

        # Read result
        with open(temp_output, 'r', encoding='utf-8') as f:
            return f.read()

    def parse_multipart(self, body, boundary):
        """Parse multipart form data"""
        boundary = boundary.encode() if isinstance(boundary, str) else boundary
        parts = body.split(b'--' + boundary)
        form_data = {}

        for part in parts:
            if not part or part == b'--\r\n' or part == b'--':
                continue

            # Split headers and content
            if b'\r\n\r\n' in part:
                headers, content = part.split(b'\r\n\r\n', 1)
            else:
                continue

            # Extract field name
            name_match = re.search(rb'name="([^"]+)"', headers)
            if not name_match:
                continue

            field_name = name_match.group(1).decode('utf-8')

            # Remove trailing boundary markers
            content = content.rstrip(b'\r\n')

            # Check if it's a file or regular field
            if b'filename=' in headers:
                # It's a file - decode as text
                try:
                    form_data[field_name] = content.decode('utf-8')
                except:
                    form_data[field_name] = content.decode('utf-8', errors='ignore')
            else:
                # It's a regular field
                form_data[field_name] = content.decode('utf-8')

        return form_data

    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def send_error_response(self, status, message):
        """Send error response"""
        self.send_json_response({
            'success': False,
            'error': message
        }, status)

    def do_OPTIONS(self):
        """Handle OPTIONS for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
