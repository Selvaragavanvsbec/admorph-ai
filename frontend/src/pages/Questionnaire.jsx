import React, { useState, useEffect } from 'react';
import { startCampaign, submitAnswer, axiosInstance } from '../api';

export default function Questionnaire({ onComplete }) {
  const [sessionId, setSessionId] = useState(null);
  const [question, setQuestion] = useState("What is the name of the product or service we are advertising?");
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(1);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [filePreview, setFilePreview] = useState(null);

  const totalSteps = 7;
  const isOptional = progress === totalSteps;
  const isImageQuestion = progress === totalSteps;

  const initializedRef = React.useRef(false);

  useEffect(() => {
    if (initializedRef.current) return;
    initializedRef.current = true;
    init();
  }, []);

  const init = async () => {
    // We don't set loading to true here anymore, so the 'Continue' button doesn't spin on mount
    try {
      const data = await startCampaign();
      setSessionId(data.session_id);
      // Only set question if it's different (usually it's the same first question)
      if (data.next_question && data.next_question !== question) {
        setQuestion(data.next_question);
      }
    } catch (err) {
      console.error("Silent init failed. Will retry on first submit.");
    }
  };

  const handleFileUpload = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await axiosInstance.post('/upload-image', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      return response.data.file_path;
    } catch (err) {
      console.error("Upload error:", err);
      return null;
    }
  };

  const handleAction = async (forcedAnswer = null) => {
    let finalAnswer = forcedAnswer !== null ? forcedAnswer : (answer.trim() || 'skip');
    
    setLoading(true);
    try {
      let currentSessionId = sessionId;
      
      // Lazy init if sessionId is missing (e.g. if silent init failed or was too slow)
      if (!currentSessionId) {
        const startData = await startCampaign();
        currentSessionId = startData.session_id;
        setSessionId(currentSessionId);
      }

      // If there's a file, upload it first
      if (selectedFile && isImageQuestion) {
        const uploadedPath = await handleFileUpload(selectedFile);
        if (uploadedPath) {
          finalAnswer = uploadedPath;
        }
      }

      const data = await submitAnswer(currentSessionId, finalAnswer);
      console.log("Answer Submitted. Progress:", data.progress, "Next:", data.next_question);
      if (data.status === 'complete') {
        onComplete(currentSessionId);
      } else {
        setQuestion(data.next_question);
        setAnswer('');
        setProgress(parseInt(data.progress.split('/')[0]));
      }
    } catch (err) {
      const msg = err.response?.data?.detail || "Failed to submit answer.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (loading) return;
    if (!isOptional && !answer.trim()) return;
    handleAction();
  };

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center p-10 clay-card border-red-500/50">
        <p className="text-red-500 font-bold mb-4">{error}</p>
        <button onClick={init} className="clay-btn clay-btn-primary">Try Again</button>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto mt-10 p-8 liquid-glass shadow-[var(--clay-shadow-out)] rounded-[40px] backdrop-blur-3xl animate-in fade-in slide-in-from-bottom-5">
      <div className="flex justify-between items-center mb-8">
        <h2 className="text-2xl font-bold text-slate-800">Strategy Phase</h2>
        <span className="text-sm font-bold text-slate-500">Step {progress} of {totalSteps}</span>
      </div>

      <div className="w-full bg-slate-200 h-2 rounded-full mb-10 overflow-hidden shadow-[inset_1px_1px_3px_rgba(0,0,0,0.1)]">
        <div 
          className="h-full bg-[var(--accent)] transition-all duration-500" 
          style={{ width: `${(progress / totalSteps) * 100}%` }}
        />
      </div>

      <p className="text-lg font-medium text-slate-700 mb-6 leading-relaxed">
        {question || "Waking up the Strategy Agent..."}
      </p>

      <form onSubmit={handleSubmit} className="space-y-6">
        {!isImageQuestion ? (
          <textarea
            className="clay-input min-h-[140px] resize-none"
            placeholder="Type your answer here..."
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            disabled={loading}
            autoFocus
          />
        ) : (
          <div className="space-y-4">
            <div className="flex flex-col gap-4 p-6 border-2 border-dashed border-slate-300 rounded-2xl bg-slate-50 hover:border-[var(--accent)] transition-colors">
              <p className="text-sm font-semibold text-center text-slate-500">
                Drag & drop or click to upload product image
              </p>
              <input 
                type="file" 
                accept="image/*"
                onChange={(e) => {
                  const file = e.target.files[0];
                  if (file) {
                    setSelectedFile(file);
                    setFilePreview(URL.createObjectURL(file));
                    setAnswer(''); // Clear URL if file is picked
                  }
                }}
                className="hidden" 
                id="file-upload"
              />
              <label 
                htmlFor="file-upload" 
                className="clay-btn bg-slate-200 text-slate-700 text-center cursor-pointer hover:bg-slate-300"
              >
                {selectedFile ? 'Change Image' : 'Select Local Image'}
              </label>
              
              {filePreview && (
                <div className="flex justify-center mt-2">
                  <img src={filePreview} alt="Preview" className="h-32 rounded-lg border border-slate-200 object-contain shadow-md" />
                </div>
              )}
            </div>

            <div className="relative flex items-center py-2">
              <div className="flex-grow border-t border-slate-300"></div>
              <span className="flex-shrink mx-4 text-slate-500 font-bold text-xs uppercase tracking-widest">or use url</span>
              <div className="flex-grow border-t border-slate-300"></div>
            </div>

            <input
              className="clay-input"
              placeholder="https://example.com/product-image.png"
              value={answer}
              onChange={(e) => {
                setAnswer(e.target.value);
                setSelectedFile(null);
                setFilePreview(null);
              }}
              disabled={loading}
            />
          </div>
        )}
        
        <div className="flex flex-col gap-3 mt-6">
          <button 
            type="submit" 
            className="clay-btn clay-btn-primary w-full flex items-center justify-center gap-2"
            disabled={loading || (!isOptional && !answer.trim() && !selectedFile)}
          >
            {loading ? (
              <span className="animate-spin rounded-full h-5 w-5 border-2 border-white/30 border-t-white" />
            ) : (isOptional && !answer.trim() && !selectedFile ? "Skip & Use AI Sourcing" : "Continue")}
          </button>
          
          {isImageQuestion && (
            <p className="text-xs font-semibold text-center text-slate-500 italic mt-2">
              Tip: Leaving this blank will let our AI Stylist scrape a relevant reference image.
            </p>
          )}
        </div>
      </form>
    </div>
  );
}
