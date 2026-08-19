require("dotenv").config();

const path = require("path");
const express = require("express");
const cors = require("cors");
const multer = require("multer");

const { extractResumeText } = require("./extractText");
const { tailorResume } = require("./tailorResume");
const { buildDocxFromText } = require("./buildDocx");

const app = express();
const PORT = process.env.PORT || 3000;

const upload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB
});

app.use(cors());
app.use(express.json({ limit: "1mb" }));
app.use(express.static(path.join(__dirname, "..", "public")));

app.get("/api/health", (req, res) => {
  res.json({ ok: true, hasApiKey: Boolean(process.env.ANTHROPIC_API_KEY) });
});

app.post("/api/tailor", upload.single("resume"), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: "Please upload a resume file." });
    }

    const jobDescription = (req.body.jobDescription || "").trim();
    if (!jobDescription) {
      return res.status(400).json({ error: "Please paste a job description." });
    }
    if (jobDescription.length < 30) {
      return res
        .status(400)
        .json({ error: "That job description looks too short — please paste the full posting." });
    }

    let resumeText;
    try {
      resumeText = await extractResumeText(req.file.buffer, req.file.originalname, req.file.mimetype);
    } catch (err) {
      return res.status(400).json({ error: err.message });
    }

    if (!resumeText || resumeText.length < 30) {
      return res.status(400).json({
        error: "Couldn't read meaningful text from that file. Try a different format (PDF/DOCX/TXT).",
      });
    }

    if (!process.env.ANTHROPIC_API_KEY) {
      return res.status(500).json({
        error:
          "Server is missing an ANTHROPIC_API_KEY. Set it in your .env file and restart the server.",
      });
    }

    const result = await tailorResume(resumeText, jobDescription);

    res.json({
      originalResumeText: resumeText,
      ...result,
    });
  } catch (err) {
    console.error("Error in /api/tailor:", err);
    res.status(500).json({ error: "Something went wrong while tailoring the resume. Please try again." });
  }
});

app.post("/api/download-docx", express.json({ limit: "1mb" }), async (req, res) => {
  try {
    const { resumeText, filename } = req.body;
    if (!resumeText || typeof resumeText !== "string") {
      return res.status(400).json({ error: "Missing resumeText." });
    }

    const buffer = await buildDocxFromText(resumeText);
    const safeName = (filename || "tailored-resume").replace(/[^a-z0-9-_]/gi, "_");

    res.setHeader(
      "Content-Type",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    );
    res.setHeader("Content-Disposition", `attachment; filename="${safeName}.docx"`);
    res.send(buffer);
  } catch (err) {
    console.error("Error in /api/download-docx:", err);
    res.status(500).json({ error: "Failed to generate the .docx file." });
  }
});

app.use((err, req, res, next) => {
  if (err instanceof multer.MulterError) {
    if (err.code === "LIMIT_FILE_SIZE") {
      return res.status(400).json({ error: "File is too large. Max size is 10MB." });
    }
    return res.status(400).json({ error: err.message });
  }
  next(err);
});

app.listen(PORT, () => {
  console.log(`Resume tailor running at http://localhost:${PORT}`);
  if (!process.env.ANTHROPIC_API_KEY) {
    console.warn("Warning: ANTHROPIC_API_KEY is not set. Requests to /api/tailor will fail until it is.");
  }
});
