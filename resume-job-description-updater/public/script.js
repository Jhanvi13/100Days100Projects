const form = document.getElementById("tailor-form");
const fileInput = document.getElementById("resume-file");
const fileNameEl = document.getElementById("file-name");
const jobDescriptionInput = document.getElementById("job-description");
const submitBtn = document.getElementById("submit-btn");
const errorBox = document.getElementById("error-box");
const loadingEl = document.getElementById("loading");
const resultEl = document.getElementById("result");

const matchScoreEl = document.getElementById("match-score");
const summaryTextEl = document.getElementById("summary-text");
const changesListEl = document.getElementById("changes-list");
const keywordsListEl = document.getElementById("keywords-list");
const gapsWrapEl = document.getElementById("gaps-wrap");
const gapsListEl = document.getElementById("gaps-list");
const tailoredResumeEl = document.getElementById("tailored-resume");

const copyBtn = document.getElementById("copy-btn");
const downloadTxtBtn = document.getElementById("download-txt-btn");
const downloadDocxBtn = document.getElementById("download-docx-btn");

let lastTailoredResume = "";

fileInput.addEventListener("change", () => {
  fileNameEl.textContent = fileInput.files[0] ? fileInput.files[0].name : "";
});

function showError(message) {
  errorBox.textContent = message;
  errorBox.hidden = false;
}

function clearError() {
  errorBox.hidden = true;
  errorBox.textContent = "";
}

function fillList(el, items, emptyMessage) {
  el.innerHTML = "";
  if (!items || items.length === 0) {
    const li = document.createElement("li");
    li.textContent = emptyMessage;
    li.style.opacity = "0.6";
    el.appendChild(li);
    return;
  }
  for (const item of items) {
    const li = document.createElement("li");
    li.textContent = item;
    el.appendChild(li);
  }
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  clearError();
  resultEl.hidden = true;

  const file = fileInput.files[0];
  const jobDescription = jobDescriptionInput.value.trim();

  if (!file) {
    showError("Please choose a resume file.");
    return;
  }
  if (!jobDescription) {
    showError("Please paste a job description.");
    return;
  }

  const formData = new FormData();
  formData.append("resume", file);
  formData.append("jobDescription", jobDescription);

  submitBtn.disabled = true;
  loadingEl.hidden = false;

  try {
    const response = await fetch("/api/tailor", {
      method: "POST",
      body: formData,
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Something went wrong.");
    }

    lastTailoredResume = data.tailoredResume;

    matchScoreEl.textContent = data.matchScore !== null ? `${data.matchScore}%` : "–";
    summaryTextEl.textContent = data.summary || "";
    fillList(changesListEl, data.changes, "No specific changes reported.");
    fillList(keywordsListEl, data.keywordsAdded, "No keywords reported.");

    if (data.gaps && data.gaps.length > 0) {
      gapsWrapEl.hidden = false;
      fillList(gapsListEl, data.gaps, "");
    } else {
      gapsWrapEl.hidden = true;
    }

    tailoredResumeEl.textContent = data.tailoredResume;
    resultEl.hidden = false;
    resultEl.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (err) {
    showError(err.message || "Something went wrong. Please try again.");
  } finally {
    submitBtn.disabled = false;
    loadingEl.hidden = true;
  }
});

copyBtn.addEventListener("click", async () => {
  if (!lastTailoredResume) return;
  try {
    await navigator.clipboard.writeText(lastTailoredResume);
    copyBtn.textContent = "Copied!";
    setTimeout(() => (copyBtn.textContent = "Copy text"), 1500);
  } catch {
    showError("Couldn't copy to clipboard. Select the text manually instead.");
  }
});

downloadTxtBtn.addEventListener("click", () => {
  if (!lastTailoredResume) return;
  const blob = new Blob([lastTailoredResume], { type: "text/plain" });
  triggerDownload(blob, "tailored-resume.txt");
});

downloadDocxBtn.addEventListener("click", async () => {
  if (!lastTailoredResume) return;
  downloadDocxBtn.disabled = true;
  try {
    const response = await fetch("/api/download-docx", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resumeText: lastTailoredResume, filename: "tailored-resume" }),
    });
    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      throw new Error(data.error || "Failed to generate .docx");
    }
    const blob = await response.blob();
    triggerDownload(blob, "tailored-resume.docx");
  } catch (err) {
    showError(err.message || "Failed to generate .docx");
  } finally {
    downloadDocxBtn.disabled = false;
  }
});

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
