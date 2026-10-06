import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

const DETAILED_STAGES = [
  { id: 1, name: 'Passage Retrieval', desc: 'Sparse & Dense retrieval over documents' },
  { id: 2, name: 'Answer Generation', desc: 'Model generates candidate response' },
  { id: 3, name: 'Claim Extraction', desc: 'Answer split into atomic propositions' },
  { id: 4, name: 'Evidence Matching', desc: 'Semantic similarity alignment' },
  { id: 5, name: 'Contradiction Check', desc: 'Bidirectional NLI & numeric validation' },
  { id: 6, name: 'Trust Scoring', desc: 'Weakest-link consensus assignment' },
];

export default function PipelineStatus({ loading, currentStage = 6 }) {
  const [showTechnical, setShowTechnical] = useState(false);

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-2xs">
      {/* High-Level 4-Stage Workflow */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
        <div>
          <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
            Verification Workflow
          </h4>
          <p className="text-xs text-slate-500 mt-0.5">
            How TRUST Index verifies an AI-generated answer against evidence
          </p>
        </div>

        <button
          onClick={() => setShowTechnical(!showTechnical)}
          className="text-xs text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1 self-start sm:self-auto"
        >
          <span>{showTechnical ? 'Hide Technical Pipeline' : 'View Technical Pipeline'}</span>
          {showTechnical ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>
      </div>

      {/* 4 Steps Banner */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 pt-3">
        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200/80">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-800">
            <span className="w-4 h-4 rounded-full bg-blue-100 text-blue-700 text-[10px] font-bold flex items-center justify-center">1</span>
            <span>Retrieve</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Retrieve policy passages</p>
        </div>

        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200/80">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-800">
            <span className="w-4 h-4 rounded-full bg-blue-100 text-blue-700 text-[10px] font-bold flex items-center justify-center">2</span>
            <span>Generate</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Produce candidate answer</p>
        </div>

        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200/80">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-800">
            <span className="w-4 h-4 rounded-full bg-blue-100 text-blue-700 text-[10px] font-bold flex items-center justify-center">3</span>
            <span>Verify</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Compare claims with evidence</p>
        </div>

        <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200/80">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-800">
            <span className="w-4 h-4 rounded-full bg-blue-100 text-blue-700 text-[10px] font-bold flex items-center justify-center">4</span>
            <span>Trust</span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Assign explainable score</p>
        </div>
      </div>

      {/* Expandable Technical Pipeline */}
      {showTechnical && (
        <div className="mt-4 pt-3 border-t border-slate-100 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 text-xs">
          {DETAILED_STAGES.map((stg) => {
            const isProcessing = loading && currentStage === stg.id;
            return (
              <div 
                key={stg.id} 
                className={`p-2 rounded border ${
                  isProcessing 
                    ? 'bg-blue-50 border-blue-300 text-blue-900 font-medium' 
                    : 'bg-white border-slate-200 text-slate-600'
                }`}
              >
                <div className="text-[10px] font-mono text-slate-400">Step {stg.id}</div>
                <div className="font-semibold text-slate-800 text-[11px] mt-0.5">{stg.name}</div>
                <div className="text-[10px] text-slate-500 mt-0.5 leading-snug">{stg.desc}</div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
