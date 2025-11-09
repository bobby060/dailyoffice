# Testing Instructions for API Sample Collection

## Purpose

This script collects sample data from the Daily Office 2019 API so we can continue development without needing direct API access. You'll run this locally where the API works, then send me the collected data.

## Running the Collection Script

### 1. Make sure dependencies are installed

```bash
pip install requests
```

### 2. Run the collection script

```bash
python collect_api_samples.py
```

The script will:
- Fetch data from various API endpoints
- Save responses as JSON files in the `api_samples/` directory
- Print progress and results
- Create a README documenting what was collected

### 3. Review the collected data

Check the `api_samples/` directory structure:

```
api_samples/
├── README.md           # Summary of collected data
├── office/             # Office prayers
│   ├── morning_prayer_2025-11-08.json
│   ├── evening_prayer_2025-11-08.json
│   ├── midday_prayer_2025-11-08.json
│   ├── compline_2025-11-08.json
│   └── ...
├── family/             # Family prayers
│   ├── family_morning_prayer_2025-11-08.json
│   └── ...
├── calendar/           # Calendar data
│   ├── calendar_2025-11-08.json
│   └── ...
└── general/            # General endpoints
    ├── collects.json
    ├── psalms.json
    └── ...
```

### 4. Compress the data

Create a zip file to share:

**On macOS/Linux:**
```bash
zip -r api_samples.zip api_samples/
```

**On Windows:**
```powershell
Compress-Archive -Path api_samples -DestinationPath api_samples.zip
```

### 5. Share the data

You can share the `api_samples.zip` file by:
- Uploading to a file-sharing service (Google Drive, Dropbox, etc.)
- Attaching to an email
- Or simply paste the contents of key files if they're not too large

## What Gets Collected

The script collects samples from these endpoints:

### Office Prayers (Main Focus)
- Morning Prayer (multiple dates)
- Midday Prayer
- Evening Prayer
- Compline

Test dates include:
- Today
- Christmas (2025-12-25)
- Easter (2025-04-20)
- Ash Wednesday (2025-03-05)
- Regular Sunday (2025-11-23)

### Family Prayers
- Family Morning Prayer
- Family Midday Prayer
- Family Early Evening Prayer
- Family Close of Day Prayer

### Calendar Information
- Daily calendar entries
- Monthly calendar view

### Daily Readings
- Scripture readings for each test date

### General Endpoints
- All collects
- Grouped collects
- Collect categories
- Psalm list
- Psalm topics
- Litany
- Available settings
- Individual psalms (1, 23, 51, 119)

## Troubleshooting

### If you get 403 errors
The API might be blocking requests. Try:
1. Running from a different network
2. Adding a delay between requests (modify the script if needed)
3. Running at a different time of day

### If some endpoints fail
That's okay! The script will continue and report what succeeded vs. failed. Even partial data is useful.

### If you get timeout errors
Increase the timeout in the script (line where `timeout=30` appears).

## Expected File Size

The complete collection should be around 5-20 MB depending on how many endpoints succeed.

## Next Steps After Collection

Once you've shared the data with me, I can:
1. Enhance the markdown generator with more formatting details
2. Add support for evening prayer, compline, and other services
3. Implement LaTeX output generation
4. Create comprehensive tests
5. Add more features based on the actual API structure

## Questions?

If you encounter any issues or have questions about the collection process, let me know!
