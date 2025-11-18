# Deployment Guide - HTML Conversion Tool

## 🚀 Quick Deploy to Vercel

### Prerequisites
- Vercel account
- Anthropic API key (get one at https://console.anthropic.com)
- Git repository connected to Vercel

### Step 1: Connect Repository to Vercel

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Vercel will auto-detect the configuration

### Step 2: Add Environment Variables

In your Vercel project settings:

1. Go to **Settings** → **Environment Variables**
2. Add the following variable:
   - **Key**: `ANTHROPIC_API_KEY`
   - **Value**: Your Anthropic API key (e.g., `sk-ant-...`)
   - **Environment**: Production, Preview, Development

### Step 3: Deploy

1. Click **Deploy**
2. Wait for deployment to complete
3. Your app will be live at `https://your-project.vercel.app`

## 📝 How It Works

### Web Interface
- Upload Word HTML files via drag-and-drop or file picker
- Select template type (Casino Review, Sportsbook Review, or Crypto Comparison)
- Optionally specify platform or let AI auto-detect
- AI-powered conversion using Claude
- Download converted HTML with proper styling

### API Endpoint

**POST** `/api/convert`

**Form Data:**
- `file`: HTML file content
- `template_type`: Template to use (casino-review, sportsbook-review, crypto-comparison)
- `platform`: Optional platform identifier

**Response:**
```json
{
  "success": true,
  "html": "<converted HTML content>",
  "method": "ai"
}
```

### Conversion Methods

1. **AI-Powered (Primary)**: Uses Claude API to intelligently extract and map content
2. **Rule-Based (Fallback)**: Uses pattern matching if API key is missing

## 🔧 Local Development

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Set Environment Variable
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### Run with Vercel CLI
```bash
npm install -g vercel
vercel dev
```

Visit http://localhost:3000

## 📂 Project Structure

```
html-conversion-tool-export-new/
├── index.html              # Web interface
├── api/
│   └── convert.py         # Serverless function for conversion
├── config/
│   ├── affiliate-links.json
│   ├── image-urls.json
│   └── platform-metadata.json
├── templates/
│   ├── casino-review.html
│   ├── sportsbook-review.html
│   ├── crypto-comparison.html
│   └── components/        # Reusable components
├── scripts/
│   └── convert.py         # Core conversion logic
├── vercel.json            # Vercel configuration
└── requirements.txt       # Python dependencies
```

## 🎨 Adding Your Stylesheet

The templates reference `styling-test-page-fixed.css`. To add it:

1. Create a `public/` directory
2. Add your CSS file: `public/styling-test-page-fixed.css`
3. Vercel will automatically serve it

Or update template references to use your hosted CSS URL.

## 🐛 Troubleshooting

### "API key not found" error
- Make sure `ANTHROPIC_API_KEY` is set in Vercel environment variables
- Redeploy after adding the variable

### "Module not found" error
- Ensure `requirements.txt` includes all dependencies
- Vercel should install them automatically

### Templates not loading
- Check that templates directory is included in deployment
- Vercel includes all files by default

### CORS errors
- The API endpoint includes proper CORS headers
- If issues persist, check Vercel logs

## 📊 Monitoring

View deployment logs in Vercel dashboard:
- **Deployments**: See build and runtime logs
- **Analytics**: Track usage
- **Functions**: Monitor serverless function performance

## 🔒 Security Notes

- API keys are stored securely in Vercel environment variables
- File uploads are processed in memory (not stored)
- Affiliate links use nofollow/noopener for SEO

## 💡 Tips

1. **API Costs**: Claude API calls have costs - monitor usage
2. **File Size**: Large HTML files may hit function timeout limits
3. **Caching**: Vercel caches static files automatically
4. **Custom Domain**: Add in Vercel project settings

## 📞 Support

- Vercel Docs: https://vercel.com/docs
- Anthropic API Docs: https://docs.anthropic.com
- Repository Issues: [Your GitHub issues page]

---

**Ready to deploy!** Push your code and let Vercel handle the rest.
