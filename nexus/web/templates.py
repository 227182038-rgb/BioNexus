"""Minimal static HTML page for the web UI.

The page is intentionally framework-free: a single HTML file with
vanilla JS that calls the FastAPI endpoints in :mod:`nexus.api`. This
keeps the web layer dependency-light and easy to audit.
"""

from __future__ import annotations

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Nexus Ω — Biological Interpretation Intelligence</title>
<style>
  body { font-family: -apple-system, system-ui, sans-serif; margin: 0; padding: 0;
         background: #fafafa; color: #1a1a1a; }
  header { background: #162032; color: #fff; padding: 1.5rem 2rem; }
  header h1 { margin: 0; font-size: 1.5rem; font-weight: 500; }
  header .sub { color: #8898A8; font-size: 0.9rem; margin-top: 0.25rem; }
  main { max-width: 960px; margin: 2rem auto; padding: 0 1rem; }
  .card { background: #fff; border: 1px solid #e0ddd5; border-radius: 6px;
          padding: 1.5rem; margin-bottom: 1.5rem; }
  textarea { width: 100%; min-height: 80px; padding: 0.75rem; font-family: inherit;
             border: 1px solid #c3beb0; border-radius: 4px; resize: vertical; }
  button { background: #8b7423; color: #fff; border: none; padding: 0.75rem 1.5rem;
           border-radius: 4px; cursor: pointer; font-size: 0.95rem; }
  button:hover { background: #6e5d1c; }
  button:disabled { background: #ccc; cursor: not-allowed; }
  .answer { white-space: pre-wrap; margin-top: 1rem; line-height: 1.6; }
  .meta { color: #6a6a6a; font-size: 0.85rem; margin-top: 1rem; }
  .citations { margin-top: 1rem; font-size: 0.85rem; }
  .citations ul { padding-left: 1.5rem; }
  .error { color: #8e453e; }
</style>
</head>
<body>
<header>
  <h1>Nexus Ω</h1>
  <div class="sub">Biological Interpretation Intelligence — AI-native scientific OS for biology</div>
</header>
<main>
  <div class="card">
    <h2>Ask Nexus</h2>
    <p>Ask a biological question. Nexus will retrieve evidence, reason, and respond with citations.</p>
    <textarea id="question" placeholder="e.g. What is known about the function of BRCA1?"></textarea>
    <p><button id="ask" onclick="askNexus()">Ask</button></p>
    <div id="result"></div>
  </div>
</main>
<script>
async function askNexus() {
  const question = document.getElementById('question').value.trim();
  if (!question) return;
  const btn = document.getElementById('ask');
  const result = document.getElementById('result');
  btn.disabled = true;
  result.innerHTML = '<p>Thinking...</p>';
  try {
    const resp = await fetch('/api/interpret', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: question, agent: 'literature' }),
    });
    if (!resp.ok) throw new Error('HTTP ' + resp.status);
    const data = await resp.json();
    let html = '<div class="answer">' + escapeHtml(data.answer || '(no answer)') + '</div>';
    html += '<div class="meta">Confidence: ' + (data.confidence || 0).toFixed(2)
          + ' · Provider: ' + escapeHtml(data.provider_model || 'unknown') + '</div>';
    if (data.citations && data.citations.length) {
      html += '<div class="citations"><strong>Citations:</strong><ul>';
      data.citations.forEach(c => { html += '<li>' + escapeHtml(c) + '</li>'; });
      html += '</ul></div>';
    }
    result.innerHTML = html;
  } catch (err) {
    result.innerHTML = '<p class="error">Error: ' + escapeHtml(err.message) + '</p>';
  } finally {
    btn.disabled = false;
  }
}
function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, ch => (
    {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]
  ));
}
</script>
</body>
</html>
"""

__all__ = ["HTML"]
