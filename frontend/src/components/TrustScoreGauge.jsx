import React, { useState } from 'react';
import { 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  ChevronDown, 
  ChevronUp 
} from 'lucide-react';

export default function TrustScoreGauge({ verification }) {
  const [showTechnical, setShowTechnical] = useState(false);

  if (!verification) return null;

  const { trust_score = 0, status = 'Uncertain', explanation = '' } = verification;

  const isUncertain = status === 'Uncertain';
  const isHallucinated = status === 'Hallucinated';

  let statusConfig = {
    color: '#15803d', // green-700
    label: 'TRUSTED',
    badgeClass: 'bg-emerald-50 text-emerald-800 border-emerald-300',
    barColor: 'bg-emerald-600',
    icon: CheckCircle2,
    shortReason: 'Supported by retrieved policy evidence without contradiction.'
  };

  if (isUncertain) {
    statusConfig = {
      color: '#b45309', // amber-700
      label: 'UNCERTAIN',
      badgeClass: 'bg-amber-50 text-amber-800 border-amber-300',
      barColor: 'bg-amber-500',
      icon: AlertTriangle,
      shortReason: 'Contains ungrounded additions or lacks decisive evidence.'
    };
  } else if (isHallucinated) {
    statusConfig = {
      color: '#b91c1c', // red-700
      label: 'HALLUCINATED',
      badgeClass: 'bg-rose-50 text-rose-800 border-rose-300',
      barColor: 'bg-rose-600',
      icon: XCircle,
      shortReason: 'Contradicts facts documented in the retrieved evidence.'
    };
  }

  const StatusIcon = statusConfig.icon;
  const scoreValue = Math.round(trust_score);

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs flex flex-col justify-between h-full">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            Trust Decision
          </h3>
          <span className={`px-2.5 py-0.5 rounded-full border text-xs font-bold flex items-center gap-1 ${statusConfig.badgeClass}`}>
            <StatusIcon className="w-3.5 h-3.5" />
            <span>{statusConfig.label}</span>
          </span>
        </div>

        {/* Large Clean Score Display */}
        <div className="py-5 text-center">
          <div className="flex items-baseline justify-center gap-1">
            <span 
              className="text-5xl font-extrabold tracking-tight font-sans"
              style={{ color: statusConfig.color }}
            >
              {scoreValue}
            </span>
            <span className="text-xl font-medium text-slate-400">/ 100</span>
          </div>
          <p className="text-xs font-semibold text-slate-700 mt-1 uppercase tracking-wide">
            {statusConfig.label}
          </p>
          <p className="text-xs text-slate-500 mt-1 max-w-xs mx-auto">
            {explanation || statusConfig.shortReason}
          </p>
        </div>

        {/* Visual Threshold Bar */}
        <div className="space-y-1.5 px-2">
          <div className="w-full h-2.5 bg-slate-100 rounded-full overflow-hidden relative">
            {/* Markers */}
            <div className="absolute left-[50%] top-0 bottom-0 w-0.5 bg-white z-10" />
            <div className="absolute left-[80%] top-0 bottom-0 w-0.5 bg-white z-10" />
            
            {/* Active progress */}
            <div 
              className={`h-full rounded-full transition-all duration-700 ${statusConfig.barColor}`}
              style={{ width: `${Math.max(5, scoreValue)}%` }}
            />
          </div>

          <div className="flex justify-between text-[10px] font-medium text-slate-400">
            <span className="text-rose-700 font-semibold">0 Hallucinated</span>
            <span className="text-amber-700 font-semibold">50 Uncertain</span>
            <span className="text-emerald-700 font-semibold">80 Trusted</span>
            <span>100</span>
          </div>
        </div>
      </div>

      {/* Expandable Technical Details */}
      <div className="pt-4 mt-3 border-t border-slate-100">
        <button
          onClick={() => setShowTechnical(!showTechnical)}
          className="text-xs text-slate-500 hover:text-slate-800 font-medium flex items-center justify-between w-full"
        >
          <span>Scoring Method & Thresholds</span>
          {showTechnical ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
        </button>

        {showTechnical && (
          <div className="mt-2.5 p-3 rounded-lg bg-slate-50 border border-slate-200 text-xs text-slate-600 space-y-1.5 animate-fade-in">
            <p className="text-[11px]">
              <strong className="text-slate-800">Weakest-Link Principle:</strong> Overall Trust Score = <code className="bg-white px-1 py-0.5 rounded border border-slate-200 text-[10px]">min(claim_scores)</code>
            </p>
            <p className="text-[11px]">
              A single contradicted claim bounds the final score, preventing false-trust acceptances.
            </p>
            <div className="grid grid-cols-3 gap-1 pt-1 text-[10px] text-center font-mono">
              <span className="bg-white p-1 rounded border border-slate-200 text-rose-700">&lt;50: Hallucinated</span>
              <span className="bg-white p-1 rounded border border-slate-200 text-amber-700">50–79: Uncertain</span>
              <span className="bg-white p-1 rounded border border-slate-200 text-emerald-700">≥80: Trusted</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
