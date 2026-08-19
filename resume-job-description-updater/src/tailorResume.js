const Anthropic = require("@anthropic-ai/sdk");

const client = new Anthropic();
const MODEL = "claude-opus-5";

const SYSTEM_PROMPT = `You are an expert resume writer and career coach. You tailor resumes to specific
job descriptions while staying strictly truthful to the candidate's actual background.

Rules you must follow:
- Never invent employers, job titles, dates, degrees, certifications, or metrics that are not
  present in or reasonably implied by the original resume.
- You may rephrase, reorder, emphasize, and surface relevant existing experience/skills using
  language and keywords drawn from the job description (for ATS matching).
- You may tighten weak bullet points and improve clarity/impact, but must not fabricate outcomes.
- Keep the tailored resume in the same overall structure/sections as the original where sensible
  (e.g. Summary, Experience, Skills, Education), unless the original has no clear structure, in
  which case impose a clean standard resume structure.
- Output must be plain text using simple section headers in ALL CAPS and "- " for bullet points,
  suitable for copy/paste or conversion to a document. Do not use markdown symbols like # or **.

Respond with ONLY a single JSON object (no markdown code fences, no extra prose) matching this
exact shape:
{
  "tailoredResume": string,       // the full tailored resume as plain text
  "matchScore": number,           // 0-100 estimate of how well the ORIGINAL resume matched the JD before tailoring
  "summary": string,              // 2-4 sentence summary of the overall approach taken
  "changes": string[],            // bullet list of concrete changes made (5-10 items)
  "keywordsAdded": string[],      // important JD keywords/skills now reflected in the tailored resume
  "gaps": string[]                // JD requirements the candidate's resume does not support; be honest, do not paper over these
}`;

function buildUserPrompt(resumeText, jobDescription) {
  return `Here is the candidate's original resume:

<resume>
${resumeText}
</resume>

Here is the target job description:

<job_description>
${jobDescription}
</job_description>

Tailor the resume to this job description following your system instructions. Respond with only
the JSON object described in your instructions.`;
}

function extractJson(rawText) {
  let text = rawText.trim();
  const fenceMatch = text.match(/```(?:json)?\s*([\s\S]*?)```/i);
  if (fenceMatch) text = fenceMatch[1].trim();

  const firstBrace = text.indexOf("{");
  const lastBrace = text.lastIndexOf("}");
  if (firstBrace === -1 || lastBrace === -1 || lastBrace < firstBrace) {
    throw new Error("Model response did not contain a JSON object.");
  }
  const jsonSlice = text.slice(firstBrace, lastBrace + 1);
  return JSON.parse(jsonSlice);
}

async function tailorResume(resumeText, jobDescription) {
  const response = await client.messages.create({
    model: MODEL,
    max_tokens: 8000,
    system: SYSTEM_PROMPT,
    messages: [{ role: "user", content: buildUserPrompt(resumeText, jobDescription) }],
  });

  const textBlock = response.content.find((block) => block.type === "text");
  if (!textBlock) {
    throw new Error("Model returned no text content.");
  }

  const parsed = extractJson(textBlock.text);

  if (!parsed.tailoredResume || typeof parsed.tailoredResume !== "string") {
    throw new Error("Model response was missing the tailored resume text.");
  }

  return {
    tailoredResume: parsed.tailoredResume,
    matchScore: typeof parsed.matchScore === "number" ? parsed.matchScore : null,
    summary: parsed.summary || "",
    changes: Array.isArray(parsed.changes) ? parsed.changes : [],
    keywordsAdded: Array.isArray(parsed.keywordsAdded) ? parsed.keywordsAdded : [],
    gaps: Array.isArray(parsed.gaps) ? parsed.gaps : [],
  };
}

module.exports = { tailorResume };
