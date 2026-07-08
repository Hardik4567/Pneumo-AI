/**
 * ==========================================================================
 * PneumoAI - Clinical Image Upload & Analysis Controller
 * File: upload.js
 * Version: 1.0.0
 * Description: High-fidelity client-side workflow engine for chest X-ray ingestion.
 * Handles drag-and-drop mechanics, async multi-stage Fetch pipelines, 
 * AbortController lifecycle tracking, Grad-CAM visualization, and focus management.
 * ==========================================================================
 */

'use strict';

(function () {
    /* ==========================================================================
       1. CONFIGURATION SYSTEM
       ========================================================================== */
    const CONFIG = {
        FILE: {
            MAX_SIZE_BYTES: 10 * 1024 * 1024, // 10 Megabytes
            ALLOWED_EXTENSIONS: ['png', 'jpg', 'jpeg'],
            ALLOWED_MIME_TYPES: ['image/png', 'image/jpeg'],
            FUTURE_EXTENSIONS: ['dcm', 'dicom'] // Hooks reserved for PACS deployment integration
        },
        ENDPOINTS: {
            PREDICT: '/predict',
            GRADCAM: '/gradcam',
            DOWNLOAD_REPORT: '/download-report',
            HEALTH: '/health'
        },
        TIMEOUTS: {
            ANALYSIS: 45000, // 45 seconds total execution timeout boundary
            HEALTH_CHECK: 5000
        },
        ANIMATION: {
            FADE_DURATION: 300
        }
    };

    /* ==========================================================================
       2. DOM ELEMENTS CACHE
       ========================================================================== */
    const DOM = {};

    const cacheElements = () => {
        const root = document.getElementById('uploadForm');
        if (!root) return false;

        DOM.root = root;
        DOM.dropZone = document.getElementById('dropZone');
        DOM.fileInput = document.getElementById('fileInput');
        DOM.dragOverlay = document.getElementById('dragOverlay');
        
        // Context Preview Panel Components
        DOM.previewCard = document.getElementById('previewCard');
        DOM.previewImage = document.getElementById('previewImage');
        DOM.fileName = document.getElementById('detailFileName');
        DOM.fileSize = document.getElementById('detailFileSize');
        DOM.fileType = document.getElementById('detailFileType');
        DOM.dimensions = document.getElementById('detailDimensions');
        DOM.uploadTime = document.getElementById('detailUploadTime');
        
        // Interface Action Controls Matrix
        DOM.analyzeButton = document.getElementById('analyzeBtn');
        DOM.resetButton = document.getElementById('resetBtn');
        DOM.changeButton = document.getElementById('changeImageBtn');
        DOM.removeButton = document.getElementById('removeImageBtn');
        
        // Synchronous Processing Tracking Containers
        DOM.loadingSection = document.getElementById('loadingSection');
        DOM.progressBar = document.getElementById('analysisProgressFill');
        DOM.progressText = null; // Will be updated manually if needed
        DOM.analysisLabel = document.getElementById('analysisProgressLabel');
        DOM.ariaLiveRegion = null; // Add a live region in HTML if needed
        
        // Diagnostic Report Interface Output Nodes
        DOM.resultSection = document.getElementById('resultPlaceholder');
        DOM.predictionValue = null; // Will be set dynamically
        DOM.confidenceValue = null; // Will be set dynamically
        DOM.confidenceFill = null; // Will be set dynamically
        DOM.gradcamImage = null; // Will be set dynamically
        DOM.gradcamPlaceholder = null; // Will be set dynamically
        DOM.downloadButton = null; // Will be set dynamically
        DOM.shareButton = null; // Will be set dynamically

        return true;
    };

    /* ==========================================================================
       3. UPLOAD INSTANCE RUNTIME VARIABLE STATE
       ========================================================================== */
    const STATE = {
        selectedFile: null,
        previewURL: null,
        isUploading: false,
        isAnalyzing: false,
        predictionResult: null,
        gradcamResult: null,
        abortController: null,
        lastValidationHash: ''
    };

    /* ==========================================================================
       4. CONTEXTUAL CORE UTILITY HELPER METHODS
       ========================================================================== */
    const formatBytes = (bytes, decimals = 2) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    };

    const getCurrentTimestamp = () => {
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric', month: 'short', day: '2-digit',
            hour: '2-digit', minute: '2-digit', second: '2-digit',
            hour12: false
        }).format(new Date());
    };

    const show = (element, displayStyle = 'block') => {
        if (!element) return;
        element.style.display = displayStyle;
        element.removeAttribute('aria-hidden');
    };

    const hide = (element) => {
        if (!element) return;
        element.style.display = 'none';
        element.setAttribute('aria-hidden', 'true');
    };

    const setAccessibilityAlert = (message) => {
        if (DOM.ariaLiveRegion) DOM.ariaLiveRegion.textContent = message;
    };

    const setProgressState = (percent, phaseLabel) => {
        const value = Math.round(clamp(percent, 0, 100));
        if (DOM.progressBar) DOM.progressBar.style.width = `${value}%`;
        if (DOM.progressText) DOM.progressText.textContent = `${value}%`;
        if (DOM.analysisLabel) DOM.analysisLabel.textContent = phaseLabel;
        DOM.progressBar?.setAttribute('aria-valuenow', value);
    };

    const clamp = (val, min, max) => Math.min(Math.max(val, min), max);

    /* ==========================================================================
       5. DETAILED FILE VALIDATION SPECIFICATIONS
       ========================================================================== */
    const validateFile = async (file) => {
        if (!file) throw new Error('No target source file data object provided.');

        // 1. Structural File Footprint Dimensional Restrictions Checklist
        if (file.size > CONFIG.FILE.MAX_SIZE_BYTES) {
            throw new Error(`File footprint violates maximum sizing thresholds. Maximum allowed limit is ${formatBytes(CONFIG.FILE.MAX_SIZE_BYTES)}.`);
        }

        // 2. Format / File Extension Structure Verifications
        const extension = file.name.split('.').pop().toLowerCase();
        if (!CONFIG.FILE.ALLOWED_EXTENSIONS.includes(extension)) {
            if (CONFIG.FILE.FUTURE_EXTENSIONS.includes(extension)) {
                throw new Error('DICOM medical archive imaging formats currently require manual processing conversion routing configurations via standard PACS networks.');
            }
            throw new Error('Unsupported image format structure definition detected. Please supply valid PNG or JPEG chest radiography files.');
        }

        // 3. MIME Content Verification Routing Mapping Check
        if (!CONFIG.FILE.ALLOWED_MIME_TYPES.includes(file.type)) {
            throw new Error('Invalid system structural data type classification identified.');
        }

        // 4. Client Side Binary Integrity Execution Verification Loop Map
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.src = URL.createObjectURL(file);
            
            img.onload = () => {
                const structuralMetadata = {
                    width: img.naturalWidth,
                    height: img.naturalHeight,
                    aspectRatio: (img.naturalWidth / img.naturalHeight).toFixed(2)
                };
                URL.revokeObjectURL(img.src);

                if (structuralMetadata.width < 128 || structuralMetadata.height < 128) {
                    reject(new Error('Radiographic spatial dimension indices are insufficient to yield reliable algorithmic validation matrix checks.'));
                    return;
                }
                resolve(structuralMetadata);
            };

            img.onerror = () => {
                URL.revokeObjectURL(img.src);
                reject(new Error('Image metadata instantiation failed. Resource tracking binary layer may be corrupt or unstable.'));
            };
        });
    };

    /* ==========================================================================
       6. USER DRAG AND DROP CAPTURE SUBSYSTEMS
       ========================================================================== */
    const initDragAndDropArchitecture = () => {
        const zone = DOM.dropZone;
        if (!zone) return;

        const preventDefaults = (e) => {
            e.preventDefault();
            e.stopPropagation();
        };

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            zone.addEventListener(eventName, preventDefaults, { passive: false });
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            zone.addEventListener(eventName, () => {
                zone.classList.add('dropzone--drag-active');
                if (DOM.dragOverlay) show(DOM.dragOverlay, 'flex');
            }, { passive: true });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            zone.addEventListener(eventName, () => {
                zone.classList.remove('dropzone--drag-active');
                if (DOM.dragOverlay) hide(DOM.dragOverlay);
            }, { passive: true });
        });

        zone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            const files = dt.files;
            if (files.length > 0) {
                processFileSelection(files[0]);
            }
        }, { passive: false });
    };

    /* ==========================================================================
       7. CLIPBOARD ACCESS INTERACTION PIPELINES (Ctrl+V CAPTURE)
       ========================================================================== */
    const initClipboardPasteSupport = () => {
        document.addEventListener('paste', (e) => {
            // Guard conditions preventing interception while manipulating system text entries
            if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return;

            const items = e.clipboardData?.items;
            if (!items) return;

            for (let i = 0; i < items.length; i++) {
                if (items[i].type.indexOf('image') !== -1) {
                    const file = items[i].getAsFile();
                    if (file) {
                        const syntheticFile = new File([file], `pasted_radiograph_${Date.now()}.png`, { type: 'image/png' });
                        processFileSelection(syntheticFile);
                        setAccessibilityAlert('Image data intercepted via global system clipboard registration hooks.');
                        break;
                    }
                }
            }
        }, { passive: true });
    };

    /* ==========================================================================
       8. ASYNCHRONOUS DATA PREVIEW RENDER MATRICES
       ========================================================================== */
    const processFileSelection = async (file) => {
        if (!file) return;

        // Optimize structural redundant processing calculations check loops
        const signatureHash = `${file.name}-${file.size}-${file.lastModified}`;
        if (signatureHash === STATE.lastValidationHash) return;

        try {
            // Re-establish display structures cleanly across variable re-allocations
            clearVisualValidationErrors();
            
            const dimensions = await validateFile(file);
            
            STATE.selectedFile = file;
            STATE.lastValidationHash = signatureHash;

            if (STATE.previewURL) URL.revokeObjectURL(STATE.previewURL);
            STATE.previewURL = URL.createObjectURL(file);

            // Populate Metadata Properties Canvas Structure Mapping Array
            if (DOM.previewImage) DOM.previewImage.src = STATE.previewURL;
            if (DOM.fileName) DOM.fileName.textContent = file.name;
            if (DOM.fileSize) DOM.fileSize.textContent = formatBytes(file.size);
            if (DOM.fileType) DOM.fileType.textContent = file.type.split('/').pop().toUpperCase();
            if (DOM.dimensions) DOM.dimensions.textContent = `${dimensions.width} × ${dimensions.height} px`;
            if (DOM.uploadTime) DOM.uploadTime.textContent = getCurrentTimestamp();

            // Perform interface transformation animations sequences
            hide(DOM.dropZone);
            show(DOM.previewCard);
            DOM.analyzeButton?.removeAttribute('disabled');
            DOM.analyzeButton?.focus();

            setAccessibilityAlert(`Radiograph file ${file.name} validated successfully. Analysis matrix pipeline execution interface ready.`);
        } catch (error) {
            handleWorkflowFailure(error.message, 'Validation Exception');
            resetUploadState();
        }
    };

    /* ==========================================================================
       9. ASYNCHRONOUS FLASK BACKEND PREDICTION INTERFACES
       ========================================================================== */
    const startAnalysisPipeline = async () => {
        if (!STATE.selectedFile || STATE.isUploading || STATE.isAnalyzing) return;

        // Deploy AbortController structural hooks instantiation sets
        STATE.abortController = new AbortController();
        const signal = STATE.abortController.signal;

        try {
            updateInterfaceProcessingState(true);
            setProgressState(10, 'Initializing data packaging structures...');

            const formData = new FormData();
            formData.append('file', STATE.selectedFile);

            setProgressState(30, 'Streaming binary image payload data arrays to endpoint...');

            // Configure dynamic fetch connection wrappers containing hardware metrics tracking integrations
            const response = await fetchWithTimeout(CONFIG.ENDPOINTS.PREDICT, {
                method: 'POST',
                body: formData,
                signal
            }, CONFIG.TIMEOUTS.ANALYSIS);

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `HTTP Service Exception Pipeline Breakdown: Route status verification flag returned code ${response.status}`);
            }

            setProgressState(75, 'Deep Neural Network running logical classification matrices...');
            
            const payload = await response.json();
            
            setProgressState(95, 'Structuring visual analytical maps arrays payload data layers...');
            renderDiagnosticReport(payload);
            
        } catch (error) {
            if (error.name === 'AbortError') {
                setAccessibilityAlert('Analysis pipeline sequence execution cleanly terminated by operator directive.');
                return;
            }
            handleWorkflowFailure(error.message, 'Analytical System Inversion Fault');
        } finally {
            updateInterfaceProcessingState(false);
        }
    };

    const fetchWithTimeout = async (resource, options = {}, timeout) => {
        const { signal, ...rest } = options;
        const controller = new AbortController();
        const id = setTimeout(() => controller.abort(), timeout);

        // Bind parent signal destruction down down the execution stack trees
        if (signal) {
            signal.addEventListener('abort', () => {
                clearTimeout(id);
                controller.abort();
            });
        }

        try {
            const response = await fetch(resource, { ...rest, signal: controller.signal });
            clearTimeout(id);
            return response;
        } catch (error) {
            clearTimeout(id);
            if (error.name === 'AbortError' && !signal?.aborted) {
                throw new Error(`Data transport link verification step exceeded structural timeout parameters at ${timeout / 1000} seconds boundary rules.`);
            }
            throw error;
        }
    };

    /* ==========================================================================
       10. DIAGNOSTIC DATA REPORT COMPONENT VISUAL RENDER MODULES
       ========================================================================== */
    const renderDiagnosticReport = (data) => {
        // Validation evaluation schema profiles enforcement check
        if (!data || (!data.prediction && !data.data?.prediction)) {
            throw new Error('Server classification returned a schema definition vector payload mismatch configuration anomaly.');
        }

        STATE.predictionResult = data;
        
        // Save prediction result to session storage for results page
        try {
            sessionStorage.setItem('pneumo_prediction_result', JSON.stringify(data));
            
            // Add to history if available
            if (window.PneumoHistory?.add) {
                window.PneumoHistory.add(data);
            }
        } catch (error) {
            console.warn('Could not save to session storage:', error);
        }

        // 1. Structural Element Node Text Alignments Injection
        if (DOM.predictionValue) {
            DOM.predictionValue.textContent = data.prediction;
            // Clean contextual state class tags mapping logic
            DOM.predictionValue.className = 'prediction-title js-upload-res-prediction';
            DOM.predictionValue.classList.add(`prediction-title--${data.prediction.toLowerCase().replace(/\s+/g, '')}`);
        }
        
        if (DOM.confidenceValue) DOM.confidenceValue.textContent = `${data.confidence.toFixed(2)}%`;
        if (DOM.confidenceFill) {
            DOM.confidenceFill.style.width = `${data.confidence}%`;
            // Address structural high-contrast feedback profiles dynamically
            DOM.confidenceFill.className = 'confidence-bar__fill js-upload-res-confidence-fill';
            if (data.confidence > 85) DOM.confidenceFill.classList.add('confidence-bar__fill--high');
            else if (data.confidence > 50) DOM.confidenceFill.classList.add('confidence-bar__fill--mid');
            else DOM.confidenceFill.classList.add('confidence-bar__fill--low');
        }

        // 2. Grad-CAM Image Lazy Injection Routine Orchestration Step
        if (DOM.gradcamImage && data.gradcam) {
            if (DOM.gradcamPlaceholder) show(DOM.gradcamPlaceholder);
            hide(DOM.gradcamImage);

            const preloader = new Image();
            preloader.src = data.gradcam;
            preloader.onload = () => {
                DOM.gradcamImage.src = data.gradcam;
                if (DOM.gradcamPlaceholder) hide(DOM.gradcamPlaceholder);
                show(DOM.gradcamImage);
                DOM.gradcamImage.classList.add('gradcam-fade-in');
            };
            preloader.onerror = () => {
                if (DOM.gradcamPlaceholder) DOM.gradcamPlaceholder.textContent = 'Grad-CAM overlay rendering interface asset unavailable.';
            };
        }

        // 3. Redirect to results page after a brief delay
        setTimeout(() => {
            window.location.href = '/results';
        }, 1500);
        
        // 4. Transformation Sequence Views Controls Map Shifts
        hide(DOM.previewCard);
        hide(DOM.loadingSection);
        show(DOM.resultSection);
        
        if (DOM.resultSection) {
            DOM.resultSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
        if (DOM.downloadButton) DOM.downloadButton.focus();
        
        setAccessibilityAlert(`Analysis loop sequence complete. Structural diagnosis outputs read path indicator status: ${data.prediction} containing confidence indexes metric evaluated at ${data.confidence.toFixed(2)} percent.`);
    };

    /* ==========================================================================
       11. CLINICAL CLINICAL REPORT COMPONENT DOWNLOADS ROUTERS
       ========================================================================== */
    const downloadAnalyticalReportFile = async () => {
        if (!STATE.predictionResult?.report) {
            window.PneumoAI?.showToast?.('Target documentation reference pointer addresses cannot be resolved locally.', 'error');
            return;
        }

        try {
            DOM.downloadButton?.setAttribute('disabled', 'true');
            window.PneumoAI?.showToast?.('Generating formal platform clinical laboratory export sheets...', 'info');

            const reportUrl = STATE.predictionResult.report;
            const response = await fetch(reportUrl);
            
            if (!response.ok) throw new Error('Network transport channels failed downstream asset delivery validation tracking.');

            const blob = await response.blob();
            const downloadAnchor = document.createElement('a');
            downloadAnchor.href = URL.createObjectURL(blob);
            downloadAnchor.download = `PneumoAI_Report_${STATE.selectedFile?.name.split('.')[0] || 'Capture'}.pdf`;
            
            document.body.appendChild(downloadAnchor);
            downloadAnchor.click();
            
            document.body.removeChild(downloadAnchor);
            URL.revokeObjectURL(downloadAnchor.href);
            
            window.PneumoAI?.showToast?.('Documentation verification export sequence compiled completely.', 'success');
        } catch (error) {
            window.PneumoAI?.showToast?.(`File composition process experienced standard termination: ${error.message}`, 'error');
        } finally {
            DOM.downloadButton?.removeAttribute('disabled');
        }
    };

    /* ==========================================================================
       12. PIPELINE DESTRUCTION & INVERSION STATE RESTORATION RULES
       ========================================================================== */
    const resetUploadState = () => {
        // 1. Terminate all pending background asynchronous tracking pipelines immediately
        if (STATE.abortController) {
            STATE.abortController.abort();
            STATE.abortController = null;
        }

        // 2. Purge system memory references to object endpoints allocations safely
        if (STATE.previewURL) {
            URL.revokeObjectURL(STATE.previewURL);
            STATE.previewURL = null;
        }

        // 3. Purge structural local parameters values states cache
        STATE.selectedFile = null;
        STATE.lastValidationHash = '';
        STATE.isUploading = false;
        STATE.isAnalyzing = false;
        STATE.predictionResult = null;
        STATE.gradcamResult = null;

        // 4. Reset core data source DOM properties element values configurations mapping
        if (DOM.fileInput) DOM.fileInput.value = '';
        if (DOM.previewImage) DOM.previewImage.src = '';
        if (DOM.gradcamImage) DOM.gradcamImage.src = '';
        
        // 5. Interface display maps layout matrix adjustments updates reset
        hide(DOM.previewCard);
        hide(DOM.loadingSection);
        hide(DOM.resultSection);
        show(DOM.dropZone);
        
        DOM.analyzeButton?.setAttribute('disabled', 'true');
        clearVisualValidationErrors();
        
        DOM.dropZone?.focus();
        setAccessibilityAlert('Platform data ingest frameworks channels reset completely. File upload state pathways normalized.');
    };

    const updateInterfaceProcessingState = (processingActiveStateFlag) => {
        STATE.isAnalyzing = processingActiveStateFlag;
        STATE.isUploading = processingActiveStateFlag;

        if (processingActiveStateFlag) {
            DOM.analyzeButton?.setAttribute('disabled', 'true');
            DOM.changeButton?.setAttribute('disabled', 'true');
            DOM.removeButton?.setAttribute('disabled', 'true');
            hide(DOM.previewCard);
            show(DOM.loadingSection);
            DOM.progressBar?.setAttribute('aria-valuenow', '0');
        } else {
            DOM.changeButton?.removeAttribute('disabled');
            DOM.removeButton?.removeAttribute('disabled');
            hide(DOM.loadingSection);
        }
    };

    const handleWorkflowFailure = (message, contextualNamespace = 'Processing Anomaly') => {
        console.error(`[PneumoAI Upload Engine Fault Monitoring System] -> [${contextualNamespace} Exception Link Cascade Trigger Context]: ${message}`);
        
        // Expose structured tracking parameters elements directly inside main platform layout notifications frameworks nodes
        if (window.PneumoAI?.showToast) {
            window.PneumoAI.showToast(message, 'error', 6000);
        } else {
            alert(`[System Clinical Verification Error Context - ${contextualNamespace}]: ${message}`);
        }
        setAccessibilityAlert(`System validation layer interruption flag triggered notice: ${message}`);
    };

    const clearVisualValidationErrors = () => {
        // Hooks placeholder designed to wipe local visual sub-node configurations fields mapping lists
    };

    /* ==========================================================================
       13. ACCESSIBILITY INTERFACE MANAGEMENT & EVENT RECEPTORS MAPS
       ========================================================================== */
    const initEventBridges = () => {
        // File Selector Interaction Channels Map Activation Controls 
        DOM.fileInput?.addEventListener('change', (e) => {
            if (e.target.files.length > 0) processFileSelection(e.target.files[0]);
        }, { passive: true });

        DOM.dropZone?.addEventListener('click', () => DOM.fileInput?.click(), { passive: true });

        // Screen Keyboard Accessible Structural Directives Mapping Vectors Actions Keys
        DOM.dropZone?.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                DOM.fileInput?.click();
            }
        }, { passive: false });

        // Operational Pipeline Lifecycle Control Trigger Links Mapping Actions Matrix
        DOM.analyzeButton?.addEventListener('click', (e) => {
            e.preventDefault();
            startAnalysisPipeline();
        }, { passive: false });

        DOM.removeButton?.addEventListener('click', (e) => {
            e.preventDefault();
            resetUploadState();
        }, { passive: false });

        DOM.changeButton?.addEventListener('click', (e) => {
            e.preventDefault();
            DOM.fileInput?.click();
        }, { passive: false });

        DOM.resetButton?.addEventListener('click', (e) => {
            e.preventDefault();
            resetUploadState();
        }, { passive: false });

        DOM.downloadButton?.addEventListener('click', (e) => {
            e.preventDefault();
            downloadAnalyticalReportFile();
        }, { passive: false });

        // Guard against unpredictable window state destructions while processing mutations arrays operations loops
        window.addEventListener('beforeunload', (e) => {
            if (STATE.isAnalyzing || STATE.isUploading) {
                e.preventDefault();
                e.returnValue = 'Data interpretation pipeline sequence calculations are currently active. Terminating window routing tracking will cancel diagnostics parameters profiles validation loops.';
                return e.returnValue;
            }
        }, { passive: false });
    };

    /* ==========================================================================
       14. PLATFORM API STRATEGY WRAPPER DISTRIBUTION EXPORTS REGISTER
       ========================================================================== */
    window.Upload = {
        resetUpload: () => resetUploadState(),
        startAnalysis: () => startAnalysisPipeline(),
        validateFile: (file) => validateFile(file),
        showResult: (mockPayloadDataStructureObject) => renderDiagnosticReport(mockPayloadDataStructureObject)
    };

    /* ==========================================================================
       15. SYNCHRONOUS RUNTIME INTERFACE INGEST BOOT INITIALIZATION INITIALIZER
       ========================================================================== */
    const initUpload = () => {
        if (!cacheElements()) return; // Quietly terminate system layers when context framework targets verify missing profiles

        initDragAndDropArchitecture();
        initClipboardPasteSupport();
        initEventBridges();
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initUpload);
    } else {
        initUpload();
    }
})();