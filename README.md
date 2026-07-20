# Resume Tailor

An AI-powered desktop application that automatically tailors your resume and cover letter for specific job applications using OpenAI or Anthropic (Claude) models.

## Overview

Resume Tailor analyzes job descriptions and intelligently customizes your resume by:
- Emphasizing relevant skills and experience that match the job requirements
- Using terminology and keywords from the job posting
- Maintaining authenticity while optimizing for Applicant Tracking Systems (ATS)
- Generating tailored cover letters
- Rating job/resume match and job quality before you commit to generating documents
- Tracking application history with match ratings and job quality metrics
- Automatically converting documents to PDF format

The application uses a PySide6 GUI to collect job information and leverages the OpenAI or Anthropic API (depending on the model selected) to generate customized resumes from your base resume templates.

## Features

- **AI-Powered Tailoring**: Uses GPT or Claude models to analyze job descriptions and customize resumes
- **Multi-Provider Support**: Switch between OpenAI and Anthropic models from the Settings page — no code changes needed
- **Match & Quality Rating**: Check a job's match rating and job quality score before generating a full tailored resume
- **Save Submission Mode**: Log an application (with an optional application link) without generating documents
- **Multi-Format Output**: Generates both .docx and PDF versions of resumes and cover letters
- **Application Tracking**: History page with filtering by match rating, job quality, date range, and tech stack
- **Favorites System**: Mark and filter favorite applications for quick access
- **Archive Management**: Dedicated archive page to organize and review old applications
- **Permanent Delete**: Remove history items you don't want to keep, even archived ones
- **Audio Notifications**: Sound alert when document generation completes
- **Document Regeneration**: Regenerate resume and cover letter from any saved application

## Prerequisites

