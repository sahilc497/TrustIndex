import React, { useState } from 'react';
import { FileText, CheckCircle2, AlertTriangle, XCircle, ChevronDown, ChevronUp, X } from 'lucide-react';

export default function EvidencePanel({
  claims = [],
  selectedClaimIdx,
  selectedEvidenceId,
  onClearSelection
}) {
  const [showTechnical, setShowTechnical] = useState(false);

  // If nothing is selected, default to first claim if available
  let activeClaim = null;
  let activeEdges = [];

  const effectiveClaimIdx = selectedClaimIdx !== null ? selectedClaimIdx : (claims.length > 0 ? 0 : null);

  if (effectiveClaimIdx !== null && claims[effectiveClaimIdx]) {
    activeClaim = claims[effectiveClaimIdx];
    activeEdges = activeClaim.evidence || [];
  } else if (selectedEvidenceId) {
    claims.forEach(c => {
      (c.evidence || []).forEach(e => {
        const key = `${e.doc}::${e.text.slice(0, 40)}`;
        if (key === selectedEvidenceId) {
          activeEdges.push(e);
          if (!activeClaim) activeClaim = c;
        }
      });
    });
  }

  if (activeEdges.length === 0) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs text-center text-slate-500 text-xs">
        No evidence passages available for inspection.
      </div>
    );
  }

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div>
          <h3 className="text-sm font-bold text-slate-900">
            Why did TRUST Index assign this score?
          </h3>
          <p className="text-xs text-slate-500 mt-0.5">
            {activeClaim ? `Evidence comparison for: "${activeClaim.claim}"` : 'Retrieved evidence comparison'}
          </p>
        </div>

        {selectedClaimIdx !== null && (
          <button
            onClick={onClearSelection}
            className="text-xs text-slate-400 hover:text-slate-600 p-1"
            title="Reset to default selection"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* 3 Simple Cards for the Professor */}
      <div className="space-y-3">
        {activeEdges.map((edge, idx) => {
          const isEntailment = edge.label === 'ENTAILMENT';
          const isContradiction = edge.label === 'CONTRADICTION';

          let relationshipLabel = 'NEUTRAL / UNRELATED';
          let relationshipStyle = 'bg-slate-50 text-slate-700 border-slate-200';
          let relationshipIcon = AlertTriangle;

          if (isEntailment) {
            relationshipLabel = 'SUPPORTS CLAIM';
            relationshipStyle = 'bg-emerald-50 text-emerald-800 border-emerald-300';
            relationshipIcon = CheckCircle2;
          } else if (isContradiction) {
            relationshipLabel = 'CONTRADICTS CLAIM';
            relationshipStyle = 'bg-rose-50 text-rose-800 border-rose-300';
            relationshipIcon = XCircle;
          }

          const RelIcon = relationshipIcon;
          const simPct = Math.round((edge.similarity || 0) * 100);

          return (
            <div key={idx} className="border border-slate-200 rounded-lg p-4 bg-slate-50/50 space-y-3">
              {/* Top row: 3 key metrics cards */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                {/* 1. Relationship */}
                <div className={`p-2.5 rounded-lg border flex flex-col justify-between ${relationshipStyle}`}>
                  <span className="text-[10px] font-semibold uppercase tracking-wider opacity-75">
                    Relationship
                  </span>
                  <div className="flex items-center gap-1.5 mt-1 font-bold text-xs sm:text-sm">
                    <RelIcon className="w-4 h-4 shrink-0" />
                    <span>{relationshipLabel}</span>
                  </div>
                </div>

                {/* 2. Similarity */}
                <div className="p-2.5 rounded-lg bg-white border border-slate-200 flex flex-col justify-between">
                  <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                    Text Relevance
                  </span>
                  <div className="mt-1 flex items-baseline gap-1">
                    <span className="text-lg font-bold text-slate-800">{simPct}%</span>
                    <span className="text-xs text-slate-400">similarity</span>
                  </div>
                </div>

                {/* 3. Source Document */}
                <div className="p-2.5 rounded-lg bg-white border border-slate-200 flex flex-col justify-between">
                  <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider">
                    Document Source
                  </span>
                  <div className="mt-1 flex items-center gap-1 text-xs font-semibold text-slate-700 truncate">
                    <FileText className="w-3.5 h-3.5 text-blue-600 shrink-0" />
                    <span className="truncate">{edge.doc}</span>
                  </div>
                </div>
              </div>

              {/* Verbatim Evidence Passage */}
              <div className="bg-white p-3 rounded-lg border border-slate-200 space-y-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 block">
                  Evidence Found in Policy Document:
                </span>
                <p className="text-xs text-slate-800 italic leading-relaxed">
                  "{edge.text}"
                </p>
              </div>

              {/* Plain English Reason */}
              {edge.reason && (
                <div className="text-xs text-slate-600">
                  <span className="font-semibold text-slate-800">Explanation:</span> {edge.reason}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Expandable Technical Details */}
      <div className="pt-2 border-t border-slate-100">
        <button
          onClick={() => setShowTechnical(!showTechnical)}
          className="text-xs text-slate-500 hover:text-slate-800 font-medium flex items-center justify-between w-full"
        >
          <span>Technical Parameters (SBERT & NLI)</span>
          {showTechnical ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>

        {showTechnical && (
          <div className="mt-2 p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-600 space-y-1 animate-fade-in font-mono text-[11px]">
            {activeEdges.map((e, i) => (
              <div key={i} className="flex justify-between border-b border-slate-200/60 pb-1 last:border-b-0">
                <span>Passage {i + 1}: sim={e.similarity?.toFixed(3)}</span>
                <span className="font-semibold text-slate-800">NLI={e.label}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
