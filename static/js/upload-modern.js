/**
 * PneumoAI — Upload Controller v2.1
 * Matches upload.html template exactly.
 * Fixes: original image + heatmap forwarded to result page via sessionStorage.
 */
'use strict';
(function () {

  const CONFIG = {
    MAX_SIZE    : 25 * 1024 * 1024,
    ALLOWED_EXT : ['png', 'jpg', 'jpeg'],
    ALLOWED_MIME: ['image/png', 'image/jpeg'],
    PREDICT_URL : '/predict',
    TIMEOUT_MS  : 60000,
    STORAGE_KEY : 'pneumo_prediction_result',
  };

  /* DOM refs — matching upload.html IDs exactly */
  const D  = {};
  const $  = (id) => document.getElementById(id);

  const cacheDOM = () => {
    D.dropZone       = $('dropZone');
    D.fileInput      = $('fileInput');
    D.previewSection = $('previewSection');
    D.previewImage   = $('previewImage');
    D.fileName       = $('detailFileName');
    D.fileSize       = $('detailFileSize');
    D.dimensions     = $('detailDimensions');
    D.fileType       = $('detailFileType');
    D.analyzeBtn     = $('analyzeBtn');
    D.removeBtn      = $('removeImageBtn');
    D.changeBtn      = $('changeImageBtn');
    D.loadingSection = $('loadingSection');
    D.analysisLabel  = $('analysisLabel');
    D.progressFill   = $('analysisProgressFill');
    D.resultSection  = $('resultSection');
    D.predValue      = $('predictionValue');
    D.predStatus     = $('predictionStatus');
    D.confPercent    = $('confidencePercent');
    D.confFill       = $('confidenceFill');
    D.detailPred     = $('detailPrediction');
    D.detailConf     = $('detailConfidence');
    D.detailTime     = $('detailTime');
    D.newAnalysisBtn = $('newAnalysisBtn');
    D.errorSection   = $('errorSection');
    D.errorMessage   = $('errorMessage');
    D.errorRetryBtn  = $('errorRetryBtn');
    return !!D.dropZone;
  };

  const STATE = {
    file      : null,
    previewURL: null,   // blob URL of the selected file
    analyzing : false,
    controller: null,
    startTime : null,
  };

  const show    = (el) => { if (el) el.classList.remove('d-none'); };
  const hide    = (el) => { if (el) el.classList.add('d-none'); };
  const setText = (el, v) => { if (el) el.textContent = v; };

  const fmtBytes = (b) => {
    if (!b) return '0 B';
    const k = 1024, sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(b) / Math.log(k));
    return +(b / Math.pow(k, i)).toFixed(2) + ' ' + sizes[i];
  };

  const extractField = (data, field) => {
    if (data?.data?.[field] !== undefined) return data.data[field];
    if (data?.[field]       !== undefined) return data[field];
    return null;
  };

  /* -------------------------------------------------------------------------
   * Convert a blob URL to a base64 data URL so it survives page navigation.
   * Returns null if conversion fails.
   * ---------------------------------------------------------------------- */
  const blobUrlToBase64 = (blobUrl) =>
    new Promise((resolve) => {
      if (!blobUrl) { resolve(null); return; }
      const xhr      = new XMLHttpRequest();
      xhr.open('GET', blobUrl, true);
      xhr.responseType = 'blob';
      xhr.onload  = () => {
        const reader     = new FileReader();
        reader.onloadend = () => resolve(reader.result); // "data:image/...;base64,..."
        reader.onerror   = () => resolve(null);
        reader.readAsDataURL(xhr.response);
      };
      xhr.onerror = () => resolve(null);
      xhr.send();
    });

  /* File validation */
  const validateFile = (file) =>
    new Promise((resolve, reject) => {
      if (!file) return reject(new Error('No file selected.'));
      if (file.size > CONFIG.MAX_SIZE)
        return reject(new Error('File too large. Maximum 25 MB.'));
      const ext = file.name.split('.').pop().toLowerCase();
      if (!CONFIG.ALLOWED_EXT.includes(ext))
        return reject(new Error('Unsupported format. Use PNG or JPEG.'));
      if (!CONFIG.ALLOWED_MIME.includes(file.type))
        return reject(new Error('Invalid file type.'));
      const img = new Image();
      const url = URL.createObjectURL(file);
      img.src    = url;
      img.onload = () => {
        URL.revokeObjectURL(url);
        if (img.naturalWidth < 128 || img.naturalHeight < 128)
          return reject(new Error('Image too small. Minimum 128×128 px.'));
        resolve({ width: img.naturalWidth, height: img.naturalHeight });
      };
      img.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error('Corrupt or unreadable image.'));
      };
    });

  /* Handle file selection */
  const handleFile = async (file) => {
    if (!file) return;
    try {
      const dims = await validateFile(file);
      STATE.file = file;
      if (STATE.previewURL) URL.revokeObjectURL(STATE.previewURL);
      STATE.previewURL = URL.createObjectURL(file);
      if (D.previewImage) D.previewImage.src = STATE.previewURL;
      setText(D.fileName,   file.name);
      setText(D.fileSize,   fmtBytes(file.size));
      setText(D.dimensions, `${dims.width} × ${dims.height} px`);
      setText(D.fileType,   file.type.split('/').pop().toUpperCase());
      hide(D.dropZone); hide(D.resultSection);
      hide(D.errorSection); hide(D.loadingSection);
      show(D.previewSection);
    } catch (e) {
      showError(e.message);
    }
  };

  /* Set loading step */
  const setStep = (step, pct) => {
    if (window.__setLoadingStep) window.__setLoadingStep(step, pct);
    if (D.progressFill) D.progressFill.style.width = pct + '%';
    const labels = [
      'Uploading image…',
      'Preprocessing…',
      'Neural inference running…',
      'Generating report…',
    ];
    setText(D.analysisLabel, labels[step - 1] || 'Analyzing…');
  };

  /* -------------------------------------------------------------------------
   * Run analysis
   * ---------------------------------------------------------------------- */
  const analyze = async () => {
    if (!STATE.file || STATE.analyzing) return;
    STATE.analyzing = true;
    STATE.startTime = performance.now();
    STATE.controller = new AbortController();
    hide(D.previewSection); hide(D.resultSection); hide(D.errorSection);
    show(D.loadingSection);
    setStep(1, 10);

    try {
      const fd = new FormData();
      fd.append('file', STATE.file);

      const pName   = $('patientNameInput')?.value   || 'Anonymous';
      const pAge    = $('patientAgeInput')?.value    || '0';
      const pGender = $('patientGenderInput')?.value || 'Unknown';
      fd.append('patient_name',   pName);
      fd.append('patient_age',    pAge);
      fd.append('patient_gender', pGender);

      setStep(2, 30);

      const token = localStorage.getItem('accessToken');
      const res   = await fetch(CONFIG.PREDICT_URL, {
        method : 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body   : fd,
        signal : STATE.controller.signal,
      });

      // ── DEBUG: log the raw response shape ──────────────────────────────
      const payload = await res.json();
      console.log('[PneumoAI] Raw API payload:', JSON.stringify(payload));
      // ───────────────────────────────────────────────────────────────────

      if (!res.ok || payload.success === false)
        throw new Error(payload.error || `Server error (${res.status})`);

      setStep(4, 100);
      const elapsed = ((performance.now() - STATE.startTime) / 1000).toFixed(2);

      // renderResult is async — await it so sessionStorage write completes
      // before the redirect fires.
      await renderResult(payload, elapsed);

    } catch (e) {
      if (e.name === 'AbortError') return;
      showError(e.message);
    } finally {
      STATE.analyzing  = false;
      STATE.controller = null;
      hide(D.loadingSection);
    }
  };

  /* -------------------------------------------------------------------------
   * Render inline result card, persist enriched payload, then redirect.
   * Made async so we can await the base64 conversion before navigating.
   * ---------------------------------------------------------------------- */
  const renderResult = async (payload, elapsed) => {
    const prediction = extractField(payload, 'prediction') || 'Unknown';
    const rawConf    = extractField(payload, 'confidence');
    const confidence = rawConf !== null ? parseFloat(rawConf) : 0;
    const safeConf   = isNaN(confidence) ? 0 : Math.min(Math.max(confidence, 0), 100);
    const isPneumonia = prediction.toLowerCase().includes('pneumonia');

    console.log('[PneumoAI] Prediction:', prediction, '| Confidence:', safeConf);

    /* Prediction status bubble */
    if (D.predStatus) {
      D.predStatus.style.cssText = isPneumonia
        ? 'display:inline-flex;align-items:center;gap:8px;padding:10px 18px;border-radius:999px;font-size:16px;font-weight:700;background:rgba(255,71,87,0.12);color:#ff4757;border:1px solid rgba(255,71,87,0.25)'
        : 'display:inline-flex;align-items:center;gap:8px;padding:10px 18px;border-radius:999px;font-size:16px;font-weight:700;background:rgba(0,212,170,0.12);color:#00d4aa;border:1px solid rgba(0,212,170,0.25)';
      const icon = D.predStatus.querySelector('i');
      if (icon) icon.className = isPneumonia ? 'fas fa-triangle-exclamation' : 'fas fa-check-circle';
    }

    setText(D.predValue,   prediction);
    setText(D.confPercent, safeConf.toFixed(1));
    setText(D.detailPred,  prediction);
    setText(D.detailConf,  safeConf.toFixed(2) + '%');
    setText(D.detailTime,  elapsed + 's');

    if (D.confFill) {
      setTimeout(() => { D.confFill.style.width = safeConf + '%'; }, 100);
      D.confFill.style.background = isPneumonia
        ? 'linear-gradient(90deg,#ff4757,#ff6b35)'
        : 'linear-gradient(90deg,#4f8ef7,#00d4aa)';
    }

    /* ------------------------------------------------------------------
     * Persist payload to sessionStorage.
     * Attach the original uploaded image as base64 (__originalImage) and
     * normalise the heatmap path (__heatmapUrl) so result.js gets both
     * as ready-to-use values regardless of OS path separators.
     * ---------------------------------------------------------------- */
    try {
      // Convert blob URL → base64 so it survives navigation
      console.log('[PneumoAI] Original image blob URL:', STATE.previewURL);
      const originalImageB64 = await blobUrlToBase64(STATE.previewURL);
      console.log('[PneumoAI] Original image base64 ready:', !!originalImageB64);

      // Normalise heatmap path from API (handles Windows backslashes)
      const heatmapRaw = extractField(payload, 'heatmap');
      const heatmapUrl = heatmapRaw
        ? '/' + heatmapRaw.replace(/\\/g, '/').replace(/^\/+/, '')
        : null;
      console.log('[PneumoAI] Heatmap raw path:', heatmapRaw);
      console.log('[PneumoAI] Heatmap public URL:', heatmapUrl);

      // Enrich the payload with pre-computed values for result.js
      const enrichedPayload = {
        ...payload,
        __originalImage: originalImageB64,  // data:image/...;base64,...  (or null)
        __heatmapUrl   : heatmapUrl,         // /static/heatmaps/overlay.png (or null)
      };

      sessionStorage.setItem(CONFIG.STORAGE_KEY, JSON.stringify(enrichedPayload));
      console.log('[PneumoAI] Prediction saved to sessionStorage ✓');

    } catch (e) {
      console.error('[PneumoAI] Failed to enrich/save prediction:', e);
      // Fallback: save bare payload so the result page still has data
      try {
        sessionStorage.setItem(CONFIG.STORAGE_KEY, JSON.stringify(payload));
      } catch (_) { /* storage full — nothing more we can do */ }
    }

    STATE.analyzing = false;

    /* Redirect to results page */
    window.location.href = '/results';
  };

  /* Show error card */
  const showError = (msg) => {
    hide(D.loadingSection); hide(D.resultSection); hide(D.previewSection);
    setText(D.errorMessage, msg || 'An error occurred.');
    show(D.errorSection); show(D.dropZone);
  };

  /* Reset to initial state */
  const reset = () => {
    if (STATE.controller) STATE.controller.abort();
    if (STATE.previewURL) { URL.revokeObjectURL(STATE.previewURL); STATE.previewURL = null; }
    STATE.file = null; STATE.analyzing = false;
    if (D.fileInput)    D.fileInput.value = '';
    if (D.previewImage) D.previewImage.src = '';
    hide(D.previewSection); hide(D.loadingSection);
    hide(D.resultSection);  hide(D.errorSection);
    show(D.dropZone);
  };

  /* Drag & drop */
  const initDragDrop = () => {
    const z = D.dropZone; if (!z) return;
    const prevent = (e) => { e.preventDefault(); e.stopPropagation(); };
    z.addEventListener('dragover',  prevent, { passive: false });
    z.addEventListener('dragenter', (e) => { prevent(e); z.classList.add('active'); });
    z.addEventListener('dragleave', () => z.classList.remove('active'));
    z.addEventListener('drop', (e) => {
      prevent(e); z.classList.remove('active');
      const f = e.dataTransfer?.files?.[0];
      if (f) handleFile(f);
    }, { passive: false });
    z.addEventListener('click',   () => D.fileInput?.click());
    z.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); D.fileInput?.click(); }
    });
  };

  /* Clipboard paste */
  const initClipboard = () => {
    document.addEventListener('paste', (e) => {
      if (['INPUT', 'TEXTAREA'].includes(document.activeElement?.tagName)) return;
      for (const item of e.clipboardData?.items || []) {
        if (item.type.startsWith('image/')) {
          const f = item.getAsFile();
          if (f) { handleFile(new File([f], `pasted_${Date.now()}.png`, { type: 'image/png' })); break; }
        }
      }
    }, { passive: true });
  };

  /* Event wiring */
  const initEvents = () => {
    D.fileInput?.addEventListener('change', (e) => {
      const f = e.target.files?.[0]; if (f) handleFile(f);
    }, { passive: true });
    D.analyzeBtn?.addEventListener('click',  (e) => { e.preventDefault(); analyze(); });
    D.removeBtn?.addEventListener('click',   (e) => { e.preventDefault(); reset(); });
    D.changeBtn?.addEventListener('click',   (e) => { e.preventDefault(); D.fileInput?.click(); });
    D.newAnalysisBtn?.addEventListener('click', (e) => { e.preventDefault(); reset(); });
    D.errorRetryBtn?.addEventListener('click',  (e) => { e.preventDefault(); reset(); });
    // Warn only when navigation happens WHILE a request is in flight
    window.addEventListener('beforeunload', (e) => {
      if (!STATE.analyzing) return;
      e.preventDefault();
      e.returnValue = '';
    });
  };

  const init = () => {
    if (!cacheDOM()) { console.warn('[PneumoAI] Upload form not found.'); return; }
    initDragDrop(); initClipboard(); initEvents();
    console.log('[PneumoAI] Upload controller v2.1 initialized.');
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();

  window.PneumoUpload = { reset, analyze };

})();