- Python 3.8 or higher
- Windows OS (for batch scripts and PDF conversion)
- An API key for at least one provider:
  - OpenAI API key ([Get one here](https://platform.openai.com/api-keys)), and/or
  - Anthropic API key ([Get one here](https://console.anthropic.com/settings/keys))
- Microsoft Word or compatible .docx editor (for template creation)

## Setup Instructions

### 1. Install Dependencies

**Option A: Using the install script (Windows)**
```bash
install.bat
```

**Option B: Manual installation**
```bash
pip install -r requirements.txt
```

This installs:
- `openai` - OpenAI API client
- `anthropic` - Anthropic (Claude) API client
- `python-dotenv` - Environment variable management
- `python-docx` - Word document processing
- `docx2pdf` - PDF conversion
- `PySide6` - GUI framework
- `pygame` - Audio notifications
- `icecream` - Debugging utility

### 2. Configure API Key(s)

Create a `.env` file in the project root directory. Add the key(s) for whichever provider(s) you plan to use:

```
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

You only need the key for the provider matching your selected model in Settings (see [Changing the AI Model](#changing-the-ai-model)), but you can set both to switch freely.

**Important**: Never commit the `.env` file to version control. It's already in `.gitignore`.

### 3. Prepare Your Base Resumes

The `BaseResumes/` folder should contain your source resume(s) in .docx format. These are the resumes the AI will use as a foundation for tailoring.

**What to include:**
- One or more .docx files with your complete work history, skills, and projects
- Include ALL your experience, skills, and accomplishments (the AI will select the most relevant ones)
- Multiple versions are fine (e.g., technical resume, management resume)
- Use clear, detailed bullet points with metrics and specific technologies

**Example structure:**
```
BaseResumes/
├── Resume2025_Technical.docx
├── Resume2025_Management.docx
└── Resume2025_General.docx
```

**Tips:**
- Don't worry about tailoring or length in base resumes - include everything
- Use specific numbers and metrics (e.g., "Reduced load time by 40%")
- List all technologies, frameworks, and tools you've used
- Include all projects, even if some won't fit on the final resume

### 4. Set Up Resume Template

The `Resources/Resume Template.docx` file defines the formatting and layout of your tailored resumes.

**Required placeholders** (surround with curly braces):

```
{Summary}                          - Professional summary (2-3 lines)

{Job1Title}                        - First job position and company
{J1Details1}, {J1Details2}...      - Job 1 bullet points (up to 6)

{Job2Title}                        - Second job position and company
{J2Details1}, {J2Details2}...      - Job 2 bullet points (up to 3)

{TechnicalSkillsCategory1}         - First skill category name
{TechnicalSkillsCategory1List}     - Skills list for category 1

{TechnicalSkillsCategory2}         - Second skill category name
{TechnicalSkillsCategory2List}     - Skills list for category 2

{TechnicalSkillsCategory3}         - Third skill category name
{TechnicalSkillsCategory3List}     - Skills list for category 3

{Certifications}                   - Professional certifications

{PersonalProject1}                 - First project name and tech stack
{P1Details1}, {P1Details2}         - Project 1 bullet points

{PersonalProject2}                 - Second project name and tech stack
{P2Details1}, {P2Details2}         - Project 2 bullet points
```

**Formatting tips:**
- Keep formatting simple and ATS-friendly (avoid tables, columns, graphics)
- Use standard fonts (Arial, Calibri, Times New Roman)
- Maintain consistent spacing and alignment
- Target one-page layout (32 usable lines)

**Example layout:**
```
{Summary}

PROFESSIONAL EXPERIENCE
{Job1Title}
• {J1Details1}
• {J1Details2}
• {J1Details3}

{Job2Title}
• {J2Details1}
• {J2Details2}

TECHNICAL SKILLS
{TechnicalSkillsCategory1}: {TechnicalSkillsCategory1List}
{TechnicalSkillsCategory2}: {TechnicalSkillsCategory2List}

PROJECTS
{PersonalProject1}
• {P1Details1}
• {P1Details2}
```

### 5. Set Up Cover Letter Template

The `Resources/Cover Letter Template.docx` file defines your cover letter format.

**Required placeholders:**

```
{Date}           - Letter date
{CompanyName}    - Company name
{Paragraph1}     - Opening paragraph
{Paragraph2}     - Body paragraph 1
{Paragraph3}     - Body paragraph 2/closing
```

**Example layout:**
```
{Date}

Hiring Manager
{CompanyName}

Dear Hiring Manager,

{Paragraph1}

{Paragraph2}

{Paragraph3}

Sincerely,
[Your Name]
```

### 6. Configure JSON Template (Optional)

The `Resources/Json Template.json` file defines the structure of AI responses. The default template is pre-configured, but you can customize it.

**Main sections:**

1. **Meta** - File naming and metadata
2. **Resume** - Resume content structure
3. **CoverLetter** - Cover letter structure
4. **Job** - Application tracking metadata

**Key points:**
- Arrays (lists) will be expanded to numbered keys (e.g., `J1Details: [1,2,3]` → `J1Details1`, `J1Details2`, `J1Details3`)
- Character limits are guidelines in comments (e.g., `"Summary": "(240 - 335 Characters)"`)
- Ensure placeholder names match your template .docx files exactly

**Example Resume section:**
```json
"Resume": {
    "File Name": "{Company Name} Resume",
    "Summary": "(240 - 335 Characters)",
    "Job1Title": "{Title} - {Company} | Jan 2023 - Jan 2025",
    "J1Details": [
        "Details1 (~93-210 Characters)",
        "Details2 (~93-210 Characters)",
        "Details3 (~93-210 Characters)"
    ],
    "TechnicalSkillsCategory1": "",
    "TechnicalSkillsCategory1List": ">89 Characters"
}
```

### 7. Add Notification Sound (Optional)

Add an MP3 file named `Notification Sound.mp3` to the `Resources/` folder. This will play when resume generation completes.

If no sound file exists, the application will still work but won't play audio notifications.

## Usage

### Starting the Application

**Option A: Using the run script (Windows)**
```bash
run.bat
```

**Option B: Manual start**
```bash
python Source/Main.py
```

### Generating a Tailored Resume

1. **Enter Job Details** (on the Resume Generation page):
   - **Company Name** (optional): Name of the company
   - **Job Title** (optional): Position title
   - **Job Description** (required): Paste the full job posting
   - **Application Link** (optional): URL of the job posting/application
   - **Save Submission** (optional checkbox): When checked, generation only logs the application to your history — it skips document generation entirely. Useful for tracking applications you're submitting without a freshly tailored resume.

2. **Optional: Click "Check Rating"** to preview fit before generating anything:
   - The AI scores **Match Rating** (how well your experience fits the job) and **Job Quality** (how good the job/company looks), each 1-10 with a short explanation, shown in a popup
   - From the popup you can **Close** (go back and edit inputs) or **Generate Resume** (proceed straight to document generation using the rating you just saw, without asking the AI to re-score it)

3. **Click "Generate"**: The application will:
   - Analyze the job description
   - Select relevant experience from your base resumes
   - Tailor bullet points to match job requirements
   - Compute Match Rating and Job Quality (unless already computed via "Check Rating")
   - Generate both resume and cover letter (skipped if "Save Submission" is checked)
   - Create PDF versions
   - Save everything to the `Results/` folder
   - Play a notification sound

4. **Access Your Documents**:
   - Find generated files in the `Results/` folder
   - Both .docx and .pdf versions are created
   - File names include company and position (e.g., "Google Resume.docx")

### Viewing Application History

Navigate to the **Files** page (🗂️ icon) to:
- View all active (non-archived) applications
- Filter by match rating, job quality, date range, or search term
- See total applications count and today's applications count
- Expand items to view job details, responsibilities, tech stack, and quality ratings
- Mark applications as favorites with the ⭐ button
- Filter to show only favorited applications
- Open the Results folder directly
- Regenerate documents from saved data
- Archive old applications
- Permanently delete applications you no longer want to track (confirmation required, cannot be undone)

**History filters:**
- **Search bar**: Filter by position, company, or tech stack (case-insensitive)
- **Min Rating**: Filter by match rating (1-10)
- **Min Quality**: Filter by job quality assessment (1-10)
- **Date Range**: Filter by Today, Last 3/7/30 Days, or Any day
- **⭐ Favorites**: Show only favorited applications

### Managing Archived Applications

Navigate to the **Archive** page (📦 icon) to:
- View all archived applications
- Use the same filtering capabilities as the Files page
- Expand items to review archived application details
- Regenerate documents from archived data
- Unarchive applications to move them back to the Files page
- Keep your active applications list focused and organized

**Archiving workflow:**
1. On the Files page, expand an application you want to archive
2. Click the 📦 Archive button
3. The application moves to the Archive page
4. To restore, go to Archive page and click the ↩️ Unarchive button

### Configuring Settings

Navigate to the **Settings** page (⚙️ icon) to:
- **Auto Archive Expired Applications**: Toggle automatic archiving of applications past their expected response date
- **Auto Archive Expired Favorite Applications**: When enabled, favorite applications will also be auto-archived after they expire (disabled by default to protect favorites)
- **Select AI Model**: Choose from available OpenAI or Anthropic models (e.g. gpt-5, gpt-5-mini, claude-sonnet-5, claude-opus-4-8)

Settings are saved to `Config.json`. You need a valid API key in `.env` for whichever provider (OpenAI or Anthropic) the selected model belongs to.

## Project Structure

```
.
├── BaseResumes/              # Your source resumes (.docx files)
├── Resources/                # Configuration and templates
│   ├── Json Data/           # Saved application data (JSON)
│   │   └── Archived/        # Archived applications
│   ├── Json Template.json   # AI response structure
│   ├── Resume Template.docx # Resume formatting template
│   ├── Cover Letter Template.docx
│   ├── Resume Prompt.md     # AI instructions for tailoring
│   ├── Match Rating Prompt.md # AI instructions for the match rating score
│   ├── Job Quality Prompt.md  # AI instructions for the job quality score
│   └── Notification Sound.mp3 (optional)
├── Results/                  # Generated resumes and cover letters
├── Temp/                     # Temporary files during generation
├── Source/                   # Python source code
│   ├── Main.py              # GUI application (entry point)
│   ├── Utility.py           # Document processing
│   ├── Agent.py             # OpenAI + Anthropic API integration
│   └── Widgets.py           # Reusable UI components
├── .env                      # API keys (create this)
├── Config.json              # Application settings
├── requirements.txt         # Python dependencies
├── install.bat              # Windows installation script
├── run.bat                  # Windows run script
└── README.md               # This file
```

## Customizing AI Behavior

Edit `Resources/Resume Prompt.md` to modify how the AI tailors resumes:

- **Analysis focus**: What to prioritize in job descriptions
- **Writing style**: Tone and phrasing preferences
- **Format constraints**: Line counts, character limits
- **ATS optimization**: Keyword strategies

The AI follows these instructions when generating each resume. Templates and prompts are reloaded from disk on every "Generate" click, so edits take effect immediately without restarting the app.

Similarly, edit `Resources/Match Rating Prompt.md` and `Resources/Job Quality Prompt.md` to change how the "Check Rating" score and explanation are derived.

## Troubleshooting

### "API key not found" (OpenAI or Anthropic)
- Ensure `.env` file exists in the project root
- Verify `OPENAI_API_KEY=your_key_here` and/or `ANTHROPIC_API_KEY=your_key_here` are set correctly, matching the model selected in Settings
- No spaces around the `=` sign

### "Module not found" errors
- Run `install.bat` or `pip install -r requirements.txt`
- Ensure you're using Python 3.8 or higher

### PDF conversion fails
- Ensure Microsoft Word is installed (required for docx2pdf on Windows)
- Check that .docx files are being created successfully first
- Try manually converting one .docx file to verify Word is accessible

### Templates not updating
- Click "Generate" to reload templates (they're reloaded each time)
- Verify placeholder names match exactly between template .docx and JSON template
- Check for typos in `{PlaceholderNames}` (case-sensitive)

### No notification sound
- Add `Notification Sound.mp3` to the `Resources/` folder
- Ensure the file is a valid MP3 format
- Check volume settings on your computer

### Resume exceeds one page
- Edit `Resources/Resume Prompt.md` to adjust line count constraints
- Reduce the number of bullet points in `Json Template.json` arrays
- Modify character limits in the prompt

## Advanced Configuration

### Changing the AI Model

**Via GUI:**
- Go to Settings page (⚙️)
- Select model from dropdown
- Changes save automatically to `Config.json`

**Via Config.json:**
```json
{
    "Settings": {
        "Auto Archive Expired Applications": true,
        "Auto Archive Expired Favorite Applications": false,
        "Current Model": "claude-sonnet-5"
    }
}
```

Available models are listed in `Config.json` under `Resources.Available Models` and can include both OpenAI (e.g. `gpt-5`, `gpt-5-mini`) and Anthropic (e.g. `claude-sonnet-5`, `claude-opus-4-8`) model names — the app routes each request to the right provider automatically based on the model name. Custom model names must contain `"gpt"` or `"claude"` to route correctly.

### Adding Custom Base Resumes

Simply add more .docx files to the `BaseResumes/` folder. The application will:
- Automatically scan all .docx files in the folder
- Combine content from all resumes
- Use the combined text as context for the AI

This is useful if you have different resume versions for different career paths.

### Using Favorites

Mark important applications as favorites for quick access:

**To mark as favorite:**
1. Go to Files page (🗂️) or Archive page (📦)
2. Expand the application
3. Click the ⭐ button (turns green when favorited)

**To filter favorites:**
1. Check the "⭐ Favorites" checkbox at the top of the page
2. Only favorited applications will be displayed
3. Combine with other filters (search, rating, quality, date)

**Use cases:**
- Track high-priority applications you're actively pursuing
- Mark applications with great match ratings for follow-up
- Highlight companies you're most interested in
- Quickly access applications you want to tailor further

### Archiving Applications

**Manual archiving:**
1. Go to Files page (🗂️)
2. Expand the application you want to archive
3. Click the 📦 Archive button
4. The application is moved to `Resources/Json Data/Archived/`

**Viewing archived applications:**
1. Navigate to the Archive page (📦)
2. View all archived applications with the same filtering options
3. Expand items to review details
4. Click ↩️ Unarchive to restore an application to the Files page

**Benefits of archiving:**
- Keep your active Files page focused on current applications
- Maintain historical records without cluttering the main view
- Easily filter between active and archived applications
- Quickly unarchive if you need to reference or regenerate documents

## Tips for Best Results

1. **Detailed Base Resumes**: Include as much detail as possible in your base resumes. The AI will select what's relevant.

2. **Specific Job Descriptions**: Paste the complete job posting, including requirements, responsibilities, and company info.

3. **Review Generated Content**: Always review the AI-generated resume before submitting. Verify accuracy of all claims.

4. **Iterate on Templates**: Adjust the Resume Prompt.md instructions based on results to improve future generations.

5. **Track Match Ratings**: Use the match rating to prioritize which applications to pursue. The AI calculates this based on tech stack overlap, similar responsibilities, and experience level match.

6. **Use Favorites Strategically**: Mark high-match applications (8+) or companies you're most interested in to easily track your top opportunities.

7. **Archive Old Applications**: Keep your Files page organized by archiving applications after you've heard back or decided not to pursue them.

8. **Leverage Document Regeneration**: If you want to try a different approach, you can regenerate documents from any saved application without re-entering the job description.

9. **Customize Per Application**: The company and job title fields help the AI understand context, even if optional.

10. **Monitor Date Filters**: Use the "Today" filter to quickly see how many applications you've generated each day and maintain application momentum.

## Security Notes

- **Never commit `.env` file**: Your OpenAI/Anthropic API keys should remain private
- **API costs**: Each resume generation (and each "Check Rating" call) makes an API call. Monitor your usage with your provider
- **Local processing**: All document processing happens locally; only text is sent to the OpenAI or Anthropic API, depending on the selected model
- **Data storage**: Application history is stored locally in `Resources/Json Data/`

## License

This project is for personal use. Ensure compliance with OpenAI's and/or Anthropic's usage policies when using their APIs.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Verify all setup steps were completed
3. Review `CLAUDE.md` for technical implementation details
4. Check OpenAI/Anthropic API status if generation fails

---

**Version**: 1.1
**Last Updated**: 2026
