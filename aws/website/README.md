# Daily Office Prayer Generator - Static Website

A simple, dependency-free static website for generating Daily Office prayer PDFs using the AWS Lambda backend.

## Features

- ✅ Zero dependencies - pure HTML, CSS, and JavaScript
- ✅ Responsive design - works on desktop, tablet, and mobile
- ✅ Supports all Lambda API options:
  - Daily and monthly prayer generation
  - All prayer types (Morning, Evening, Midday, Compline)
  - Date/year/month selection
  - Psalm cycle selection (30 or 60 day)
  - Page size (Letter or Remarkable 2 tablet)
  - Cache bypass option
- ✅ Local storage for API endpoint
- ✅ Clear loading states and error handling
- ✅ Automatic PDF download

## Configuration

Before deploying, you must configure the API endpoint:

1. **Edit `index.html`**
2. **Find the configuration section** (around line 363):
   ```javascript
   const API_ENDPOINT = 'https://YOUR_API_ID.execute-api.YOUR_REGION.amazonaws.com/prod/prayer';
   ```
3. **Replace with your actual API Gateway URL** from the CloudFormation stack outputs

## Files

- `index.html` - The complete website (HTML, CSS, and JavaScript in one file)

## Deployment Options

### Option 1: Deploy to AWS S3 (Static Website Hosting)

1. **Create an S3 bucket**:
```bash
BUCKET_NAME="dailyoffice-website"
aws s3 mb s3://$BUCKET_NAME
```

2. **Configure for static website hosting**:
```bash
aws s3 website s3://$BUCKET_NAME \
    --index-document index.html \
    --error-document index.html
```

3. **Set bucket policy for public read**:
```bash
cat > bucket-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::${BUCKET_NAME}/*"
    }
  ]
}
EOF

aws s3api put-bucket-policy \
    --bucket $BUCKET_NAME \
    --policy file://bucket-policy.json
```

4. **Upload the website**:
```bash
cd website
aws s3 sync . s3://$BUCKET_NAME --exclude "README.md"
```

5. **Get the website URL**:
```bash
echo "Website URL: http://${BUCKET_NAME}.s3-website-${AWS_REGION}.amazonaws.com"
```

**Note**: For HTTPS and custom domains, use CloudFront with S3.

### Option 2: Deploy to GitHub Pages

1. **Create a new repository** on GitHub (e.g., `dailyoffice-prayer`)

2. **Clone and add files**:
```bash
git clone https://github.com/YOUR_USERNAME/dailyoffice-prayer.git
cd dailyoffice-prayer
cp /path/to/aws/website/index.html .
git add index.html
git commit -m "Add Daily Office Prayer Generator website"
git push origin main
```

3. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main` / root
   - Click Save

4. **Access your site**:
   - URL: `https://YOUR_USERNAME.github.io/dailyoffice-prayer/`

### Option 3: Deploy to Netlify

1. **Install Netlify CLI** (optional):
```bash
npm install -g netlify-cli
```

2. **Deploy**:
```bash
cd website
netlify deploy --prod
```

Or simply drag and drop the `website` folder to [Netlify Drop](https://app.netlify.com/drop).

### Option 4: Deploy to Vercel

1. **Install Vercel CLI** (optional):
```bash
npm install -g vercel
```

2. **Deploy**:
```bash
cd website
vercel --prod
```

Or use the Vercel web interface to deploy.

## Usage

1. **Open the website** in your browser
2. **Select options**:
   - Choose Daily or Monthly mode
   - Select prayer type
   - Choose date/month
   - Configure page size if needed
3. **Click "Generate Prayer PDF"**
4. **Wait for download** (a few seconds for daily, 1-2 minutes for monthly)

## CORS Configuration

Your API Gateway must have CORS enabled for the website to work. The Lambda functions already include the correct CORS headers:

```javascript
'Access-Control-Allow-Origin': '*'
```

If you want to restrict access to specific domains, update the Lambda handlers to check the `Origin` header.

## Customization

### Change Colors

Edit the CSS in `index.html` around line 16. The main color variables are:

```css
/* Primary gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Primary color */
color: #667eea;
```

### Add Analytics

Add your analytics script before the closing `</body>` tag:

```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### Add Custom Domain (S3 + CloudFront)

1. Create CloudFront distribution pointing to S3 bucket
2. Add custom domain to CloudFront
3. Create Route 53 record pointing to CloudFront
4. Request SSL certificate via ACM

## Browser Compatibility

- ✅ Chrome/Edge 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Troubleshooting

### CORS Errors

If you see CORS errors in the browser console:

1. Verify API Gateway has CORS enabled
2. Check that Lambda functions return the `Access-Control-Allow-Origin` header
3. Try using the `nocache` option to bypass cached responses

### API Endpoint Not Saved

Clear browser cache and local storage, then re-enter the endpoint.

### PDF Not Downloading

1. Check browser console for errors
2. Verify the API endpoint URL is correct
3. Test the API directly using curl:
   ```bash
   curl -v "https://your-api.com/prod/prayer?type=morning"
   ```

### Monthly Generation Times Out

Monthly PDFs can take 1-2 minutes to generate. Be patient and don't refresh the page. If it consistently fails:

1. Check Lambda timeout settings (should be 300s for generator)
2. Check CloudWatch logs for errors
3. Try generating a smaller month (February has fewer days)

## Security Notes

- The website runs entirely in the browser
- No user data is stored or transmitted anywhere except to your API
- API endpoint is stored in browser local storage only
- All communication is over HTTPS (if your API uses HTTPS)

## Development

To test locally:

1. Open `index.html` directly in a browser, or
2. Use a simple HTTP server:
   ```bash
   python3 -m http.server 8000
   # Open http://localhost:8000
   ```

## License

Same as the main Daily Office Prayer Generator project.
