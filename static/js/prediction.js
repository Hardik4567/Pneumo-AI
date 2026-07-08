/**
 * PneumoAI — Prediction Results Handler v3.1
 * Reads prediction payload from sessionStorage and populates result.html.
 * Supports __originalImage (base64) and __heatmapUrl (normalised) injected
 * by upload.js v2.1, with full fallback to raw API fields.
 */
'use strict';
(function () {

  // ---------------------------------------------------------------------------
  // Constants
  // ---------------------------------------------------------------------------

  const STORAGE_KEY      = 'pneumo_prediction_result';
  const UPLOAD_PATH      = '/upload';
  const REPORT_API       = (id) => `/api/report/download/${id}`;
  const HIGH_RISK_THRESHOLD = 85;

  // ---------------------------------------------------------------------------
  // Utilities
  // ---------------------------------------------------------------------------

  /**
   * Safely retrieve an element by ID; logs a warning when absent.
   * @param {string} id
   * @returns {HTMLElement|null}
   */
  const $ = (id) => {
    const el = document.getElementById(id);
    if (!el) console.warn(`[PneumoAI] Element #${id} not found.`);
    return el;
  };

  /** Set textContent if element exists. */
  const setText = (el, value) => { if (el) el.textContent = value; };

  /**
   * Extract a field from data.data[field] or data[field] (flat payload).
   * Also checks the top-level __ prefixed pre-computed keys injected by upload.js.
   */
  const extractField = (data, field) => {
    if (data?.data?.[field] !== undefined) return data.data[field];
    if (data?.[field]       !== undefined) return data[field];
    return null;
  };

  /**
   * Convert a Windows-style backslash path to a browser-safe URL.
   * Returns '' for falsy input.
   * @param {string} rawPath  e.g. "static\\heatmaps\\overlay.png"
   * @returns {string}        e.g. "/static/heatmaps/overlay.png"
   */
  const toPublicUrl = (rawPath) => {
    if (!rawPath) return '';
    const normalized = rawPath.replace(/\\/g, '/').replace(/^\/+/, '');
    return '/' + normalized;
  };

  /** Format a Date to a readable string. */
  const formatDate = (date) =>
    new Intl.DateTimeFormat('en-US', {
      month : 'short', day: '2-digit', year: 'numeric',
      hour  : '2-digit', minute: '2-digit', hour12: true,
    }).format(date);

  /** Emit a toast via global PneumoAI helper or fall back to console. */
  const showToast = (msg, type = 'info') => {
    if (window.PneumoAI?.showToast) {
      window.PneumoAI.showToast(msg, type);
    } else {
      console.info(`[PneumoAI Toast][${type}] ${msg}`);
    }
  };

  // ---------------------------------------------------------------------------
  // Rendering helpers
  // ---------------------------------------------------------------------------

  /** Prediction label + CSS class. */
  const renderPrediction = (prediction, isPneumonia) => {
    const el = $('resultPrediction');
    if (!el) return;
    el.textContent = prediction;
    el.className   = 'pred-value ' + (isPneumonia ? 'pneumonia' : 'normal');
  };

  /** Confidence bar, text, and ring. */
  const renderConfidence = (safeConf, isPneumonia) => {
    const gradient = isPneumonia
      ? 'linear-gradient(90deg,#ff4757,#ff6b35)'
      : 'linear-gradient(90deg,#4f8ef7,#00d4aa)';

    setText($('resultConfidence'), safeConf.toFixed(1));

    const bar = $('resultConfidenceBar');
    if (bar) {
      bar.style.background = gradient;
      setTimeout(() => { bar.style.width = safeConf + '%'; }, 100);
    }

    if (typeof window.__updateConfRing === 'function') {
      window.__updateConfRing(safeConf);
    }
  };

  /** Pneumonia / Normal probability bars. */
  const renderProbabilities = (safeConf, isPneumonia) => {
    const pneuPct = isPneumonia ? safeConf          : (100 - safeConf);
    const normPct = isPneumonia ? (100 - safeConf)  : safeConf;

    setText($('pneumoniaProb'), pneuPct.toFixed(1) + '%');
    setText($('normalProb'),    normPct.toFixed(1) + '%');

    const pneuBar = $('pneumoniaBar');
    const normBar = $('normalBar');
    if (pneuBar) setTimeout(() => { pneuBar.style.width = pneuPct + '%'; }, 150);
    if (normBar) setTimeout(() => { normBar.style.width = normPct + '%'; }, 200);
  };

  /** Severity label, colour, indicator dots. */
  const renderSeverity = (isPneumonia, safeConf) => {
    const sevEl = $('severityVal');
    const sev2  = $('sev2');
    const sev3  = $('sev3');
    if (!sevEl) return;

    if (isPneumonia && safeConf >= HIGH_RISK_THRESHOLD) {
      sevEl.textContent = 'High Risk'; sevEl.style.color = '#ff4757';
      if (sev2) sev2.style.background = '#ff4757';
      if (sev3) sev3.style.background = '#ff4757';
    } else if (isPneumonia) {
      sevEl.textContent = 'Moderate'; sevEl.style.color = '#f0a060';
      if (sev2) sev2.style.background = '#f0a060';
    } else {
      sevEl.textContent = 'Low Risk'; sevEl.style.color = '#00d4aa';
    }
  };

  /** Recommendation and explanation copy. */
  const renderCopy = (isPneumonia) => {
    setText(
      $('recommendationText'),
      isPneumonia
        ? 'Consult a healthcare professional immediately for proper diagnosis and treatment plan.'
        : 'No significant signs of pneumonia detected. Maintain regular health checkups.'
    );
    setText(
      $('explanationText'),
      isPneumonia
        ? 'The AI model detected abnormal opacities in the lung regions, indicating a possible pneumonia infection. The highlighted areas show the regions that most influenced this prediction.'
        : 'The AI model analysed the chest X-ray and found no significant indicators of pneumonia. The lung fields appear clear with no abnormal opacities detected.'
    );
  };

  /** Dates and processing time. */
  const renderMeta = (processingTime) => {
    const dateStr = formatDate(new Date());
    ['scanDate', 'analysisDate'].forEach((id) => setText($(id), dateStr));

    const timeStr = processingTime
      ? parseFloat(processingTime).toFixed(2) + 's'
      : '—';
    ['analysisTime', 'analysisSummaryTime'].forEach((id) => setText($(id), timeStr));
  };

  /**
   * Render the original uploaded X-ray image.
   *
   * Priority:
   *   1. data.__originalImage  — base64 data URL written by upload.js v2.1
   *   2. Falls back silently if not present (older session).
   *
   * Target element: #originalImage
   */
  const renderOriginalImage = (data) => {
    const src = data.__originalImage || null;

    console.log('[PneumoAI] Original image from session:', !!src);

    if (!src) {
      console.warn('[PneumoAI] No __originalImage in session — original X-ray will not be shown.');
      return;
    }

    const el = $('originalImage');
    if (!el) {
      console.warn('[PneumoAI] Element #originalImage not found in DOM.');
      return;
    }

    const ph = $('xrayPlaceholder');

    // The img starts with src="" which fires onerror immediately in many browsers,
    // setting display:none on the img. Undo that before assigning the real src.
    el.removeAttribute('onerror');          // prevent the inline handler from re-firing
    el.style.display = 'block';             // restore visibility hidden by onerror

    el.onload = () => {
      // Image loaded successfully — hide placeholder, ensure img is visible
      el.style.display = 'block';
      if (ph) ph.style.display = 'none';
      console.log('[PneumoAI] #originalImage loaded ✓');
    };

    el.onerror = () => {
      // Real load failure — show placeholder
      el.style.display = 'none';
      if (ph) ph.style.display = 'flex';
      console.warn('[PneumoAI] #originalImage failed to load.');
    };

    el.src = src;
    el.alt = 'Original X-Ray';
    console.log('[PneumoAI] #originalImage src set ✓ (base64, length:', src.length, ')');
  };

  /**
   * Render the Grad-CAM heatmap overlay.
   *
   * Priority:
   *   1. data.__heatmapUrl    — pre-normalised URL written by upload.js v2.1
   *   2. extractField(data, 'heatmap') — raw API path, normalised here as fallback
   *
   * Target element: #heatmapImage (preferred) → #originalImage (legacy fallback)
   */
  const renderHeatmap = (data) => {
    const publicUrl =
      data.__heatmapUrl ||
      toPublicUrl(extractField(data, 'heatmap')) ||
      null;

    console.log('[PneumoAI] Heatmap public URL:', publicUrl);

    if (!publicUrl) {
      console.warn('[PneumoAI] No heatmap path found in session payload.');
      return;
    }

    const target = $('heatmapImage');
    const ph     = $('heatmapPlaceholder');

    if (!target) {
      console.warn('[PneumoAI] Element #heatmapImage not found in DOM.');
      return;
    }

    // Ensure the img element is visible before we assign src
    // (browsers may have hidden it due to the initial empty src)
    target.style.display = 'block';

    target.onload = () => {
      target.style.display = 'block';
      if (ph) ph.style.display = 'none';
      console.log('[PneumoAI] #heatmapImage loaded ✓ src:', publicUrl);
    };

    target.onerror = () => {
      target.style.display = 'none';
      if (ph) ph.style.display = 'flex';
      console.warn('[PneumoAI] #heatmapImage failed to load. URL was:', publicUrl);
    };

    target.src = publicUrl;
    target.alt = 'Grad-CAM Heatmap';
    console.log('[PneumoAI] #heatmapImage src set ✓');
  };

  // ---------------------------------------------------------------------------
  // Main render orchestrator
  // ---------------------------------------------------------------------------

  /**
   * Populate every result.html element from the sessionStorage payload.
   * @param {Object} data  Parsed JSON from sessionStorage
   */
  const displayResults = (data) => {
    if (!data) {
      showToast('No prediction data available.', 'error');
      return;
    }

    const prediction     = extractField(data, 'prediction') || 'Unknown';
    const rawConf        = extractField(data, 'confidence');
    const confidence     = rawConf !== null ? parseFloat(rawConf) : 0;
    const safeConf       = isNaN(confidence) ? 0 : Math.min(Math.max(confidence, 0), 100);
    const isPneumonia    = prediction.toLowerCase().includes('pneumonia');
    const processingTime = extractField(data, 'processing_time');

    console.log('[PneumoAI] Rendering results — Prediction:', prediction, '| Confidence:', safeConf);

    renderPrediction(prediction, isPneumonia);
    renderConfidence(safeConf, isPneumonia);
    renderProbabilities(safeConf, isPneumonia);
    renderSeverity(isPneumonia, safeConf);
    renderCopy(isPneumonia);
    renderMeta(processingTime);
    renderOriginalImage(data);   // ← original X-ray (base64 from upload.js)
    renderHeatmap(data);         // ← Grad-CAM overlay (path from API)

    const dlBtn = $('downloadReportBtn');
    if (dlBtn) dlBtn.disabled = false;
  };

  // ---------------------------------------------------------------------------
  // Download report
  // ---------------------------------------------------------------------------

  const downloadReport = async (data) => {
    const historyId = extractField(data, 'history_id');
    if (!historyId) { showToast('Report ID not found in session.', 'error'); return; }

    showToast('Requesting report…', 'info');

    try {
      const token = localStorage.getItem('accessToken');
      const res   = await fetch(REPORT_API(historyId), {
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!res.ok) throw new Error(`Server responded with ${res.status}`);

      const reportInfo = await res.json();
      console.log('[PneumoAI] Report info:', reportInfo);

      const downloadUrl = reportInfo.downloadUrl
        || toPublicUrl(extractField(data, 'report_path'));
      const fileName    = reportInfo.fileName
        || extractField(data, 'report_name')
        || `pneumoai_report_${historyId}.pdf`;

      if (!downloadUrl) throw new Error('No download URL available.');

      const anchor         = document.createElement('a');
      anchor.href          = downloadUrl;
      anchor.download      = fileName;
      anchor.style.display = 'none';
      document.body.appendChild(anchor);
      anchor.click();
      document.body.removeChild(anchor);

      showToast('Report downloaded successfully.', 'success');
    } catch (err) {
      console.error('[PneumoAI] Download error:', err);
      showToast('Download failed: ' + err.message, 'error');
    }
  };

  // ---------------------------------------------------------------------------
  // Event wiring
  // ---------------------------------------------------------------------------

  const initEvents = (data) => {
    $('downloadReportBtn')?.addEventListener('click', () => {
      if (!data) { showToast('No prediction data to download.', 'error'); return; }
      downloadReport(data);
    });

    $('newAnalysisBtn')?.addEventListener('click', () => {
      sessionStorage.removeItem(STORAGE_KEY);
      window.location.href = UPLOAD_PATH;
    });

    $('shareResultsBtn')?.addEventListener('click', () => {
      if (!navigator.clipboard) {
        showToast('Clipboard not supported in this browser.', 'warning');
        return;
      }
      navigator.clipboard
        .writeText(window.location.href)
        .then(() => showToast('Link copied to clipboard.', 'success'))
        .catch(()  => showToast('Could not copy link.', 'error'));
    });
  };

  // ---------------------------------------------------------------------------
  // Bootstrap
  // ---------------------------------------------------------------------------

  const init = () => {
    console.log('[PneumoAI] Results handler v3.1 initialised.');

    const raw = sessionStorage.getItem(STORAGE_KEY);
    let data  = null;

    if (raw) {
      try {
        data = JSON.parse(raw);
        console.log('[PneumoAI] Session payload keys:', Object.keys(data));
      } catch (parseErr) {
        console.error('[PneumoAI] Failed to parse session data:', parseErr);
      }
    }

    if (!data) {
      console.warn('[PneumoAI] No prediction data in sessionStorage — redirecting.');
      const predEl = $('resultPrediction');
      if (predEl) { predEl.textContent = 'No Results'; predEl.style.color = 'rgba(255,255,255,0.3)'; }
      showToast('No prediction data found. Redirecting…', 'warning');
      setTimeout(() => { window.location.href = UPLOAD_PATH; }, 3000);
      return;
    }

    displayResults(data);
    initEvents(data);
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window.PredictionResult = { displayResults };

})();
