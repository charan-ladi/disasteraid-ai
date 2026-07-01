const resultSection = document.getElementById("resultSection");
const resultJson = document.getElementById("resultJson");
const loading = document.getElementById("loading");
const mockBanner = document.getElementById("mockBanner");

function showLoading(show) {
  loading.classList.toggle("hidden", !show);
}

function renderResult(data) {
  resultSection.classList.remove("hidden");
  resultJson.textContent = JSON.stringify(data, null, 2);
  mockBanner.classList.toggle("hidden", !data.mock_mode);
}

document.getElementById("submitText").addEventListener("click", async () => {
  const text = document.getElementById("textInput").value.trim();
  if (!text) { alert("Please enter a report."); return; }

  showLoading(true);
  resultSection.classList.add("hidden");
  try {
    const res = await fetch("/api/process/text", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to process text");
    renderResult(data);
  } catch (err) {
    alert(err.message);
  } finally {
    showLoading(false);
  }
});

document.getElementById("submitFile").addEventListener("click", async () => {
  const input = document.getElementById("fileInput");
  if (!input.files.length) { alert("Please choose a file."); return; }

  const formData = new FormData();
  formData.append("file", input.files[0]);

  showLoading(true);
  resultSection.classList.add("hidden");
  try {
    const res = await fetch("/api/process/file", { method: "POST", body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Failed to process file");
    renderResult(data);
  } catch (err) {
    alert(err.message);
  } finally {
    showLoading(false);
  }
});
