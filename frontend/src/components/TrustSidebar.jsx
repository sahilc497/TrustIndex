import React, { useState } from 'react';
import { 
  ShieldCheck, 
  AlertTriangle, 
  AlertOctagon, 
  ChevronDown, 
  ChevronRight, 
  GitFork
} from 'lucide-react';
import EvidenceGraph from './EvidenceGraph';

export default function TrustSidebar({ verification, loading }) {
  const [graphExpanded, setGraphExpanded] = useState(true);
  const [expandedClaims, setExpandedClaims] = useState({});

  const toggleClaim = (idx) => {
    setExpandedClaims(prev => ({
      ...prev,
      [idx]: !prev[idx]
    }));
  };

  if (loading) {
    return (
      <aside className="w-full lg:w-96 border-l border-slate-800 bg-slate-900/60 p-6 flex flex-col items-center justify-center min-h-[500px]">
        <div className="w-12 h-12 border-4 border-blue-500/20 border-t-blue-500 rounded-full animate-spin mb-4"></div>
        <p className="text-sm text-slate-400 font-medium">Verifying claims with SBERT & NLI...</p>
        <p className="text-xs text-slate-500 mt-1">Calculating graph consensus & trust index</p>
      </aside>
    );
  }

  if (!verification) {
    return (
      <aside className="w-full lg:w-96 border-l border-slate-800 bg-slate-900/40 p-6 flex flex-col items-center justify-center text-center">
        <div className="w-14 h-14 rounded-2xl bg-slate-800/80 border border-slate-700 flex items-center justify-center mb-4 text-slate-400">
          <ShieldCheck className="w-7 h-7 text-slate-400" />
        </div>
        <h3 className="font-semibold text-slate-300 text-base mb-1">Verification Idle</h3>
        <p className="text-xs text-slate-500 max-w-xs">
          Submit a query or select a canned example on the left to trigger real-time trust scoring and claim verification.
        </p>
      </aside>
    );
  }

  const { trust_score, status, explanation, claims } = verification;

  // Status visual configurations
  let statusBadge = {
    bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
    icon: ShieldCheck,
    label: 'Trusted',
    color: '#10b981',
    barColor: 'from-emerald-500 to-teal-400',
  };

  if (status === 'Uncertain') {
    statusBadge = {
      bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
      icon: AlertTriangle,
      label: 'Uncertain',
      color: '#eab308',
      barColor: 'from-amber-500 to-yellow-400',
    };
  } else if (status === 'Hallucinated') {
    statusBadge = {
      bg: 'bg-rose-500/10 border-rose-500/30 text-rose-400',
      icon: AlertOctagon,
      label: 'Hallucinated',
      color: '#ef4444',
      barColor: 'from-rose-500 to-red-400',
    };
  }

  const StatusIcon = statusBadge.icon;

  return (
    <aside className="w-full lg:w-[440px] border-l border-slate-800 bg-slate-900/90 flex flex-col h-full overflow-y-auto">
      {/* Top Header */}
      <div className="p-5 border-b border-slate-800 flex items-center justify-between">
        <div>
          <h2 className="text-xs font-bold tracking-wider text-slate-400 uppercase">Verification Layer</h2>
          <span className="text-base font-bold text-slate-100 flex items-center gap-2 mt-0.5">
            TRUST Index
          </span>
        </div>
        <div className={`px-3 py-1 rounded-full border text-xs font-semibold flex items-center gap-1.5 ${statusBadge.bg}`}>
          <StatusIcon className="w-3.5 h-3.5" />
          {status}
        </div>
      </div>

      {/* Main Score Gauge */}
      <div className="p-6 border-b border-slate-800 bg-gradient-to-b from-slate-900 to-slate-950/60">
        <div className="flex items-baseline justify-between mb-2">
          <span className="text-xs font-medium text-slate-400">Weakest-Link Trust Score</span>
          <span className="text-3xl font-extrabold tracking-tight" style={{ color: statusBadge.color }}>
            {trust_score.toFixed(1)}%
          </span>
        </div>
        
        {/* Progress Bar */}
        <div className="w-full h-2.5 bg-slate-800 rounded-full overflow-hidden p-0.5">
          <div 
            className={`h-full rounded-full transition-all duration-700 bg-gradient-to-r ${statusBadge.barColor}`}
            style={{ width: `${Math.max(4, trust_score)}%` }}
          />
        </div>

        <div className="flex justify-between text-[10px] text-slate-500 mt-1.5 font-mono">
          <span>0 (Hallucinated)</span>
          <span>50 (Uncertain)</span>
          <span>80 (Trusted)</span>
        </div>

        {/* Prominent explanation banner when Uncertain or Hallucinated */}
        {status !== 'Trusted' && (
          <div className={`mt-4 p-3 rounded-lg border text-xs leading-relaxed ${status === 'Hallucinated' ? 'bg-rose-950/30 border-rose-800/50 text-rose-200' : 'bg-amber-950/30 border-amber-800/50 text-amber-200'}`}>
            <div className="font-semibold flex items-center gap-1.5 mb-1">
              <StatusIcon className="w-4 h-4 shrink-0" />
              <span>Flag Reason:</span>
            </div>
            <p className="text-slate-300">{explanation}</p>
          </div>
        )}

        {status === 'Trusted' && (
          <div className="mt-4 p-3 rounded-lg border bg-emerald-950/20 border-emerald-800/40 text-xs leading-relaxed text-emerald-200">
            <div className="font-semibold flex items-center gap-1.5 mb-1">
              <ShieldCheck className="w-4 h-4 shrink-0 text-emerald-400" />
              <span>Verified Factuality</span>
            </div>
            <p className="text-slate-300">{explanation}</p>
          </div>
        )}
      </div>

      {/* Collapsible Evidence Graph */}
      <div className="border-b border-slate-800">
        <button
          onClick={() => setGraphExpanded(!graphExpanded)}
          className="w-full p-4 flex items-center justify-between text-xs font-semibold text-slate-300 hover:bg-slate-800/50 transition-colors"
        >
          <span className="flex items-center gap-2">
            <GitFork className="w-4 h-4 text-blue-400" />
            Bipartite Consensus Graph
          </span>
          {graphExpanded ? <ChevronDown className="w-4 h-4 text-slate-400" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
        </button>

        {graphExpanded && (
          <div className="px-4 pb-4">
            <EvidenceGraph claims={claims} />
          </div>
        )}
      </div>

      {/* Per-Claim Breakdown */}
      <div className="p-4 flex-1">
        <h3 className="text-xs font-bold tracking-wider text-slate-400 uppercase mb-3 flex items-center justify-between">
          <span>Atomic Claims Breakdown</span>
          <span className="text-slate-500 font-normal">{claims?.length || 0} claims</span>
        </h3>

        <div className="space-y-3">
          {claims?.map((item, idx) => {
            const isExpanded = expandedClaims[idx] !== false; // default expanded
            const consensusScore = item.consensus;
            let consensusColor = 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
            if (consensusScore < 0) {
              consensusColor = 'text-rose-400 bg-rose-500/10 border-rose-500/20';
            } else if (consensusScore < 0.6) {
              consensusColor = 'text-amber-400 bg-amber-500/10 border-amber-500/20';
            }

            return (
              <div key={idx} className="border border-slate-800 bg-slate-950/40 rounded-lg overflow-hidden">
                <div 
                  onClick={() => toggleClaim(idx)}
                  className="p-3 cursor-pointer hover:bg-slate-800/30 flex items-start justify-between gap-3 transition-colors"
                >
                  <div className="flex-1">
                    <span className="text-[10px] font-mono text-slate-500 uppercase tracking-wider block mb-1">
                      Claim {idx + 1}
                    </span>
                    <p className="text-xs font-medium text-slate-200 leading-snug">
                      "{item.claim}"
                    </p>
                  </div>
                  <div className="flex flex-col items-end gap-1.5 shrink-0">
                    <span className={`text-[11px] font-mono font-bold px-2 py-0.5 rounded border ${consensusColor}`}>
                      {consensusScore > 0 ? `+${consensusScore}` : consensusScore}
                    </span>
                    {isExpanded ? <ChevronDown className="w-3.5 h-3.5 text-slate-500" /> : <ChevronRight className="w-3.5 h-3.5 text-slate-500" />}
                  </div>
                </div>

                {isExpanded && (
                  <div className="px-3 pb-3 pt-1 border-t border-slate-800/60 bg-slate-900/30 space-y-2">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                      Retrieved Evidence Alignments
                    </span>

                    {item.evidence?.map((edge, eIdx) => {
                      let tagColor = 'bg-slate-800 text-slate-300 border-slate-700';
                      if (edge.label === 'ENTAILMENT') tagColor = 'bg-emerald-950/40 text-emerald-300 border-emerald-800/50';
                      if (edge.label === 'CONTRADICTION') tagColor = 'bg-rose-950/40 text-rose-300 border-rose-800/50';

                      return (
                        <div key={eIdx} className="p-2.5 rounded bg-slate-950/60 border border-slate-800/80 text-[11px] space-y-1.5">
                          <div className="flex items-center justify-between">
                            <span className="font-mono text-slate-400 text-[10px] font-medium truncate max-w-[200px]">
                              {edge.doc}
                            </span>
                            <div className="flex items-center gap-2">
                              <span className="text-[10px] font-mono text-slate-500">
                                sim: {edge.similarity}
                              </span>
                              <span className={`px-1.5 py-0.5 rounded text-[10px] font-semibold uppercase border ${tagColor}`}>
                                {edge.label}
                              </span>
                            </div>
                          </div>
                          <p className="text-slate-400 italic text-[11px] line-clamp-2">
                            "{edge.text}"
                          </p>
                          <p className="text-slate-500 text-[10px]">
                            <span className="font-semibold text-slate-400">Diagnosis:</span> {edge.reason}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </aside>
  );
}
