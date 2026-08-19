const { Document, Packer, Paragraph, TextRun, HeadingLevel } = require("docx");

const SECTION_HEADER_RE = /^[A-Z0-9][A-Z0-9 &/'-]{2,}$/;

function buildDocxFromText(resumeText) {
  const lines = resumeText.split("\n");
  const children = [];

  for (const rawLine of lines) {
    const line = rawLine.trimEnd();

    if (line.trim() === "") {
      children.push(new Paragraph({ text: "" }));
      continue;
    }

    const isBullet = /^[-*•]\s+/.test(line.trim());
    const isHeader = SECTION_HEADER_RE.test(line.trim()) && line.trim().length < 40;

    if (isHeader) {
      children.push(
        new Paragraph({
          text: line.trim(),
          heading: HeadingLevel.HEADING_2,
          spacing: { before: 200, after: 100 },
        })
      );
    } else if (isBullet) {
      children.push(
        new Paragraph({
          text: line.trim().replace(/^[-*•]\s+/, ""),
          bullet: { level: 0 },
        })
      );
    } else {
      children.push(
        new Paragraph({
          children: [new TextRun(line.trim())],
        })
      );
    }
  }

  const doc = new Document({
    sections: [{ properties: {}, children }],
  });

  return Packer.toBuffer(doc);
}

module.exports = { buildDocxFromText };
