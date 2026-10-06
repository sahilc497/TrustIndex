import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  Play 
} from 'lucide-react';

import Header from './components/Header';
import PipelineStatus from './components/PipelineStatus';
import QueryPanel from './components/QueryPanel';
import TrustScoreGauge from './components/TrustScoreGauge';
import GeneratedAnswer from './components/GeneratedAnswer';
import EvidenceGraph from './components/EvidenceGraph';
import ClaimList from './components/ClaimList';
import EvidencePanel from './components/EvidencePanel';
import EvaluationDashboard from './components/EvaluationDashboard';
import InfoModal from './components/InfoModal';

import { DEMO_SCENARIOS } from './data/demoScenarios';

export default function App() {
  const [activeTab, setActiveTab] = useState('verifier'); // 'verifier' | 'evaluation'
  const [infoModalOpen, setInfoModalOpen] = useState(false);

  // Verification state
  const [query, setQuery] = useState('');
  const [forceHallucination, setForceHallucination] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(1);
  const [errorMessage, setErrorMessage] = useState(null);

  // Active results
  const [generatedAnswer, setGeneratedAnswer] = useState('');
  const [currentVerification, setCurrentVerification] = useState(null);

  // Synchronized selections
  const [selectedClaimIdx, setSelectedClaimIdx] = useState(null);
  const [selectedEvidenceId, setSelectedEvidenceId] = useState(null);

  // Step timer for loading animation
  useEffect(() => {
    let interval;
    if (loading) {
      interval = setInterval(() => {
        setLoadingStep(prev => (prev < 5 ? prev + 1 : prev));
      }, 300);
    }
    return () => clearInterval(interval);
  }, [loading]);

  // Main verification runner
  const runVerification = async (queryText, forceHallu, fallbackDemo = null) => {
    if (!queryText.trim()) return;

    setLoading(true);
    setLoadingStep(1);
    setErrorMessage(null);
    setSelectedClaimIdx(null);
    setSelectedEvidenceId(null);

    try {
      const resp = await fetch('http://127.0.0.1:8000/simulate-rag', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: queryText,
          force_hallucination: forceHallu,
        }),
      });

      if (!resp.ok) {
        throw new Error(`API HTTP ${resp.status}`);
      }

      const data = await resp.json();
      setGeneratedAnswer(data.generated_answer);
      setCurrentVerification(data.verification);
    } catch (err) {
      console.warn('Backend offline, using fallback scenario:', err.message);

      const matchedDemo = fallbackDemo || DEMO_SCENARIOS.find(d => 
        d.query.toLowerCase().trim() === queryText.toLowerCase().trim()
      );

      if (matchedDemo) {
        setGeneratedAnswer(matchedDemo.generated_answer);
        setCurrentVerification(matchedDemo.verification);
      } else {
        setErrorMessage(
          'Verification service is currently offline at http://127.0.0.1:8000. Please select one of the demo scenarios above or start the FastAPI backend.'
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSelectDemo = (demo) => {
    setQuery(demo.query);
    setForceHallucination(demo.expectedStatus === 'Hallucinated');
    runVerification(demo.query, demo.expectedStatus === 'Hallucinated', demo);
  };

  const handleSelectClaim = (idx) => {
    setSelectedClaimIdx(prev => (prev === idx ? null : idx));
    setSelectedEvidenceId(null);
  };

  const handleSelectEvidence = (evId) => {
    setSelectedEvidenceId(prev => (prev === evId ? null : evId));
    setSelectedClaimIdx(null);
  };

  const handleClearSelection = () => {
    setSelectedClaimIdx(null);
    setSelectedEvidenceId(null);
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans flex flex-col">
      {/* 1. Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenInfo={() => setInfoModalOpen(true)}
      />

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-6 space-y-6">
        {/* VIEW 1: Verification Console */}
        {activeTab === 'verifier' && (
          <div className="space-y-6">
            {/* 2. Simple Academic Introduction Card (Section 4) */}
            <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h2 className="text-base font-bold text-slate-900">
                  Verify whether an AI-generated answer is actually supported by retrieved evidence.
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Automated atomic claim extraction, passage alignment, and contradiction detection.
                </p>
              </div>

              {/* High-level workflow banner */}
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-600 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-lg shrink-0">
                <span className="text-blue-700">Question</span>
                <span>→</span>
                <span className="text-blue-700">AI Answer</span>
                <span>→</span>
                <span className="text-blue-700">Evidence</span>
                <span>→</span>
                <span className="text-emerald-700">Trust Decision</span>
              </div>
            </div>

            {/* 3. Query & Demo Selector */}
            <QueryPanel
              query={query}
              setQuery={setQuery}
              onVerify={(q, h) => runVerification(q, h)}
              loading={loading}
              forceHallucination={forceHallucination}
              setForceHallucination={setForceHallucination}
              onSelectDemo={handleSelectDemo}
            />

            {/* Error Message if any */}
            {errorMessage && (
              <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center justify-between gap-3 shadow-xs">
                <span>{errorMessage}</span>
                <button
                  onClick={() => runVerification(query, forceHallucination)}
                  className="px-3 py-1 bg-white border border-rose-300 rounded font-semibold text-rose-900 hover:bg-rose-100"
                >
                  Retry
                </button>
              </div>
            )}

            {/* Loading State */}
            {loading && (
              <div className="bg-white border border-slate-200 rounded-xl p-8 shadow-xs text-center space-y-3">
                <div className="w-8 h-8 border-3 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto" />
                <h4 className="text-sm font-bold text-slate-800">
                  Verifying Generated Answer...
                </h4>
                <div className="flex items-center justify-center gap-4 text-xs text-slate-500 font-medium">
                  <span className={loadingStep >= 1 ? 'text-emerald-700 font-semibold' : ''}>1. Claims</span>
                  <span>→</span>
                  <span className={loadingStep >= 2 ? 'text-emerald-700 font-semibold' : ''}>2. Evidence</span>
                  <span>→</span>
                  <span className={loadingStep >= 3 ? 'text-emerald-700 font-semibold' : ''}>3. Contradiction</span>
                  <span>→</span>
                  <span className={loadingStep >= 4 ? 'text-emerald-700 font-semibold' : ''}>4. Graph</span>
                  <span>→</span>
                  <span className={loadingStep >= 5 ? 'text-emerald-700 font-semibold' : ''}>5. Trust Score</span>
                </div>
              </div>
            )}

            {/* Active Verification Results */}
            {!loading && currentVerification && (
              <div className="space-y-6 animate-fade-in">
                {/* 4. Main Two-Column Result (Section 6) */}
                <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-stretch">
                  {/* Left Column: Generated Answer (7 cols) */}
                  <div className="md:col-span-7">
                    <GeneratedAnswer
                      answer={generatedAnswer}
                      claims={currentVerification.claims}
                      selectedClaimIdx={selectedClaimIdx}
                      onSelectClaim={handleSelectClaim}
                    />
                  </div>

                  {/* Right Column: Trust Decision (5 cols) */}
                  <div className="md:col-span-5">
                    <TrustScoreGauge verification={currentVerification} />
                  </div>
                </div>

                {/* 5. Evidence Section: "Why did TRUST Index assign this score?" (Section 9) */}
                <EvidencePanel
                  claims={currentVerification.claims}
                  selectedClaimIdx={selectedClaimIdx}
                  selectedEvidenceId={selectedEvidenceId}
                  onClearSelection={handleClearSelection}
                />

                {/* 6. Evidence Graph Centerpiece (Section 10) */}
                <EvidenceGraph
                  claims={currentVerification.claims}
                  selectedClaimIdx={selectedClaimIdx}
                  selectedEvidenceId={selectedEvidenceId}
                  onSelectClaim={handleSelectClaim}
                  onSelectEvidence={handleSelectEvidence}
                />

                {/* 7. Claim Verification Cards (Section 11) */}
                <ClaimList
                  claims={currentVerification.claims}
                  selectedClaimIdx={selectedClaimIdx}
                  onSelectClaim={handleSelectClaim}
                />

                {/* 8. Pipeline Status (Accessible Workflow) */}
                <PipelineStatus loading={loading} />
              </div>
            )}

            {/* Empty State when no query run yet */}
            {!loading && !currentVerification && (
              <div className="bg-white border border-slate-200 rounded-xl p-8 shadow-xs text-center space-y-4">
                <div className="w-12 h-12 rounded-xl bg-blue-50 border border-blue-200 flex items-center justify-center mx-auto text-blue-600">
                  <ShieldCheck className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-slate-900">
                    Ready to verify generated answers
                  </h3>
                  <p className="text-xs text-slate-500 mt-1 max-w-md mx-auto">
                    Select one of the demonstration scenarios above to observe how TRUST Index verifies atomic claims against retrieved evidence.
                  </p>
                </div>

                <div className="flex flex-wrap items-center justify-center gap-2 pt-2">
                  {DEMO_SCENARIOS.map((demo) => (
                    <button
                      key={demo.id}
                      onClick={() => handleSelectDemo(demo)}
                      className="px-3.5 py-2 rounded-lg bg-slate-50 hover:bg-slate-100 border border-slate-200 text-xs font-semibold text-slate-700 flex items-center gap-1.5 transition-colors"
                    >
                      <Play className="w-3 h-3 fill-current text-blue-600" />
                      <span>Run {demo.badge}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* VIEW 2: Empirical Research Results */}
        {activeTab === 'evaluation' && (
          <EvaluationDashboard />
        )}
      </main>

      {/* About / Methodology Modal */}
      <InfoModal
        isOpen={infoModalOpen}
        onClose={() => setInfoModalOpen(false)}
      />

      {/* Footer */}
      <footer className="border-t border-slate-200 bg-white py-4 mt-auto">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-slate-500">
          <span>TRUST Index: Explainable Trust Verification Framework for RAG</span>
          <span>Chapter 4 Experimental Results • Academic Prototype</span>
        </div>
      </footer>
    </div>
  );
}
