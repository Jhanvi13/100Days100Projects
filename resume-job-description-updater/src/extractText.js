const path = require("path");
const mammoth = require("mammoth");
const pdfParse = require("pdf-parse");

const SUPPORTED_EXTENSIONS = new Set([".pdf", ".docx", ".txt", ".md", ".rtf"]);

async function extractResumeText(buffer, originalName, mimetype) {
  const ext = path.extname(originalName || "").toLowerCase();

  if (ext === ".pdf" || mimetype === "application/pdf") {
    const { text } = await pdfParse(buffer);
    return normalize(text);
  }

  if (
    ext === ".docx" ||
    mimetype ===
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
  ) {
    const { value } = await mammoth.extractRawText({ buffer });
    return normalize(value);
  }

  if (ext === ".doc") {
    throw new Error(
      "Legacy .doc files aren't supported. Please save/export the resume as .docx or .pdf and try again."
    );
  }

  if (ext === ".txt" || ext === ".md" || ext === ".rtf" || mimetype?.startsWith("text/")) {
    return normalize(buffer.toString("utf-8"));
  }

  throw new Error(
    `Unsupported file type "${ext || mimetype || "unknown"}". Please upload a PDF, DOCX, or TXT resume.`
  );
}

function normalize(text) {
  return text.replace(/\r\n/g, "\n").replace(/[ \t]+\n/g, "\n").trim();
}

module.exports = { extractResumeText, SUPPORTED_EXTENSIONS };
