# HTML Conversion Tool

Convert Word-exported HTML files into clean, styled HTML using templates and configuration files.

## 📁 Directory Structure

```
html-conversion-tool/
├── config/                          # Configuration files
│   ├── affiliate-links.json        # Platform affiliate URLs
│   ├── image-urls.json             # Image settings and disclaimers
│   └── platform-metadata.json      # Platform data (names, logos, ratings)
├── templates/                       # Page templates
│   ├── casino-review.html          # Casino review page template
│   ├── sportsbook-review.html      # Sportsbook review page template
│   ├── crypto-comparison.html      # Comparison page template
│   └── components/                 # Reusable components
│       ├── quick-verdict.html      # Quick verdict section
│       ├── pros-cons.html          # Pros and cons grid
│       ├── platform-table-2col.html # 2-column table
│       ├── top10-item.html         # Top 10 list item
│       ├── cta-button.html         # Call-to-action button
│       └── faq-section.html        # FAQ section
├── scripts/                         # Conversion scripts
│   └── convert.py                  # Main conversion script
├── input/                           # Drop Word HTML files here
├── output/                          # Converted files appear here
└── README.md                        # This file
```

## 🚀 Quick Start

### 1. Save Your Word Document as HTML

In Microsoft Word:
1. File → Save As
2. Format: **Web Page (.htm or .html)**
3. Save to the `input/` folder

### 2. Run the Conversion

**Option A: Using Claude Code (Recommended)**
```
Ask me: "convert input/888-casino-review.html"
```

**Option B: Command Line**
```bash
cd scripts
python convert.py ../input/888-casino-review.html
```

**Option C: Specify Output Location**
```bash
python convert.py ../input/888-casino-review.html ../output/my-review.html
```

### 3. Review the Output

The converted file will be in the `output/` folder with:
- ✅ Clean HTML structure
- ✅ Proper CSS classes
- ✅ Affiliate links inserted
- ✅ Accessibility features
- ✅ Platform logos and metadata

## 🎯 What the Converter Does

### Automatic Detection
- **Page Type**: Casino review, sportsbook review, or comparison page
- **Platform**: Identifies which platform (888 Casino, Betfair, etc.)
- **Sections**: Maps Word headings to proper sections

### Content Extraction
- Headings (H1, H2, H3)
- Paragraphs
- Tables (converts to styled 2-column tables)
- Pros and cons lists
- Ratings (extracts "6.9/10" or "5 out of 5")

### HTML Generation
- Inserts affiliate links from `config/affiliate-links.json`
- Applies platform metadata from `config/platform-metadata.json`
- Uses templates from `templates/` folder
- Generates proper star ratings
- Adds accessibility features (ARIA labels, screen reader text)
- Includes disclaimers

## 📝 Configuration Files

### affiliate-links.json
Add or update affiliate URLs:
```json
{
  "888sport": "https://www.theinvestorscentre.co.uk/TIC/888sport",
  "888casino": "https://www.theinvestorscentre.co.uk/TIC/888casino"
}
```

### platform-metadata.json
Add or update platform information:
```json
{
  "888casino": {
    "name": "888 Casino",
    "logo": "888-Casino-Logo.png",
    "rating": "6.9/10",
    "stars_filled": 6,
    "stars_empty": 4,
    "min_deposit": "£10"
  }
}
```

### image-urls.json
Configure image paths, badges, and disclaimers:
```json
{
  "site_settings": {
    "base_url": "https://b3i.tech",
    "image_path": "/wp-content/uploads/2025/11/"
  }
}
```

## 🎨 Templates

### Page Templates
- `casino-review.html` - For casino reviews
- `sportsbook-review.html` - For sportsbook reviews
- `crypto-comparison.html` - For comparison pages

### Component Templates
Reusable HTML snippets:
- `quick-verdict.html` - Featured platform card
- `pros-cons.html` - Two-column pros/cons grid
- `platform-table-2col.html` - Quick facts table
- `top10-item.html` - Ranked list item
- `cta-button.html` - Call-to-action button
- `faq-section.html` - FAQ accordion

## 🔧 Customization

### Adding a New Platform

1. Add affiliate link in `config/affiliate-links.json`:
```json
"newplatform": "https://example.com/affiliate-link"
```

2. Add metadata in `config/platform-metadata.json`:
```json
"newplatform": {
  "name": "New Platform",
  "logo": "newplatform-logo.png",
  "rating": "8/10",
  "stars_filled": 8,
  "stars_empty": 2
}
```

3. The converter will automatically detect and use this data!

### Editing Templates

Templates use `{{placeholder}}` syntax. For example:
```html
<h1>{{title}} <span class="highlight">[{{year}}]</span></h1>
```

Available placeholders:
- `{{title}}` - Page title
- `{{platform_name}}` - Platform name (e.g., "888 Casino")
- `{{year}}` - Current year
- `{{intro_paragraph_1}}` - First paragraph
- `{{pros_cons_grid}}` - Pros/cons HTML
- `{{quick_facts_table}}` - Quick facts table HTML
- `{{cta_button}}` - Call-to-action button HTML

## 📚 Usage with Claude Code

The recommended workflow is to use this tool conversationally with Claude Code:

**Example conversation:**
```
You: "Convert input/888-casino-review.html"
Claude: *runs converter, shows output*

You: "Make the heading bigger"
Claude: *edits template, re-runs*

You: "Add more spacing between sections"
Claude: *updates CSS classes, re-runs*

You: "Looks good! Copy it to my website repo"
Claude: *copies output file and commits*
```

## 🐛 Troubleshooting

### "Platform not detected"
- Add the platform to `config/platform-metadata.json`
- Ensure the platform name appears in the Word document

### "Missing affiliate link"
- Add the platform to `config/affiliate-links.json`

### "Pros/cons not extracted"
- Ensure your Word doc has:
  - Bold text: **Pros:**
  - Followed by a bulleted list
  - Bold text: **Cons:**
  - Followed by a bulleted list

### "Table not converting properly"
- The converter works best with 2-column tables
- Format: Row 1 = headers, Row 2+ = data

## 📦 Requirements

- Python 3.7+ (for running `convert.py`)
- No external Python packages required (uses only standard library)

## 🎓 Examples

See the `examples/` folder (coming soon) for:
- Sample Word documents
- Expected HTML output
- Step-by-step conversion guides

## 📄 License

Internal tool for b3i.tech content production.

## 🤝 Contributing

To add new templates or improve the converter:
1. Edit files in `templates/` or `scripts/`
2. Test with sample documents
3. Commit your changes

## 💡 Tips

1. **Keep Word formatting simple** - The converter works best with basic formatting
2. **Use consistent heading structure** - H1 for title, H2 for sections
3. **Review output** - Always check the converted HTML before publishing
4. **Iterate quickly** - Use Claude Code to make adjustments on the fly
5. **Save your config** - Your affiliate links and platform data are reusable

---

**Ready to start?** Drop a Word HTML file in `input/` and ask Claude to convert it!
