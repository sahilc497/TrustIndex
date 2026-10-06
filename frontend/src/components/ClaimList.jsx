import React, { useState } from 'react';
import { CheckCircle2, AlertTriangle, XCircle, ChevronDown, ChevronUp } from 'lucide-react';

export default function ClaimList({
  claims = [],
  selectedClaimIdx,
  onSelectClaim
}) {
  const [expandedDetails, setExpandedDetails] = useState({});

  if (!claims || claims.length === 0) return null;

  const toggleTechnical = (idx, e) => {
    e.stopPropagation();
    setExpandedDetails(prev => ({
      ...prev,
      [idx]: !prev[idx]
    }));
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-slate-100">
        <div>
          <h3 className="text-sm font-bold text-slate-900">
            Claim Verification
          </h3>
          <p className="text-xs text-slate-500">
            Evaluating each atomic claim extracted from the answer
          </p>
        </div>
        <span className="text-xs text-slate-500 font-medium">
          {claims.length} {claims.length === 1 ? 'Claim' : 'Claims'} Evaluated
        </span>
      </div>

      <div className="space-y-3">
        {claims.map((claimItem, idx) => {
          const consensus = claimItem.consensus;
          const isSelected = selectedClaimIdx === idx;

          let statusLabel = 'SUPPORTED';
          let StatusIcon = CheckCircle2;
          let badgeStyle = 'bg-emerald-50 text-emerald-800 border-emerald-300';
          let scoreNumber = 100;
          let simpleReason = 'Supported by evidence documented in the policy.';

          if (consensus < 0) {
            statusLabel = 'HALLUCINATED';
            StatusIcon = XCircle;
            badgeStyle = 'bg-rose-50 text-rose-800 border-rose-300';
            scoreNumber = 0;
            simpleReason = 'Contradicted by retrieved policy evidence.';
          } else if (consensus < 0.6) {
            statusLabel = 'UNCERTAIN';
            StatusIcon = AlertTriangle;
            badgeStyle = 'bg-amber-50 text-amber-800 border-amber-300';
            scoreNumber = 50;
            simpleReason = 'Contains ungrounded claims or lacks sufficient evidence.';
          }

          const primaryEdge = claimItem.evidence?.[0];
          const isExpanded = expandedDetails[idx];

          return (
            <div
              key={idx}
              onClick={() => onSelectClaim(idx)}
              className={`p-4 rounded-lg border cursor-pointer transition-all ${
                isSelected
                  ? 'bg-blue-50/40 border-blue-500 ring-1 ring-blue-500'
                  : 'bg-slate-50/50 border-slate-200 hover:border-slate-300 hover:bg-slate-50'
              }`}
            >
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="font-bold text-xs text-slate-900">
                  Claim {idx + 1}
                </span>

                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded text-xs font-bold border flex items-center gap-1 ${badgeStyle}`}>
                    <StatusIcon className="w-3.5 h-3.5" />
                    <span>{statusLabel}</span>
                  </span>
                  <span className="text-xs font-semibold text-slate-700 bg-white px-2 py-0.5 rounded border border-slate-200">
                    Trust: {scoreNumber} / 100
                  </span>
                </div>
              </div>

              <p className="text-sm font-medium text-slate-800 leading-snug mb-2">
                "{claimItem.claim}"
              </p>

              <div className="text-xs text-slate-600">
                <span className="font-semibold text-slate-700">Reason:</span> {primaryEdge?.reason || simpleReason}
              </div>

              {/* Technical toggle */}
              <div className="mt-2.5 pt-2 border-t border-slate-200/80 flex items-center justify-between text-xs">
                <button
                  type="button"
                  onClick={(e) => toggleTechnical(idx, e)}
                  className="text-[11px] text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1"
                >
                  <span>{isExpanded ? 'Hide technical metrics' : 'View technical details'}</span>
                  {isExpanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                </button>

                <span className="text-[11px] text-slate-400">
                  {claimItem.evidence?.length || 0} supporting passages
                </span>
              </div>

              {isExpanded && primaryEdge && (
                <div className="mt-2 p-2.5 rounded bg-white border border-slate-200 text-xs text-slate-600 font-mono text-[11px] space-y-1">
                  <div>Consensus score: {consensus > 0 ? `+${consensus}` : consensus}</div>
                  <div>Source doc: {primaryEdge.doc}</div>
                  <div>Semantic similarity: {(primaryEdge.similarity || 0).toFixed(3)}</div>
                  <div>NLI label: {primaryEdge.label}</div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
