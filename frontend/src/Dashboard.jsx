import React, { useState, useEffect, useRef, useCallback } from 'react';
import { getStatus, exportVariant, exportPack, exportGlobal, transcreatePreview, API_BASE } from './api';
import { Pencil, X, Check, Type, Palette, Eye, Loader2, Wand2, ChevronRight, Heart, MessageCircle, Send, Bookmark, MoreHorizontal, User, Upload, Globe } from 'lucide-react';

const RATIOS = [
  { id: '1x1', name: 'SQUARE', desc: 'Instagram / Facebook Post (1080x1080)', width: 1080, height: 1080 },
  { id: '9x16', name: 'STORY', desc: 'Insta Story / Reels (1080x1920)', width: 1080, height: 1920 },
  { id: '4x5', name: 'PORTRAIT', desc: 'Social Feed (1080x1350)', width: 1080, height: 1350 },
  { id: '16x9', name: 'LANDSCAPE', desc: 'YouTube / Twitter (1920x1080)', width: 1920, height: 1080 },
  { id: '1.91x1', name: 'LINK PREVIEW', desc: 'LinkedIn / Link Share (1200x628)', width: 1200, height: 628 }
];

const getContrastColor = (hexcolor) => {
  if (!hexcolor) return '#1e293b'; // Default dark if nothing
  hexcolor = hexcolor.replace("#", "");
  if (hexcolor.length === 3) {
      hexcolor = hexcolor.split('').map(c => c + c).join('');
  }
  // Very rough check for rgba or other formats, we'll strip them just in case
  if (hexcolor.length !== 6 && hexcolor.length !== 8) return '#1e293b'; 

  const r = parseInt(hexcolor.substr(0, 2), 16) || 255;
  const g = parseInt(hexcolor.substr(2, 2), 16) || 255;
  const b = parseInt(hexcolor.substr(4, 2), 16) || 255;
  const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000;
  return (yiq >= 128) ? '#1e293b' : '#ffffff'; // returns dark text if bright bg
};

const MockupWrapper = ({ ratio, isSimulator, children }) => {
  if (!isSimulator) return <div className="rounded-2xl border border-slate-200 shadow-xl overflow-hidden">{children}</div>;

  if (ratio.id === '9x16') {
    return (
      <div className="relative mx-auto rounded-[3rem] border-[12px] border-slate-900 shadow-2xl overflow-hidden bg-black scale-90" 
           style={{ width: '360px', height: '640px' }}>
        {/* Notch / Dynamic Island */}
        <div className="absolute top-1 left-1/2 -translate-x-1/2 w-24 h-6 bg-black rounded-full z-30" />
        
        {/* Status Bar */}
        <div className="absolute top-0 left-0 w-full h-8 flex items-center justify-between px-8 z-20 text-white text-[10px] font-bold">
            <span>9:41</span>
            <div className="flex gap-1.5 items-center">
                <span className="w-4 h-2.5 border border-white/40 rounded-sm" />
                <span className="w-3 h-3 bg-white/40 rounded-full" />
            </div>
        </div>
        {/* Story Progress Bar */}
        <div className="absolute top-12 left-0 w-full flex gap-1 px-4 z-20">
            <div className="h-[2.5px] flex-1 bg-white/20 rounded-full overflow-hidden">
                <div className="h-full bg-white w-2/3 animate-pulse" />
            </div>
            <div className="h-[2.5px] flex-1 bg-white/20 rounded-full" />
        </div>
        {/* Profile Info */}
        <div className="absolute top-16 left-0 w-full flex items-center gap-2 px-4 z-20">
            <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-yellow-400 via-rose-500 to-purple-600 border-[1.5px] border-white p-[1.5px]">
                <div className="w-full h-full rounded-full bg-slate-300 overflow-hidden">
                    <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=AdMorph" alt="avatar" />
                </div>
            </div>
            <div className="flex flex-col">
                <span className="text-white text-[12px] font-black shadow-sm flex items-center gap-1">AdMorph.ai <Check size={10} className="bg-blue-500 rounded-full p-0.5" /></span>
                <span className="text-white/80 text-[10px] font-bold">Sponsored</span>
            </div>
        </div>
        {/* Content */}
        <div className="w-full h-full">
            {children}
        </div>
        {/* Story Footer */}
        <div className="absolute bottom-8 left-0 w-full flex items-center justify-between px-4 z-20">
            <div className="flex-1 h-12 border border-white/30 rounded-full bg-white/10 backdrop-blur-xl flex items-center px-5">
                <span className="text-white/70 text-sm font-medium">Send message...</span>
            </div>
            <div className="flex gap-4 ml-4 text-white/70">
                <Heart size={18} />
                <Send size={18} />
            </div>
        </div>
      </div>
    );
  }
  
  if (ratio.id === '1x1') {
    return (
        <div className="bg-white border border-slate-200 rounded-2xl shadow-2xl overflow-hidden max-w-[420px] scale-95 origin-top">
             {/* Insta Post Header */}
             <div className="flex items-center gap-3 p-4">
                 <div className="w-9 h-9 rounded-full bg-slate-200 overflow-hidden">
                     <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Brand" alt="avatar" />
                 </div>
                 <div className="flex flex-col">
                    <span className="text-sm font-black text-slate-900 block leading-tight">AdMorph Campaign </span>
                    <span className="text-[11px] text-slate-500 font-bold tracking-tight">Promoted Content</span>
                 </div>
                 <button className="ml-auto text-slate-900 font-black text-lg pb-2 hover:bg-slate-50 w-8 h-8 flex items-center justify-center rounded-full transition-colors">•••</button>
             </div>
             {/* Content */}
             <div className="aspect-square bg-slate-50 relative">
                 {children}
                 <div className="absolute bottom-4 right-4 bg-black/60 backdrop-blur px-2 py-1 rounded text-[10px] text-white font-black tracking-widest uppercase">Sponsored</div>
             </div>
             {/* Insta Interaction Bar */}
             <div className="p-4">
                 <div className="flex gap-4 mb-3 text-slate-900">
                     <Heart size={24} className="cursor-pointer hover:scale-110 transition-transform" />
                     <MessageCircle size={24} className="cursor-pointer hover:scale-110 transition-transform" />
                     <Send size={24} className="cursor-pointer hover:scale-110 transition-transform" />
                     <Bookmark size={24} className="ml-auto cursor-pointer hover:scale-110 transition-transform" />
                 </div>
                 <p className="text-sm font-black text-slate-900 mb-1">Liked by <span className="text-slate-950 underline">marketing_pro</span> and 2,134 others</p>
                 <p className="text-[13px] text-slate-700 leading-relaxed">
                    <span className="font-black mr-2 text-slate-900">AdMorph.ai</span>
                    Revolutionizing product photography with Generative AI... This is the future of MNC-grade creative production. 🎬✨ 
                    <span className="text-indigo-600 font-bold ml-1 cursor-pointer">#AI #Marketing #Winner</span>
                 </p>
                 <span className="text-[11px] font-bold text-slate-400 mt-2 block uppercase tracking-wider">3 MINUTES AGO</span>
             </div>
        </div>
    );
  }

  if (ratio.id === '4x5') {
    return (
      <div className="bg-white border border-slate-200 rounded-3xl shadow-2xl overflow-hidden max-w-[420px] scale-95 origin-top">
           {/* FB/Insta Header */}
           <div className="flex items-center gap-3 p-4">
               <div className="w-10 h-10 rounded-full bg-slate-100 overflow-hidden">
                   <img src="https://api.dicebear.com/7.x/pixel-art/svg?seed=Feed" alt="avatar" />
               </div>
               <div className="flex flex-col">
                  <span className="text-sm font-black text-slate-900 leading-tight">AdMorph Global</span>
                  <span className="text-[10px] text-indigo-600 font-black tracking-widest uppercase">Sponsored</span>
               </div>
           </div>
           {/* Feed Content */}
           <div className="aspect-[4/5] bg-slate-50 relative overflow-hidden">
               {children}
           </div>
           {/* CTA Bar */}
           <div className="bg-slate-50 border-y border-slate-100 p-3 flex items-center justify-between px-4">
               <span className="text-[11px] font-black text-slate-700 tracking-tight uppercase">AdMorph.ai — Premium Design</span>
               <button className="bg-slate-900 text-white text-[9px] font-black px-4 py-2 rounded-lg uppercase tracking-widest">Learn More</button>
           </div>
      </div>
    );
  }

  if (ratio.id === '16x9') {
      return (
          <div className="relative rounded-xl border-[16px] border-slate-900 shadow-[0_50px_100px_-20px_rgba(0,0,0,0.5)] bg-black overflow-hidden scale-90" 
               style={{ width: '800px', height: '450px' }}>
               {/* Billboard Lamps */}
               <div className="absolute top-0 left-0 w-full h-8 flex justify-around px-20">
                   <div className="w-12 h-2 bg-slate-800 rounded-b-lg shadow-[0_10px_30px_rgba(255,255,255,0.2)]" />
                   <div className="w-12 h-2 bg-slate-800 rounded-b-lg shadow-[0_10px_30px_rgba(255,255,255,0.2)]" />
                   <div className="w-12 h-2 bg-slate-800 rounded-b-lg shadow-[0_10px_30px_rgba(255,255,255,0.2)]" />
               </div>

               {/* Billboard Main Content */}
               <div className="w-full h-full relative">
                   {children}
                   {/* Realistic Sheen / Glare */}
                   <div className="absolute inset-0 bg-gradient-to-tr from-white/5 via-transparent to-black/10 pointer-events-none" />
                   {/* Texture Overlay */}
                   <div className="absolute inset-0 opacity-[0.03] pointer-events-none overflow-hidden">
                       <div className="absolute inset-[-100%] bg-[url('https://www.transparenttextures.com/patterns/concrete-wall.png')] mix-blend-overlay" />
                   </div>
               </div>

               {/* Billboard Supports */}
               <div className="absolute bottom-[-100px] left-1/4 w-8 h-[100px] bg-gradient-to-r from-slate-900 to-slate-800 border-x border-slate-700 shadow-2xl" />
               <div className="absolute bottom-[-100px] right-1/4 w-8 h-[100px] bg-gradient-to-r from-slate-900 to-slate-800 border-x border-slate-700 shadow-2xl" />
          </div>
      );
  }

  // Fallback Modern Card
  return <div className="rounded-2xl border-[8px] border-slate-100 shadow-2xl overflow-hidden bg-white">{children}</div>;
};

