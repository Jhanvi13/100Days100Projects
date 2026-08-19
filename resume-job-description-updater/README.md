# Resume Tailor

Upload a resume in any common format (PDF, DOCX, or TXT), paste a job description, and get back
a resume tailored to that job — plus a match score, a list of what changed, keywords now
reflected, and an honest list of gaps.

## How it works

1. **Frontend** (`public/`) — a plain HTML/CSS/JS page for uploading a resume file and pasting a
   job description.
2. **Backend** (`src/server.js`) — an Express server that:
   - Extracts text from the uploaded resume (`pdf-parse` for PDF, `mammoth` for DOCX, plain read
     for TXT/MD).
   - Sends the resume text + job description to Claude (`src/tailorResume.js`) with instructions
     to tailor the resume truthfully — no fabricated employers, titles, dates, or metrics.
   - Returns the tailored resume as text, plus a match score, change summary, keywords added, and
     gaps versus the job description.
   - Can also convert the tailored resume into a downloadable `.docx` (`src/buildDocx.js`).

## Setup

```bash
cd resume-job-description-updater
npm install
cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY=sk-ant-...
npm start
```

Then open http://localhost:3000.

## Notes

- Legacy `.doc` files are not supported — export as `.docx` or `.pdf` first.
- Max upload size is 10MB.
- The app never claims skills/experience the original resume doesn't support — the "gaps" section
  in the result surfaces anything the job description asks for that the resume doesn't back up.
