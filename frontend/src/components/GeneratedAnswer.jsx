import React from 'react';

export default function GeneratedAnswer({ 
  answer = '', 
  claims = [], 
  selectedClaimIdx, 
  onSelectClaim 
}) {
  if (!answer) return null;

  // Split or match claims inside the generated answer text
  const renderHighlightedText = () => {
    if (!claims || claims.length === 0) {
      return <p className="text-sm text-slate-800 leading-relaxed">{answer}</p>;
    }

    let segments = [{ text: answer, claimIdx: null }];

    claims.forEach((claimItem, cIdx) => {
      const claimText = claimItem.claim.trim();
      const newSegments = [];

      segments.forEach((seg) => {
        if (seg.claimIdx !== null) {
          newSegments.push(seg);
          return;
        }

        const lowerSeg = seg.text.toLowerCase();
        const lowerClaim = claimText.toLowerCase();
        const matchIdx = lowerSeg.indexOf(lowerClaim);

        if (matchIdx !== -1) {
          const before = seg.text.slice(0, matchIdx);
          const matched = seg.text.slice(matchIdx, matchIdx + claimText.length);
          const after = seg.text.slice(matchIdx + claimText.length);

          if (before) newSegments.push({ text: before, claimIdx: null });
          newSegments.push({ text: matched, claimIdx: cIdx });
          if (after) newSegments.push({ text: after, claimIdx: null });
        } else {
          newSegments.push(seg);
        }
      });

      segments = newSegments;
    });

    const hasMatches = segments.some(s => s.claimIdx !== null);

    if (!hasMatches) {
      // Fallback
      return (
        <div className="space-y-3">
          <p className="text-base text-slate-800 leading-relaxed font-sans">
            "{answer}"
          </p>
          <div className="flex flex-wrap gap-2 pt-2 border-t border-slate-100">
            {claims.map((c, idx) => {
              const consensus = c.consensus;
              let style = 'bg-emerald-50 text-emerald-800 border-emerald-300';
              if (consensus < 0) {
                style = 'bg-rose-50 text-rose-800 border-rose-300';
              } else if (consensus < 0.6) {
                style = 'bg-amber-50 text-amber-800 border-amber-300';
              }

              const isSelected = selectedClaimIdx === idx;

              return (
                <button
                  key={idx}
                  type="button"
                  onClick={() => onSelectClaim(idx)}
                  className={`text-xs px-2.5 py-1 rounded border text-left transition-all ${style} ${
                    isSelected ? 'ring-2 ring-blue-500 font-semibold' : ''
                  }`}
                >
                  <span className="font-semibold mr-1">Claim {idx + 1}:</span>
                  "{c.claim}"
                </button>
              );
            })}
          </div>
        </div>
      );
    }

    return (
      <p className="text-base text-slate-800 leading-relaxed">
        {segments.map((seg, i) => {
          if (seg.claimIdx === null) {
            return <span key={i}>{seg.text}</span>;
          }

          const claimObj = claims[seg.claimIdx];
          const consensus = claimObj.consensus;
          const isSelected = selectedClaimIdx === seg.claimIdx;

          let highlightClass = 'bg-emerald-50 text-emerald-900 border-b-2 border-emerald-500 hover:bg-emerald-100';
          let badgeText = 'Supported';
          let badgeClass = 'bg-emerald-100 text-emerald-800';

          if (consensus < 0) {
            highlightClass = 'bg-rose-50 text-rose-900 border-b-2 border-rose-500 hover:bg-rose-100';
            badgeText = 'Contradicted';
            badgeClass = 'bg-rose-100 text-rose-800';
          } else if (consensus < 0.6) {
            highlightClass = 'bg-amber-50 text-amber-900 border-b-2 border-amber-500 hover:bg-amber-100';
            badgeText = 'Uncertain';
            badgeClass = 'bg-amber-100 text-amber-800';
          }

          return (
            <span
              key={i}
              onClick={() => onSelectClaim(seg.claimIdx)}
              title={`Click to inspect Claim ${seg.claimIdx + 1} (${badgeText})`}
              className={`cursor-pointer px-1 py-0.5 rounded transition-colors inline font-medium ${highlightClass} ${
                isSelected ? 'ring-2 ring-blue-500 rounded' : ''
              }`}
            >
              <span>{seg.text}</span>
              <span className={`inline-block ml-1 text-[10px] font-semibold px-1.5 py-0.2 rounded ${badgeClass}`}>
                Claim {seg.claimIdx + 1}
              </span>
            </span>
          );
        })}
      </p>
    );
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs flex flex-col justify-between h-full">
      <div>
        <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100">
          <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
            Generated Answer
          </h3>

          <div className="flex items-center gap-3 text-xs">
            <span className="flex items-center gap-1 text-emerald-700 font-medium">
              <span className="w-2 h-2 rounded-full bg-emerald-600" /> Supported
            </span>
            <span className="flex items-center gap-1 text-amber-700 font-medium">
              <span className="w-2 h-2 rounded-full bg-amber-600" /> Uncertain
            </span>
            <span className="flex items-center gap-1 text-rose-700 font-medium">
              <span className="w-2 h-2 rounded-full bg-rose-600" /> Contradiction
            </span>
          </div>
        </div>

        <div className="bg-slate-50/80 border border-slate-200/80 rounded-lg p-4">
          {renderHighlightedText()}
        </div>
      </div>

      <div className="mt-3 pt-2 text-[11px] text-slate-500 flex items-center justify-between border-t border-slate-100">
        <span>Click any highlighted claim to view matching evidence and graph relationships.</span>
        {selectedClaimIdx !== null && (
          <span className="font-semibold text-blue-700">
            Selected: Claim {selectedClaimIdx + 1}
          </span>
        )}
      </div>
    </div>
  );
}
