import React, { useState } from 'react';
import Questionnaire from './pages/Questionnaire';
import Dashboard from './Dashboard';
import { startDevCampaign, axiosInstance } from './api';

export default function App() {
  const [stage, setStage] = useState('brief'); // brief, dashboard
  const [sessionId, setSessionId] = useState(null);
  const [devLoading, setDevLoading] = useState(false);
  const [serverStatus, setServerStatus] = useState('checking'); // checking , online, offline

  React.useEffect(() => {
    const checkServer = async () => {
       try {
          await axiosInstance.get('/health');
          setServerStatus('online');
       } catch (e) {
          setServerStatus('offline');
       }
    };
    checkServer();
    const interval = setInterval(checkServer, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleBriefComplete = (id) => {
    setSessionId(id);
    setStage('dashboard');
  };

  const handleDevMode = async () => {
    console.log("Triggering Dev Mode...");
    setDevLoading(true);
    try {
      const data = await startDevCampaign();
      console.log("Dev Mode Response:", data);
      setSessionId(data.session_id);
      setStage('dashboard');
    } catch (err) {
      console.error("Dev Mode Error:", err);
      alert("Dev Mode failed to start. Is the backend running?");
    } finally {
      setDevLoading(false);
    }
  };

  const reset = () => {
    setStage('brief');
    setSessionId(null);
  };

  return (
    <div className="min-h-screen pb-20">
      <nav className="px-8 py-4 flex justify-between items-center liquid-glass sticky top-0 z-50 transition-all duration-300">
        <div className="flex items-center gap-3 cursor-pointer" onClick={reset}>
           <div className="w-12 h-12 rounded-2xl flex items-center justify-center font-black text-2xl" style={{boxShadow: "var(--clay-shadow-out)", color: "var(--accent)"}}>A</div>
           <h1 className="text-3xl font-black tracking-tighter text-slate-800">AdMorph</h1>
        </div>
        
        <div className="hidden md:flex gap-8 text-sm font-bold tracking-widest text-[#a3b1c6]">
           <span className={stage === 'brief' ? 'text-slate-800 border-b-2 border-slate-800 pb-1' : ''}>1. BRIEF</span>
           <span className={stage === 'dashboard' ? 'text-slate-800 border-b-2 border-slate-800 pb-1' : ''}>2. WORKSPACE</span>
        </div>
        
        <div className="flex items-center gap-4">
           <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-100/50 border border-white text-[9px] font-bold tracking-tighter">
              <div className={`w-2 h-2 rounded-full ${serverStatus === 'online' ? 'bg-green-400' : serverStatus === 'offline' ? 'bg-red-400' : 'bg-amber-400 animate-pulse'}`} />
              SERVER: {serverStatus.toUpperCase()}
           </div>
           <button 
             onClick={handleDevMode}
             disabled={devLoading}
             className="clay-btn text-xs tracking-wider flex items-center gap-2"
           >
             {devLoading ? (
               <span className="animate-spin rounded-full h-3 w-3 border-2 border-[var(--accent)] border-t-transparent" />
             ) : null}
             DEV ENGINE TEST
           </button>
           <div className="text-[10px] font-mono text-slate-600">
              v2.0 // AGENTIC_SCALE_ENABLED
           </div>
        </div>
      </nav>

      {/* Decorative Clay Assets */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden flex items-center justify-center">
        <img 
           src="/clay_shapes.png" 
           className="absolute -top-32 -left-32 w-[600px] opacity-70 mix-blend-darken animate-[pulse_6s_infinite]" 
           alt="decoration" 
        />
        <img 
           src="/clay_shapes.png" 
           className="absolute -bottom-40 -right-40 w-[800px] opacity-60 mix-blend-darken animate-[bounce_8s_infinite] rotate-12" 
           alt="decoration" 
        />
      </div>

      <main className="container mx-auto px-4 pt-10 relative z-10">
        {stage === 'brief' && (
          <>
            <div className="max-w-3xl mx-auto space-y-12 mb-32">
              <div className="text-center space-y-6">
                 <h2 className="text-6xl md:text-8xl font-black tracking-tighter leading-[0.85] text-slate-800 drop-shadow-xl">
                   YOUR <span className="stylish-serif text-[var(--accent)] font-medium">AI Creative</span> WORKSPACE
                 </h2>
                 <p className="text-slate-500 text-lg max-w-xl mx-auto font-medium">
                   The intelligent design engine that transforms a simple brief into infinite, pixel-perfect, tailored campaign variations.
                 </p>
              </div>
              <Questionnaire onComplete={handleBriefComplete} />
            </div>

            {/* Landing Page Mock Sections */}
            <div className="max-w-5xl mx-auto space-y-32 pb-32">
              
              <section className="flex flex-col md:flex-row items-center gap-16">
                <div className="flex-1 space-y-6">
                  <h3 className="text-4xl font-black text-slate-800 leading-tight">Multiply Your Output <br/><span className="stylish-serif text-slate-500 font-medium">Without the headcount.</span></h3>
                  <p className="text-slate-500 text-lg font-medium leading-relaxed">Stop manually resizing, rewriting, and recoloring. AdMorph ingests your single creative thought and leverages multi-agent orchestrations to instantly map it across 10+ aspect ratios, 5+ global themes, and countless copy variations.</p>
                </div>
                <div className="flex-1 w-full relative">
                   <div className="clay-card aspect-video w-full flex items-center justify-center p-8 bg-[var(--accent)] text-white text-2xl font-black shadow-[var(--clay-shadow-out)] rotate-2 hover:rotate-0 transition-transform duration-500 relative z-10">
                      Auto-Render Engine Active
                   </div>
                   <div className="absolute top-4 left-4 clay-card aspect-video w-full bg-slate-300 -z-10 -rotate-3"></div>
                </div>
              </section>

              <section className="text-center space-y-16">
                 <h3 className="text-4xl font-black text-slate-800">Enterprise Capabilities</h3>
                 <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {[
                      { title: "Smart Theming", desc: "AI-driven color palettes mapped to emotional resonance." },
                      { title: "Dynamic Copy", desc: "Psychologically optimized headlines that convert instantly." },
                      { title: "Instant Export", desc: "One-click deployment to Meta, Google, and TikTok ad servers." }
                    ].map((feature, i) => (
                      <div key={i} className="clay-card-inset p-8 space-y-4 hover:-translate-y-2 transition-transform duration-300 cursor-pointer">
                         <div className="w-12 h-12 rounded-full bg-slate-200 border-2 border-white flex items-center justify-center shadow-[var(--clay-shadow-out)] text-slate-700 font-black">0{i+1}</div>
                         <h4 className="text-xl font-bold text-slate-800 text-left">{feature.title}</h4>
                         <p className="text-slate-500 font-medium text-left leading-relaxed">{feature.desc}</p>
                      </div>
                    ))}
                 </div>
              </section>

            </div>
          </>
        )}

        {stage === 'dashboard' && (
          <Dashboard 
            sessionId={sessionId} 
            onBack={reset}
          />
        )}
      </main>

      {stage !== 'brief' && (
        <button 
          onClick={() => window.scrollTo({top: 0, behavior: 'smooth'})}
          className="fixed bottom-10 right-10 w-12 h-12 clay-btn rounded-full flex items-center justify-center text-slate-800 transition-colors z-50 text-xl shadow-[var(--clay-shadow-out)]"
        >
          ↑
        </button>
      )}
    </div>
  );
}