function RenderingStatus({ sessionId, ratioId }) {
  const [status, setStatus] = useState('PREPARING_ENGINE');

  useEffect(() => {
    const eventSource = new EventSource(`${API_BASE}/render-status/${sessionId}/${ratioId}`);
    
    eventSource.onmessage = (event) => {
      if (event.data === 'COMPLETED') {
        eventSource.close();
      } else {
        setStatus(event.data);
      }
    };

    eventSource.onerror = () => {
      eventSource.close();
    };

    return () => eventSource.close();
  }, [sessionId, ratioId]);

  const statusMap = {
    'PREPARING_ENGINE': 'Preparing Engine...',
    'SYNCHRONIZING_AUDIO': 'Synchronizing Audio...',
    'FINALIZING_HTML': 'Finalizing Design Layer...',
    'COMPLETED': 'Ready',
  };

  return (
    <div className="flex flex-col items-center">
        <span className="text-[10px] font-black tracking-[0.3em] text-[var(--accent)] uppercase animate-pulse">
            {statusMap[status] || status}
        </span>
        <span className="text-[8px] font-bold text-slate-400 uppercase mt-2 tracking-widest">
            [LIVE BACKEND SIGNAL]
        </span>
    </div>
  );
}

// ─── Customize Modal ────────────────────────────────────────────────
function CustomizeModal({ sessionId, ratio, theme, headline, onSave, onClose }) {
  const [draft, setDraft] = useState({
    heading:         headline?.heading     || '',
    content:         headline?.content     || '',
    catchy_line:     headline?.catchy_line || '',
    cta:             'SHOP NOW',
    primary_color:   theme?.primary_color   || '#6366f1',
    secondary_color: theme?.secondary_color || '#818cf8',
    text_color:      theme?.text_color      || '#ffffff',
  });

  const iframeRef = useRef(null);
  const [iframeLoading, setIframeLoading] = useState(true);
  const [iframeSrc, setIframeSrc] = useState('');

  const buildSrc = useCallback((d) =>
    `${API_BASE}/render-html?session_id=${sessionId}` +
    `&theme_name=${encodeURIComponent(theme?.name)}` +
    `&ratio_id=${ratio.id}` +
    `&heading=${encodeURIComponent(d.heading)}` +
    `&content=${encodeURIComponent(d.content)}` +
    `&catchy_line=${encodeURIComponent(d.catchy_line)}` +
    `&vo=false&render_mode=static&_t=${Date.now()}`,
  [sessionId, theme?.name, ratio.id]);

  useEffect(() => { setIframeSrc(buildSrc(draft)); }, []); // eslint-disable-line

  // ── IN-CANVAS SYNC: Listen for messages from Iframe ──
  useEffect(() => {
    const handler = (e) => {
      if (e.data?.type === 'CANVAS_EDIT') {
        setDraft(prev => ({ ...prev, [e.data.field]: e.data.value }));
      }
    };
    window.addEventListener('message', handler);
    return () => window.removeEventListener('message', handler);
  }, []);

  // ── INSTANT PUSH: Sync text/colors TO iframe without reload ──
  const syncToIframe = (type, payload) => {
    if (iframeRef.current?.contentWindow) {
      iframeRef.current.contentWindow.postMessage({ type, ...payload }, '*');
    }
  };

  const handleTextChange = (field, val) => {
    setDraft(p => ({ ...p, [field]: val }));
    syncToIframe('UPDATE_TEXT', { field, value: val });
  };

  const handleColorChange = (field, val) => {
    const next = { ...draft, [field]: val };
    setDraft(next);
    syncToIframe('UPDATE_COLORS', { 
        colors: { primary: next.primary_color, secondary: next.secondary_color, text: next.text_color } 
    });
  };

  const panelW = 660, panelH = 530;
  const scaleW = panelW / ratio.width;
  const scaleH = panelH / ratio.height;
  const previewScale = Math.min(scaleW, scaleH, 0.52);

  const Field = ({ label, fieldKey, multiline = false }) => (
    <div className="flex flex-col gap-1.5">
      <label className="text-[9px] font-black text-slate-400 tracking-[0.25em] uppercase flex items-center gap-1">
        <ChevronRight size={10} className="text-violet-400" />{label}
      </label>
      {multiline ? (
        <textarea
          value={draft[fieldKey]}
          onChange={e => handleTextChange(fieldKey, e.target.value)}
          rows={3}
          className="w-full text-sm text-slate-800 bg-slate-50 border border-slate-200 rounded-xl px-3 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-violet-400 focus:border-violet-400 transition"
        />
      ) : (
        <input
          value={draft[fieldKey]}
          onChange={e => handleTextChange(fieldKey, e.target.value)}
          className="w-full text-sm text-slate-800 bg-slate-50 border border-slate-200 rounded-xl px-3 h-10 focus:outline-none focus:ring-2 focus:ring-violet-400 focus:border-violet-400 transition"
        />
      )}
    </div>
  );

  return (
    <div
      className="fixed inset-0 z-[1000] overflow-y-auto flex items-start justify-center"
      style={{ background: 'rgba(10,10,25,0.85)', backdropFilter: 'blur(20px)' }}
    >
      <div className="w-full max-w-[1160px] my-auto py-12 px-4">
        <div className="bg-[#f8fafc] rounded-[40px] shadow-2xl flex w-full overflow-hidden border border-white/20 min-h-[640px]">
          {/* ── Left: Controls ── */}
          <div className="w-[340px] shrink-0 flex flex-col gap-5 p-8 border-r border-slate-200 bg-white/80 backdrop-blur-md">
            <div className="flex items-center justify-between mb-2">
              <div>
                <h2 className="font-black text-xl text-slate-900 tracking-tight flex items-center gap-2">
                  <div className="w-2 h-6 bg-violet-500 rounded-full" /> Structure
                </h2>
                <p className="text-[10px] text-slate-400 font-bold tracking-widest uppercase mt-1">{theme?.name} &middot; {ratio.name}</p>
              </div>
              <button onClick={onClose} className="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 flex items-center justify-center transition"><X size={16} /></button>
            </div>

            <div className="space-y-4">
              <Field label="Catchy Line" fieldKey="catchy_line" />
              <Field label="Hero Headline" fieldKey="heading" />
              <Field label="Description" fieldKey="content" multiline />
              <Field label="Call to Action" fieldKey="cta" />
            </div>

            <div className="mt-4 pt-4 border-t border-slate-100">
              <label className="text-[10px] font-black text-slate-500 tracking-[0.2em] uppercase mb-4 block">Visual DNA</label>
              <div className="grid grid-cols-2 gap-3">
                {[
                  ['Primary', 'primary_color'], 
                  ['Secondary', 'secondary_color'], 
                  ['Text Color', 'text_color']
                ].map(([lbl, key]) => (
                  <div key={key} className="p-3 bg-slate-50 rounded-2xl border border-slate-100 flex flex-col gap-2">
                    <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider">{lbl}</span>
                    <div className="flex items-center gap-3">
                      <div className="relative w-8 h-8 rounded-lg overflow-hidden border border-white shadow-sm">
                        <input
                          type="color"
                          value={draft[key]}
                          onChange={(e) => handleColorChange(key, e.target.value)}
                          className="absolute inset-[-10px] w-[200%] h-[200%] cursor-pointer"
                        />
                      </div>
                      <span className="text-[10px] font-mono font-bold text-slate-600 uppercase">{draft[key]}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-auto pt-6 space-y-3">
              <button
                onClick={() => onSave(draft)}
                className="w-full bg-slate-900 text-white font-black text-xs tracking-[0.2em] uppercase py-4 rounded-2xl flex items-center justify-center gap-2 hover:bg-violet-600 transition-all hover:scale-[1.02] active:scale-95 shadow-xl shadow-violet-200"
              >
                <Check size={14} /> Commit Changes
              </button>
              <p className="text-[9px] text-center text-slate-400 font-bold tracking-[0.1em] uppercase">Edits Auto-Sync to Canvas</p>
            </div>
          </div>

          {/* ── Right: Preview ── */}
          <div className="flex-1 bg-[#f1f5f9] relative flex items-center justify-center p-12 overflow-hidden">
            <div className="absolute top-8 left-12 right-12 flex justify-between items-center text-[10px] font-black text-slate-300 tracking-[0.3em] uppercase">
                <span>Studio Engine v2.0</span>
                <span>Active Canvas Sync</span>
            </div>
            
            {/* Wrapper that actually takes up the scaled space so flex centering works */}
            <div style={{ 
              width: ratio.width * previewScale, 
              height: ratio.height * previewScale,
              position: 'relative',
              boxShadow: '0 40px 100px -20px rgba(0,0,0,0.25)',
              borderRadius: 24,
              overflow: 'hidden',
              background: '#fff'
            }}>
                <div style={{ 
                  width: ratio.width, 
                  height: ratio.height, 
                  transform: `scale(${previewScale})`, 
                  transformOrigin: 'top left',
                  position: 'absolute',
                  top: 0,
                  left: 0
                }}>
                  {iframeSrc && (
                    <iframe
                      ref={iframeRef}
                      src={iframeSrc}
                      onLoad={() => setIframeLoading(false)}
                      style={{ width: '100%', height: '100%', border: 'none' }}
                      title="Customize Preview"
                    />
                  )}
                </div>

                {iframeLoading && (
                  <div className="absolute inset-0 bg-white/80 backdrop-blur-sm flex flex-col items-center justify-center z-20">
                    <Loader2 className="animate-spin text-violet-500 mb-4" size={32} />
                    <span className="text-[10px] font-black tracking-widest text-slate-400 uppercase">Syncing...</span>
                  </div>
                )}
            </div>
            
            <div className="absolute bottom-10 flex gap-10 opacity-30 pointer-events-none">
                <div className="flex flex-col items-center gap-1">
                    <div className="w-8 h-8 rounded-full border-2 border-slate-400 flex items-center justify-center font-bold text-xs italic">A</div>
                    <span className="text-[8px] font-black tracking-widest uppercase">Studio Engine Active</span>
                </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Dashboard({ sessionId, onBack }) {
  const [data, setData] = useState({ headlines: [], themes: [], copy_objects: [] });
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState({}); // Tracking loading state per ratio id
  const [audioRequested, setAudioRequested] = useState({}); // {ratioId: bool}
  const [replaySeed, setReplaySeed] = useState({}); // {ratioId: timestamp} — forces iframe reload
  const [selectedVoice, setSelectedVoice] = useState('auto'); // voice name or 'auto'
  const [customizeTarget, setCustomizeTarget] = useState(null); // { ratio } when modal open
  const [variantOverrides, setVariantOverrides] = useState({}); // { ratioId: {heading, content, catchy_line} }
  const [hasPlayed, setHasPlayed] = useState({}); // {ratioId: bool}
  const [isSimulator, setIsSimulator] = useState(false);
  const [brandPalette, setBrandPalette] = useState(null); // { p: primary, s: secondary, a: accent }
  const [isBrandKitOpen, setIsBrandKitOpen] = useState(false);
  const [isExportingPack, setIsExportingPack] = useState(false);
  const [isExportingGlobal, setIsExportingGlobal] = useState(false);
  
  // Active Selections
  const [activeHeadline, setActiveHeadline] = useState(null);
  const [activeTheme, setActiveTheme] = useState(null);
  const [activeTab, setActiveTab] = useState('copy'); // 'copy' | 'themes'

  // Localization States
  const [selectedLang, setSelectedLang] = useState('English');
  const [localizedCache, setLocalizedCache] = useState({}); // { lang: {heading, content, catchy_line} }
  const [isTranslating, setIsTranslating] = useState(false);

  const WORLD_LANGS = ["English", "Spanish", "French", "German", "Japanese", "Portuguese", "Korean", "Hindi", "Arabic"];

  // Reactive Translation: Automatically translate whenever language OR headline changes
  useEffect(() => {
    if (selectedLang === 'English' || !activeHeadline) return;
    
    const lang = selectedLang;
    const cacheKey = `${activeHeadline.heading}_${lang}`;
    if (localizedCache[cacheKey]) return;

    const translate = async () => {
        setIsTranslating(true);
        try {
            const trans = await transcreatePreview(
                sessionId,
                activeHeadline.heading,
                activeHeadline.content,
                activeHeadline.catchy_line,
                lang
            );
            setLocalizedCache(prev => ({ ...prev, [cacheKey]: trans }));
        } catch (err) {
            console.error("Transcreation Preview Error:", err);
        } finally {
            setIsTranslating(false);
        }
    };
    
    translate();
  }, [selectedLang, activeHeadline, sessionId]);

  const handleLangChange = (lang) => {
    setSelectedLang(lang);
    // Translation is now handled by the useEffect for reactive consistency
  };

  // Loading Animation Cycler
  const [loadingStep, setLoadingStep] = useState(0);

  const loadingTexts = [
      "Analyzing Brand Psychology...",
      "Mapping Target Audience Demographics...",
      "Generating 10 Custom Premium Themes...",
      "Writing Persuasive Conversion Copy...",
      "Baking Multi-Agent Outputs into Render Engine...",
      "Synthesizing Liquid Glass Components...",
      "Finalizing MNC-Grade Aesthetics..."
  ];

  useEffect(() => {
      let stepInterval;
      if (loading) {
          stepInterval = setInterval(() => {
              setLoadingStep(s => (s + 1) % loadingTexts.length);
          }, 2500);
      }
      return () => clearInterval(stepInterval);
  }, [loading]);

  // ── Remove the old editRequested / postMessage sync (replaced by modal) ──

  useEffect(() => {
    let interval;
    const fetchData = async () => {
      if (isExportingPack) return; 
      try {
        const statusData = await getStatus(sessionId);
        
        setData(statusData);
        
        // Auto-select first items if not selected
        if (!activeHeadline && statusData.copy_objects?.length > 0) {
            setActiveHeadline(statusData.copy_objects[0]);
        }
        if (!activeTheme && statusData.themes?.length > 0) {
            setActiveTheme(statusData.themes[0]);
        }

        if (statusData.copy_objects?.length > 0 || statusData.themes?.length > 0) {
            setLoading(false);
            if (statusData.copy_objects?.length > 0 && statusData.themes?.length > 10) {
                // Only fully stop polling if we have a significant amount of data
                // Or we can just keep polling until interaction_complete is true
                if (statusData.interaction_complete) {
                   clearInterval(interval);
                }
            }
        }
      } catch (err) {
        console.error("Dashboard Fetch Error:", err);
      }
    };
    
    fetchData();
    interval = setInterval(fetchData, 3000); // Poll for slow generative data
    return () => clearInterval(interval);
  }, [sessionId, activeHeadline, activeTheme]);
  
  // Reset "played" status whenever the global theme or headline changes
  // This ensures a fresh "PLAY" button appears for the new design.
  useEffect(() => {
    setHasPlayed({});
  }, [activeTheme, activeHeadline]);

  if (loading && (!data.copy_objects?.length && !data.themes?.length)) {
    return (
      <div className="flex flex-col items-center justify-center p-20 min-h-[70vh]">
        <div className="relative w-40 h-40 mb-16 flex items-center justify-center">
           {/* Outer Ring */}
           <div className="absolute inset-0 border-[6px] border-slate-200 rounded-full shadow-[var(--clay-shadow-out)]"></div>
           
           {/* Spinning Progress Ring */}
           <div className="absolute inset-0 border-[6px] border-[var(--accent)] border-t-transparent rounded-full animate-spin"></div>
           
           {/* Inner Core */}
           <div className="absolute inset-4 liquid-glass shadow-[var(--clay-shadow-in)] rounded-full flex flex-col items-center justify-center overflow-hidden">
              <span className="font-black text-3xl text-[var(--accent)] animate-pulse tracking-tighter">AI</span>
           </div>
           
           {/* Glowing Background Auras */}
           <div className="absolute -inset-16 bg-cyan-400 blur-[80px] opacity-10 -z-10 rounded-full animate-pulse"></div>
           <div className="absolute -inset-24 bg-[var(--accent)] blur-[100px] opacity-[0.05] -z-10 rounded-full animate-[pulse_4s_infinite]" style={{animationDelay: "1s"}}></div>
        </div>
        
        <h2 className="text-4xl md:text-5xl font-black mb-6 text-slate-800 tracking-tighter drop-shadow-xl text-center">
           <span className="stylish-serif text-slate-400 font-medium mr-4">Orchestrating</span> 
           WORKSPACE
        </h2>
        
        <div className="h-8 flex items-center justify-center overflow-hidden w-full max-w-lg">
           <p 
              key={loadingStep} 
              className="text-sm md:text-base font-bold text-[var(--accent)] tracking-[0.2em] uppercase animate-in slide-in-from-bottom-5 fade-in duration-500 text-center"
           >
              {loadingTexts[loadingStep]}
           </p>
        </div>
        
        <div className="mt-12 flex gap-3">
           {loadingTexts.map((_, i) => (
               <div key={i} className={`h-2 rounded-full transition-all duration-700 ease-out ${i <= loadingStep ? 'w-10 bg-[var(--accent)] shadow-[0_0_15px_rgba(255,123,84,0.4)]' : 'w-3 bg-slate-300 shadow-[inset_1px_1px_3px_rgba(0,0,0,0.1)]'}`} />
           ))}
        </div>
      </div>
    );
  }

  const handleExport = async (ratioId) => {
    if (!activeTheme || !activeHeadline) return;
    
    // Use localized copy if available
    const cacheKey = `${activeHeadline.heading}_${selectedLang}`;
    const loc = localizedCache[cacheKey] || {};
    const h = loc.heading || activeHeadline.heading;
    const c = loc.content || activeHeadline.content;
    const cl = loc.catchy_line || activeHeadline.catchy_line;

    setExporting(prev => ({ ...prev, [ratioId]: true }));
    try {
        const result = await exportVariant(
            sessionId, 
            activeTheme.name, 
            ratioId, 
            h, c, cl,
            brandPalette?.p,
            brandPalette?.s,
            brandPalette?.a
        );
        window.open(result.url, '_blank');
    } catch (err) {
        console.error("Export failed:", err);
        alert("Export failed. Make sure the backend is running properly.");
    } finally {
        setExporting(prev => ({ ...prev, [ratioId]: false }));
    }
  };

  const handleExportPack = async () => {
    if (!activeTheme || !activeHeadline) return;
    
    // Use localized copy if available
    const cacheKey = `${activeHeadline.heading}_${selectedLang}`;
    const loc = localizedCache[cacheKey] || {};
    const h = loc.heading || activeHeadline.heading;
    const c = loc.content || activeHeadline.content;
    const cl = loc.catchy_line || activeHeadline.catchy_line;

    setIsExportingPack(true);
    try {
        const result = await exportPack(
            sessionId,
            activeTheme.name,
            h, c, cl,
            brandPalette?.p,
            brandPalette?.s,
            brandPalette?.a
        );
        window.open(result.url, '_blank');
    } catch (err) {
        console.error("Pack export failed:", err);
        alert("Pack export failed. Make sure the backend is running properly.");
    } finally {
        setIsExportingPack(false);
    }
  };

  const handleExportGlobal = async () => {
    if (!activeTheme || !activeHeadline) return;
    // Note: handleExportGlobal always uses English original as input 
    // because the backend endpoint handles its own 8-language transcreation
    setIsExportingGlobal(true);
    try {
        const result = await exportGlobal(
            sessionId,
            activeTheme.name,
            activeHeadline.heading,
            activeHeadline.content,
            activeHeadline.catchy_line,
            brandPalette?.p,
            brandPalette?.s,
            brandPalette?.a
        );
        window.open(result.url, '_blank');
    } catch (err) {
        console.error("Global pack export failed:", err);
        alert("Global pack export failed. Make sure the backend is running properly.");
    } finally {
        setIsExportingGlobal(false);
    }
  };

  const renderSidebarItem = (item, type, index) => {
      const isActive = type === 'copy' ? (activeHeadline?.heading === item.heading) : (activeTheme?.name === item.name);
      
      return (
          <div 
            key={index}
            onClick={() => type === 'copy' ? setActiveHeadline(item) : setActiveTheme(item)}
            className={`p-5 mb-5 rounded-3xl border-4 transition-all duration-300 cursor-pointer ${
                isActive 
                    ? 'border-[#d5dce6] bg-[var(--bg-clay)] shadow-[var(--clay-shadow-in)]' 
                    : 'border-[#eef2f6] bg-[var(--bg-clay)] shadow-[var(--clay-shadow-btn)] hover:-translate-y-1'
            }`}
          >
              {type === 'copy' ? (
                  <>
                      <div className="text-[10px] text-[var(--accent)] font-bold tracking-widest uppercase mb-1">{item.catchy_line}</div>
                      <h4 className="font-bold text-sm mb-1 text-slate-800">{item.heading}</h4>
                      <p className="text-xs text-slate-500 line-clamp-2">{item.content}</p>
                  </>
              ) : (
                  <div className="flex items-center gap-4">
                      <div 
                         className="w-12 h-12 rounded-2xl border-2 border-white/40 shadow-lg shrink-0"
                         style={{ background: `linear-gradient(135deg, ${item.primary_color}, ${item.secondary_color})` }}
                      >
                         <div className="w-full h-full bg-white/10 backdrop-blur-[2px] rounded-2xl flex items-center justify-center text-[10px] font-black text-white/80 uppercase">
                            {item.name.substring(0, 2)}
                         </div>
                      </div>
                      <div className="flex-1">
                          <h4 className="font-black text-[11px] tracking-widest text-slate-800 uppercase leading-none mb-1">{item.name}</h4>
                          <div className="flex items-center gap-1.5">
                              <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent)] animate-pulse"></span>
                              <span className="text-[9px] text-slate-500 font-bold uppercase tracking-tight">{item.who_loves_it || 'Strategic Design'}</span>
                          </div>
                      </div>
                  </div>
              )}
          </div>
      )
  }

  return (
    <div className="flex flex-col h-[calc(100vh-120px)] pb-4">
      
      {/* Top Action Bar */}
      <div className="flex items-center justify-between pb-4 px-2">
          <div>
              <h2 className="text-xl font-black text-slate-800 drop-shadow-sm">Editor Workspace</h2>
              <p className="text-xs text-slate-500 font-mono mt-1 font-bold">
                  CURRENT THEME: <span className="text-[var(--accent)]">{activeTheme?.name || 'LOADING...'}</span>
              </p>
          </div>
          <div className="flex items-center gap-3">
               <button 
                  onClick={handleExportPack}
                  disabled={isExportingPack || isExportingGlobal}
                  className={`clay-btn py-2 px-6 text-[10px] tracking-[0.2em] uppercase flex items-center gap-2 group relative overflow-hidden ${isExportingPack ? 'opacity-70 grayscale' : 'bg-gradient-to-r from-emerald-500 to-teal-500 text-white border-emerald-400 shadow-xl hover:scale-105 active:scale-95 transition-all duration-300'}`}
              >
                  {isExportingPack ? (
                      <>
                          <Loader2 size={14} className="animate-spin" />
                          ARCHIVING...
                      </>
                  ) : (
                      <>
                          <div className="absolute inset-0 bg-white/20 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700 slant-glow" />
                          <span className="text-sm">📦</span> LOCALE PACK
                      </>
                  )}
              </button>

              <button 
                  onClick={handleExportGlobal}
                  disabled={isExportingPack || isExportingGlobal}
                  className={`clay-btn py-2 px-6 text-[10px] tracking-[0.2em] uppercase flex items-center gap-2 group relative overflow-hidden ${isExportingGlobal ? 'opacity-70 grayscale' : 'bg-gradient-to-r from-indigo-600 to-violet-600 text-white border-indigo-400 shadow-xl hover:scale-105 active:scale-95 transition-all duration-300'}`}
              >
                  {isExportingGlobal ? (
                      <>
                          <Loader2 size={14} className="animate-spin" />
                          GLOBAL TRANSCREATION...
                      </>
                  ) : (
                      <>
                          <div className="absolute inset-0 bg-white/20 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700 slant-glow" />
                          <Globe size={14} className="animate-pulse" /> 1-CLICK GLOBAL (.ZIP)
                      </>
                  )}
              </button>
              <button 
                  onClick={() => setIsBrandKitOpen(true)}
                  className="flex items-center gap-2 px-6 py-3 rounded-2xl bg-white text-slate-800 font-black text-xs tracking-widest border-2 border-slate-100 hover:border-[var(--accent)] hover:text-[var(--accent)] transition-all duration-300 shadow-xl overflow-hidden relative group"
              >
                  <Palette size={16} className="group-hover:rotate-12 transition-transform" />
                  MAGIC PALETTE
                  {brandPalette && <span className="bg-[var(--accent)] text-white px-1.5 py-0.5 rounded text-[8px]">ACTIVE</span>}
              </button>

              <button 
                  onClick={() => setIsSimulator(!isSimulator)}
                  className={`flex items-center gap-2 px-6 py-3 rounded-2xl font-black text-xs tracking-widest transition-all duration-300 shadow-xl overflow-hidden relative group ${
                      isSimulator 
                      ? 'bg-slate-900 text-white' 
                      : 'bg-white text-slate-900 border-2 border-slate-100 hover:border-[var(--accent)] hover:text-[var(--accent)]'
                  }`}
              >
                  <div className={`absolute inset-0 bg-gradient-to-r from-violet-600 to-indigo-600 transition-opacity duration-300 ${isSimulator ? 'opacity-100' : 'opacity-0'}`} />
                  <div className="relative flex items-center gap-2">
                      <Eye size={16} /> 
                      {isSimulator ? 'VIEW RAW DESIGN' : 'SIMULATE SOCIAL CONTEXT'}
                      {isSimulator && <span className="bg-white/20 px-1.5 py-0.5 rounded text-[8px]">PRO MODE</span>}
                  </div>
              </button>
              <button onClick={onBack} className="clay-btn bg-slate-200 text-slate-700 text-xs px-4 py-2 hover:bg-slate-300">
                  New Campaign
              </button>
          </div>
      </div>

       <div className="flex flex-1 overflow-hidden mt-6 gap-6">
          
          {/* LEFT SIDEBAR (Controls) */}
          <aside className="w-1/3 max-w-sm flex flex-col liquid-glass rounded-[40px] shadow-[var(--clay-shadow-out)] overflow-hidden relative z-20">
              
              <div className="flex w-full pt-2 px-2 gap-2">
                  <button 
                      className={`flex-1 py-4 text-xs font-bold tracking-widest uppercase transition-all duration-300 rounded-3xl border-4 ${activeTab === 'copy' ? 'text-[var(--accent)] border-[#d5dce6] shadow-[var(--clay-shadow-in)] bg-[var(--bg-clay)]' : 'text-slate-500 border-transparent hover:text-slate-700 shadow-[var(--clay-shadow-btn)] bg-[var(--bg-clay)] hover:-translate-y-1'}`}
                      onClick={() => setActiveTab('copy')}
                  >
                      Copy ({data.copy_objects?.length || 0})
                  </button>
                  <button 
                      className={`flex-1 py-4 text-xs font-bold tracking-widest uppercase transition-all duration-300 rounded-3xl border-4 ${activeTab === 'themes' ? 'text-[var(--accent)] border-[#d5dce6] shadow-[var(--clay-shadow-in)] bg-[var(--bg-clay)]' : 'text-slate-500 border-transparent hover:text-slate-700 shadow-[var(--clay-shadow-btn)] bg-[var(--bg-clay)] hover:-translate-y-1'}`}
                      onClick={() => setActiveTab('themes')}
                  >
                      Themes ({data.themes?.length || 0})
                  </button>
              </div>

              <div className="overflow-y-auto flex-1 p-6 hide-scrollbar mt-4">
                  {activeTab === 'copy' 
                      ? data.copy_objects.map((item, idx) => renderSidebarItem(item, 'copy', idx))
                      : data.themes.map((item, idx) => renderSidebarItem(item, 'themes', idx))
                  }
              </div>
          </aside>

          {/* MAIN CANVAS (Preview) */}
          <main className="flex-1 overflow-y-auto p-4 hide-scrollbar">
              <div className="max-w-4xl mx-auto space-y-12">

                  {/* 🌍 GLOBALIZATION PREVIEW BAR */}
                  <div className="liquid-glass p-2 rounded-full border-2 border-white/50 shadow-lg flex items-center justify-between gap-4 mb-4">
                      <div className="flex items-center gap-3 pl-4">
                          <Globe size={18} className="text-violet-500 animate-[spin_10s_linear_infinite]" />
                          <div>
                              <span className="text-[10px] font-black tracking-widest text-slate-400 uppercase leading-none block">Universal Preview</span>
                              <span className="text-[9px] font-bold text-slate-500 uppercase">Live Transcreation Layer Active</span>
                          </div>
                      </div>
                      
                      <div className="flex gap-1 overflow-x-auto hide-scrollbar max-w-[60%]">
                          {WORLD_LANGS.map(lang => {
                              const isActive = selectedLang === lang;
                              return (
                                  <button
                                      key={lang}
                                      onClick={() => handleLangChange(lang)}
                                      className={`px-4 py-2 rounded-full text-[10px] font-black uppercase tracking-widest transition-all duration-300 flex items-center gap-2 whitespace-nowrap ${
                                          isActive 
                                          ? 'bg-slate-900 text-white shadow-lg scale-105' 
                                          : 'text-slate-500 hover:bg-slate-100'
                                      }`}
                                  >
                                      {lang === 'English' && '🇺🇸'}
                                      {lang === 'Spanish' && '🇪🇸'}
                                      {lang === 'French' && '🇫🇷'}
                                      {lang === 'German' && '🇩🇪'}
                                      {lang === 'Japanese' && '🇯🇵'}
                                      {lang === 'Portuguese' && '🇵🇹'}
                                      {lang === 'Korean' && '🇰🇷'}
                                      {lang === 'Hindi' && '🇮🇳'}
                                      {lang === 'Arabic' && '🇸🇦'}
                                      {lang}
                                  </button>
                              )
                          })}
                      </div>

                      <div className="pr-4 flex items-center gap-2">
                        {isTranslating ? (
                            <div className="flex items-center gap-2">
                                <Loader2 size={14} className="animate-spin text-violet-500" />
                                <span className="text-[9px] font-black text-violet-500 uppercase animate-pulse">Adapting...</span>
                            </div>
                        ) : (
                            <div className="flex items-center gap-2 text-emerald-500">
                                <Check size={14} />
                                <span className="text-[9px] font-black uppercase">Localized</span>
                            </div>
                        )}
                      </div>
                  </div>

                  {/* Strategic Insight Box */}
                  {activeTheme && (
                      <div key={activeTheme.name} className="liquid-glass p-6 rounded-[32px] border-2 border-white/50 shadow-xl space-y-6 mb-12 animate-in fade-in slide-in-from-top-4 duration-500">
                          <div className="flex items-center justify-between">
                              <div className="flex items-center gap-3">
                                 <div className="w-10 h-10 rounded-2xl bg-[var(--accent)] flex items-center justify-center text-white shadow-lg">
                                     <Wand2 size={24} />
                                 </div>
                                 <div>
                                     <h3 className="text-sm font-black tracking-widest text-slate-800 uppercase">Strategic Insight // {activeTheme.name}</h3>
                                     <p className="text-[10px] font-bold text-slate-400 tracking-tighter uppercase">AI Art Director Analysis</p>
                                 </div>
                              </div>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                              <div className="space-y-2">
                                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">The Psychology</span>
                                  <p className="text-xs font-medium text-slate-600 leading-relaxed italic border-l-2 border-[var(--accent)]/30 pl-3">
                                      {activeTheme.why_it_works || `This style uses ${activeTheme.primary_color} to trigger specific neural responses for ${activeTheme.name}.`}
                                  </p>
                              </div>
                              <div className="space-y-2">
                                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">Optimal Channels</span>
                                  <p className="text-xs font-bold text-[var(--accent)] bg-[var(--accent)]/5 px-2 py-1 rounded-lg inline-block">
                                      {activeTheme.best_for || 'Cross-Platform Display'}
                                  </p>
                              </div>
                              <div className="space-y-2">
                                  <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">Target Persona</span>
                                  <p className="text-xs font-black text-slate-700">{activeTheme.who_loves_it || 'Engaged Consumers'}</p>
                              </div>
                          </div>
                      </div>
                  )}

                   {/* ─── NARRATOR VOICE SELECTOR ─── */}
                   <div className="clay-card p-6 mb-6">
                       <div className="flex items-center justify-between mb-4">
                           <div>
                               <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">AI Narrator Voice</span>
                               <p className="text-xs text-slate-500 mt-1">Select the voice used when you enable AI Narrative on any format</p>
                           </div>
                           {selectedVoice !== 'auto' && (
                               <button onClick={() => setSelectedVoice('auto')} className="text-[9px] font-black text-slate-400 hover:text-slate-600 uppercase tracking-widest">
                                   RESET TO AUTO
                               </button>
                           )}
                       </div>
                       <div className="flex gap-3 flex-wrap">
                           {[
                               { id: 'auto',                   label: 'Auto',         sub: 'Theme Default',   icon: <Palette size={14} />, gender: 'A' },
                               { id: 'en-US-EricNeural',       label: 'Eric',         sub: 'Professional',    icon: <User size={14} />, gender: 'M' },
                               { id: 'en-US-ChristopherNeural',label: 'Christopher',  sub: 'Authoritative',   icon: <User size={14} />, gender: 'M' },
                               { id: 'en-US-GuyNeural',        label: 'Guy',          sub: 'Deep & Digital',  icon: <User size={14} />, gender: 'M' },
                               { id: 'en-US-DavisNeural',      label: 'Davis',        sub: 'Bold & Clear',    icon: <User size={14} />, gender: 'M' },
                               { id: 'en-US-BrianNeural',      label: 'Brian',        sub: 'Rhythmic Edge',   icon: <User size={14} />, gender: 'M' },
                               { id: 'en-US-JennyNeural',      label: 'Jenny',        sub: 'Warm & Clean',    icon: <User size={14} />, gender: 'F' },
                               { id: 'en-US-AriaNeural',       label: 'Aria',         sub: 'Airy & Soft',     icon: <User size={14} />, gender: 'F' },
                               { id: 'en-GB-SoniaNeural',      label: 'Sonia',        sub: 'Luxury British',  icon: <User size={14} />, gender: 'F' },
                               { id: 'en-GB-RyanNeural',       label: 'Ryan',         sub: 'Bold British',    icon: <User size={14} />, gender: 'M' },
                           ].map(voice => {
                               const isSelected = selectedVoice === voice.id;
                               return (
                                   <button
                                       key={voice.id}
                                       onClick={() => setSelectedVoice(voice.id)}
                                       className={`flex flex-col items-start gap-1 px-3 py-2 rounded-xl border transition-all duration-200 text-left min-w-[90px] ${
                                           isSelected
                                               ? 'bg-[var(--accent)]/10 border-[var(--accent)] shadow-md scale-105'
                                               : 'bg-white border-slate-200 hover:border-slate-300 hover:shadow-sm'
                                       }`}
                                   >
                                       <div className="flex items-center gap-1.5 w-full">
                                           <span className="text-sm">{voice.icon}</span>
                                           <span className={`text-[9px] font-black tracking-wider px-1 rounded ${
                                               voice.gender === 'M' ? 'bg-blue-100 text-blue-600' :
                                               voice.gender === 'F' ? 'bg-rose-100 text-rose-600' :
                                               'bg-slate-100 text-slate-500'
                                           }`}>{voice.gender}</span>
                                           {isSelected && <span className="ml-auto animate-pulse flex h-1.5 w-1.5 rounded-full bg-[var(--accent)]" />}
                                       </div>
                                       <span className={`text-[11px] font-black ${isSelected ? 'text-[var(--accent)]' : 'text-slate-700'}`}>{voice.label}</span>
                                       <span className="text-[8px] text-slate-400 font-bold uppercase tracking-wider">{voice.sub}</span>
                                   </button>
                               );
                           })}
                       </div>
                   </div>

                    {RATIOS.map(ratio => {
                        const previewScale = ratio.width > 1200 ? 0.35 : 0.45;
                        const isAudio = !!audioRequested[ratio.id];
                        const ov = variantOverrides[ratio.id] || {};
                        
                        // Localization Fallback Logic
                        const cacheKey = `${activeHeadline?.heading}_${selectedLang}`;
                        const loc = localizedCache[cacheKey] || {};
                        
                        const h = loc.heading     || ov.heading     || activeHeadline?.heading     || '';
                        const c = loc.content     || ov.content     || activeHeadline?.content     || '';
                        const cl= loc.catchy_line  || ov.catchy_line  || activeHeadline?.catchy_line  || '';
                        
                        const voiceParam = selectedVoice !== 'auto' ? `&voice=${encodeURIComponent(selectedVoice)}` : '';
                        const seed = replaySeed[ratio.id] ? `&_t=${replaySeed[ratio.id]}` : '';
                        
                        const bp = brandPalette ? `&bp=${encodeURIComponent(brandPalette.p)}` : '';
                        const bs = brandPalette ? `&bs=${encodeURIComponent(brandPalette.s)}` : '';
                        const bt = brandPalette ? `&bt=${encodeURIComponent(brandPalette.a)}` : '';

                        const mode = (hasPlayed[ratio.id]) ? 'dynamic' : 'static';
                        
                        const src = `${API_BASE}/render-html?session_id=${sessionId}&theme_name=${encodeURIComponent(activeTheme?.name)}&ratio_id=${ratio.id}&heading=${encodeURIComponent(h)}&content=${encodeURIComponent(c)}&catchy_line=${encodeURIComponent(cl)}&vo=${isAudio}${voiceParam}&render_mode=${mode}${seed}${bp}${bs}${bt}&lang=${selectedLang}`;
                        
                        return (
                            <div key={ratio.id} className={`relative group flex flex-col items-center transition-all duration-500 ${isSimulator ? 'my-20' : ''}`}>
                                <div className={`mb-6 flex items-center justify-between w-full px-4 transition-all duration-300 ${isSimulator ? 'max-w-[1200px]' : 'max-w-[80%]'}`}>
                                    <div>
                                        <h3 className="text-xl font-bold tracking-widest text-slate-800 flex items-center gap-2">
                                            {ratio.name}
                                        </h3>
                                        <span className="text-xs text-slate-500 font-mono font-bold">{ratio.desc} | {ratio.id}</span>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <button 
                                           onClick={() => {
                                               setAudioRequested(prev => ({...prev, [ratio.id]: !prev[ratio.id]}));
                                           }}
                                           className={`clay-btn py-2 px-4 text-[10px] tracking-[0.2em] uppercase hover:scale-105 transition-all ${isAudio ? 'bg-emerald-50 text-emerald-600 border-emerald-200' : 'bg-slate-100 text-slate-500 border-slate-200'}`}
                                        >
                                            {isAudio ? '🔈 AI NARRATIVE ACTIVE' : '🔇 ENABLE AI NARRATIVE'}
                                        </button>
                                         <button 
                                            onClick={() => {
                                                // Mark as played so mode switches to dynamic
                                                setHasPlayed(prev => ({...prev, [ratio.id]: true}));
                                                
                                                // Bump seed → changes src → iframe truly reloads
                                                const ts = Date.now();
                                                setReplaySeed(prev => ({...prev, [ratio.id]: ts}));
                                                
                                                // After reload, send PLAY_AUDIO if narrative is active
                                                if (isAudio) {
                                                    setTimeout(() => {
                                                        const iframe = document.getElementById(`preview-frame-${ratio.id}`);
                                                        if (iframe) {
                                                            try { iframe.contentWindow.postMessage({ type: 'PLAY_AUDIO' }, '*'); } catch(_) {}
                                                        }
                                                    }, 800); // Wait for iframe to reload (seed change + onLoad)
                                                }
                                            }}
                                            className={`clay-btn py-2 px-4 text-[10px] tracking-[0.2em] uppercase hover:scale-105 transition-all ${!hasPlayed[ratio.id] ? 'bg-indigo-600 text-white border-indigo-500 shadow-xl' : 'bg-slate-100 text-slate-500 border-slate-200'}`}
                                         >
                                             {hasPlayed[ratio.id] ? '↺ REPLAY' : '▶ PLAY MOTION'}
                                         </button>
                                         <button
                                            onClick={() => setCustomizeTarget(ratio)}
                                            className="clay-btn py-2 px-4 text-[10px] tracking-[0.2em] uppercase hover:scale-105 transition-all bg-violet-50 text-violet-600 border-violet-200 hover:bg-violet-100 flex items-center gap-1.5"
                                         >
                                             {variantOverrides[ratio.id]
                                               ? <><Check size={11} /> CUSTOMIZED</>
                                               : <><Pencil size={11} /> CUSTOMIZE</>}
                                         </button>
                                        <button 
                                           onClick={() => handleExport(ratio.id)}
                                           disabled={exporting[ratio.id]}
                                           className={`clay-btn py-2 px-4 text-[10px] tracking-[0.2em] uppercase flex items-center gap-2 ${exporting[ratio.id] ? 'opacity-50' : 'hover:scale-105'}`}
                                        >
                                            {exporting[ratio.id] ? (
                                                <>
                                                    <span className="animate-spin rounded-full h-3 w-3 border-2 border-[var(--accent)] border-t-transparent" />
                                                    GENERATING STABLE ASSET...
                                                </>
                                            ) : (
                                                <>
                                                    <span className="text-sm">↓</span> EXPORT PNG
                                                </>
                                            )}
                                        </button>
                                    </div>
                                </div>

                                {/* Refined Timeline Logic: Moved outside the design area */}
                                <div className="w-full max-w-[80%] px-4 mb-2">
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="text-[8px] font-black text-slate-400 tracking-[0.3em] uppercase">Cinematic Timeline: 0:10s</span>
                                        <div className="flex items-center gap-2">
                                            <span className="animate-pulse flex h-1.5 w-1.5 rounded-full bg-emerald-400"></span>
                                            <span className="text-[8px] font-black text-emerald-500 tracking-[0.3em] uppercase">[VO_ENABLED]</span>
                                        </div>
                                    </div>
                                    <div className="w-full h-1 bg-slate-200 rounded-full overflow-hidden relative">
                                        <div className="h-full bg-[var(--accent)] animate-[loading_10s_linear_infinite]" style={{
                                            backgroundImage: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.4), transparent)'
                                        }} />
                                    </div>
                                </div>

                                <div className={`clay-card-inset p-8 flex items-center justify-center transition-all duration-300 overflow-hidden bg-slate-100/50 relative ${isSimulator ? 'max-w-[1200px] w-full' : 'max-w-[80%] w-full'}`}>
                                    <div className="relative overflow-hidden transition-all duration-500 transform">
                                        <MockupWrapper ratio={ratio} isSimulator={isSimulator}>
                                            <div 
                                                className="relative shadow-2xl transition-all duration-300 border border-white/10 overflow-hidden"
                                                style={{ 
                                                    width: ratio.width * (isSimulator ? (ratio.id === '1x1' ? 0.38 : (ratio.id === '9x16' ? 0.33 : (ratio.id === '4x5' ? 0.35 : 0.41))) : previewScale), 
                                                    height: ratio.height * (isSimulator ? (ratio.id === '1x1' ? 0.38 : (ratio.id === '9x16' ? 0.33 : (ratio.id === '4x5' ? 0.35 : 0.41))) : previewScale),
                                                    backgroundColor: '#fff'
                                                }}
                                            >
                                                {activeTheme && activeHeadline && (
                                                    <iframe 
                                                        id={`preview-frame-${ratio.id}`}
                                                        src={src} 
                                                        allow="autoplay"
                                                        style={{ 
                                                            width: ratio.width,
                                                            height: ratio.height,
                                                            border: 'none',
                                                            transform: `scale(${isSimulator ? (ratio.id === '1x1' ? 0.38 : (ratio.id === '9x16' ? 0.33 : (ratio.id === '4x5' ? 0.35 : 0.41))) : previewScale})`,
                                                            transformOrigin: 'top left',
                                                            pointerEvents: isAudio ? 'auto' : 'none',
                                                            opacity: 0,
                                                            transition: 'opacity 0.5s ease'
                                                        }}
                                                        title={`Preview ${ratio.name}`}
                                                        onLoad={(e) => {
                                                            e.target.style.opacity = 1;
                                                            if (e.target.nextSibling) {
                                                                e.target.nextSibling.style.display = 'none';
                                                            }
                                                            // Auto-trigger audio if narrative mode is active
                                                            if (isAudio) {
                                                                setTimeout(() => {
                                                                    try { e.target.contentWindow.postMessage({ type: 'PLAY_AUDIO' }, '*'); } catch(_) {}
                                                                }, 300); // Small delay to ensure iframe scripts are ready
                                                            }
                                                        }}
                                                    />
                                                )}
                                                
                                                {/* Loading Overlay with Live Status Steps */}
                                                <div className="absolute inset-0 flex items-center justify-center bg-slate-50/50 z-10 pointer-events-none">
                                                    <div className="flex flex-col items-center gap-4">
                                                        <div className="animate-spin rounded-full h-12 w-12 border-4 border-[var(--accent)] border-t-transparent shadow-lg" />
                                                        <RenderingStatus sessionId={sessionId} ratioId={ratio.id} />
                                                    </div>
                                                </div>
                                            </div>
                                        </MockupWrapper>
                                    </div>
                                </div>
                            </div>
                        );
                    })}

              </div>
          </main>
      </div>

      {/* ── Customize Modal ── */}
      {customizeTarget && (
          <CustomizeModal
              sessionId={sessionId}
              ratio={customizeTarget}
              theme={activeTheme}
              headline={{
                  ...(activeHeadline || {}),
                  ...(variantOverrides[customizeTarget.id] || {})
              }}
              onSave={(draft) => {
                  setVariantOverrides(prev => ({...prev, [customizeTarget.id]: draft}));
                  // Force the main iframe to reload with new content
                  setReplaySeed(prev => ({...prev, [customizeTarget.id]: Date.now()}));
                  setCustomizeTarget(null);
              }}
              onClose={() => setCustomizeTarget(null)}
          />
      )}
      {/* ── Brand Kit Modal ── */}
      <BrandKitModal 
          isOpen={isBrandKitOpen} 
          onClose={() => setIsBrandKitOpen(false)} 
          palette={brandPalette}
          setPalette={setBrandPalette}
      />

    </div>
  );
}

const BrandKitModal = ({ isOpen, onClose, palette, setPalette }) => {
    const [previewUrl, setPreviewUrl] = useState(null);
    const fileInputRef = useRef();

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const url = URL.createObjectURL(file);
        setPreviewUrl(url);

        const img = new Image();
        img.onload = () => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = 100; // Small sample size for speed
            canvas.height = 100;
            ctx.drawImage(img, 0, 0, 100, 100);
            const data = ctx.getImageData(0, 0, 100, 100).data;
            
            const colors = {};
            for (let i = 0; i < data.length; i += 4) {
                const r = data[i], g = data[i+1], b = data[i+2], a = data[i+3];
                if (a < 200) continue; // Transparency
                if (r > 240 && g > 240 && b > 240) continue; // White-ish bg
                if (r < 20 && g < 20 && b < 20) continue; // Black-ish bg
                
                // Grouping: round to nearest 16 to consolidate similar shades
                const gr = Math.round(r/16)*16;
                const gg = Math.round(g/16)*16;
                const gb = Math.round(b/16)*16;
                const hex = `#${((1 << 24) + (gr << 16) + (gg << 8) + gb).toString(16).slice(1)}`;
                colors[hex] = (colors[hex] || 0) + 1;
            }
            
            const sorted = Object.entries(colors).sort((a, b) => b[1] - a[1]);
            if (sorted.length > 0) {
                setPalette({
                    p: sorted[0]?.[0] || '#6366f1',
                    s: sorted[1]?.[0] || '#ec4899',
                    a: sorted[2]?.[0] || '#8b5cf6'
                });
            }
        };
        img.src = url;
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-slate-900/60 backdrop-blur-md animate-in fade-in duration-300">
            <div className="bg-white w-full max-w-xl rounded-[40px] shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300 border-4 border-white">
                <div className="p-8 space-y-8">
                    <div className="flex items-center justify-between">
                        <div>
                            <h2 className="text-2xl font-black text-slate-800 tracking-tight">Brand Kit // Magic Palette</h2>
                            <p className="text-xs text-slate-400 font-bold uppercase tracking-widest mt-1">Extract brand identity from your logo</p>
                        </div>
                        <button onClick={onClose} className="w-10 h-10 rounded-2xl bg-slate-50 flex items-center justify-center text-slate-400 hover:text-slate-600 transition-colors">
                            <X size={20} />
                        </button>
                    </div>

                    <div 
                        onClick={() => fileInputRef.current?.click()}
                        className="relative h-48 rounded-[32px] border-4 border-dashed border-slate-100 hover:border-[var(--accent)]/30 hover:bg-[var(--accent)]/5 transition-all cursor-pointer flex flex-col items-center justify-center group overflow-hidden"
                    >
                        {previewUrl ? (
                            <img src={previewUrl} className="h-4/5 object-contain" alt="Logo preview" />
                        ) : (
                            <>
                                <div className="w-16 h-16 rounded-3xl bg-slate-50 flex items-center justify-center text-slate-300 group-hover:scale-110 group-hover:bg-[var(--accent)] group-hover:text-white transition-all duration-300">
                                    <Upload size={32} />
                                </div>
                                <span className="text-sm font-black text-slate-400 mt-4 group-hover:text-slate-600 transition-colors text-center">
                                    DROP LOGO HERE OR <span className="text-[var(--accent)]">BROWSE</span>
                                </span>
                            </>
                        )}
                        <input ref={fileInputRef} type="file" className="hidden" accept="image/*" onChange={handleFileChange} />
                    </div>

                    {palette && (
                        <div className="space-y-6">
                            <div className="flex items-center gap-2">
                                <span className="w-2 h-2 rounded-full bg-emerald-400"></span>
                                <h3 className="text-[10px] font-black tracking-widest text-slate-500 uppercase">EXTRACTED IDENTITY</h3>
                            </div>
                            
                            <div className="grid grid-cols-3 gap-6">
                                {['p', 's', 'a'].map((key) => (
                                    <div key={key} className="space-y-3">
                                        <div 
                                            className="h-20 rounded-2xl shadow-inner relative group flex items-center justify-center overflow-hidden border-2 border-slate-50"
                                            style={{ backgroundColor: palette[key] }}
                                        >
                                            <input 
                                                type="color" 
                                                value={palette[key]} 
                                                onChange={(e) => setPalette({...palette, [key]: e.target.value})}
                                                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
                                            />
                                            <div className="bg-black/20 backdrop-blur-md opacity-0 group-hover:opacity-100 transition-opacity p-2 rounded-xl text-[10px] font-bold text-white uppercase">EDIT</div>
                                        </div>
                                        <div className="px-1 text-center">
                                            <p className="text-[9px] font-black text-slate-400 uppercase tracking-tighter mb-1">
                                                {key === 'p' ? 'Primary' : key === 's' ? 'Secondary' : 'Accent'}
                                            </p>
                                            <code className="text-[10px] font-mono font-bold text-slate-800 bg-slate-100 px-1.5 py-0.5 rounded">{palette[key]}</code>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    <div className="flex items-center justify-between pt-4">
                        <button 
                            onClick={onClose}
                            className="text-[10px] font-black text-slate-400 hover:text-slate-600 uppercase tracking-widest pl-2"
                        >
                            CLOSE WITHOUT UPDATING
                        </button>
                        <button 
                            onClick={() => {
                                onClose();
                            }}
                            className="bg-slate-900 text-white px-8 py-4 rounded-2xl font-black text-xs tracking-widest shadow-xl hover:-translate-y-1 transition-all"
                        >
                            APPLY TO WORKSPACE
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};
