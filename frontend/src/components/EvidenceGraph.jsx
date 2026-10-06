import React, { useState, useRef, useMemo } from 'react';
import { GitFork, ZoomIn, ZoomOut, RotateCcw } from 'lucide-react';

export default function EvidenceGraph({
  claims = [],
  selectedClaimIdx,
  selectedEvidenceId,
  onSelectClaim,
  onSelectEvidence
}) {
  const containerRef = useRef(null);

  // Pan & Zoom
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  // Hover highlighting
  const [hoveredNode, setHoveredNode] = useState(null); // { type: 'claim' | 'ev', id: any }

  const handleReset = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const handleZoomIn = () => setZoom(prev => Math.min(2.0, prev + 0.15));
  const handleZoomOut = () => setZoom(prev => Math.max(0.6, prev - 0.15));

  const handleMouseDown = (e) => {
    if (e.target.tagName === 'svg' || (e.target.tagName === 'rect' && e.target.classList.contains('canvas-bg'))) {
      setIsDragging(true);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleMouseMove = (e) => {
    if (isDragging) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // Build clean node and edge layout
  const { edges, claimPositions, evPositions } = useMemo(() => {
    if (!claims || claims.length === 0) {
      return { edges: [], claimPositions: [], evPositions: [] };
    }

    const evMap = new Map();
    claims.forEach((c, cIdx) => {
      (c.evidence || []).forEach((e) => {
        const key = `${e.doc}::${e.text.slice(0, 40)}`;
        if (!evMap.has(key)) {
          evMap.set(key, {
            id: key,
            doc: e.doc,
            text: e.text,
            snippet: e.text.length > 55 ? e.text.slice(0, 52) + '...' : e.text,
            firstClaimIdx: cIdx,
          });
        }
      });
    });

    const evList = Array.from(evMap.values());
    const height = Math.max(300, Math.max(claims.length, evList.length) * 75 + 50);

    const leftX = 140;
    const rightX = 620;

    const claimSpacing = claims.length > 1 ? (height - 80) / (claims.length - 1) : 0;
    const evSpacing = evList.length > 1 ? (height - 80) / (evList.length - 1) : 0;

    const cPositions = claims.map((c, i) => ({
      ...c,
      idx: i,
      id: `claim-${i}`,
      x: leftX,
      y: claims.length === 1 ? height / 2 : 45 + i * claimSpacing,
    }));

    const ePositions = evList.map((ev, i) => ({
      ...ev,
      idx: i,
      x: rightX,
      y: evList.length === 1 ? height / 2 : 45 + i * evSpacing,
    }));

    // Build edges
    const edgeList = [];
    cPositions.forEach((cp, ci) => {
      (cp.evidence || []).forEach((e) => {
        const evKey = `${e.doc}::${e.text.slice(0, 40)}`;
        const ep = ePositions.find((ev) => ev.id === evKey);
        if (ep) {
          let edgeType = 'NEUTRAL';
          let color = '#64748b'; // gray-500
          let strokeDash = '4,4';
          let strokeWidth = 2;
          let labelText = 'Related';

          if (e.label === 'ENTAILMENT') {
            edgeType = 'SUPPORTS';
            color = '#15803d'; // green-700
            strokeDash = 'none';
            strokeWidth = 3;
            labelText = 'SUPPORTS';
          } else if (e.label === 'CONTRADICTION') {
            edgeType = 'CONTRADICTS';
            color = '#b91c1c'; // red-700
            strokeDash = '6,4';
            strokeWidth = 3.5;
            labelText = 'CONTRADICTS';
          }

          edgeList.push({
            id: `edge-${ci}-${ep.idx}`,
            claimIdx: ci,
            evId: ep.id,
            evIdx: ep.idx,
            x1: cp.x + 75,
            y1: cp.y,
            x2: ep.x - 75,
            y2: ep.y,
            color,
            edgeType,
            labelText,
            label: e.label,
            similarity: e.similarity,
            strokeDash,
            strokeWidth,
            reason: e.reason
          });
        }
      });
    });

    return {
      evidenceList: evList,
      edges: edgeList,
      claimPositions: cPositions,
      evPositions: ePositions
    };
  }, [claims]);

  if (!claims || claims.length === 0) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl p-8 text-center text-slate-400">
        <GitFork className="w-8 h-8 text-slate-300 mx-auto mb-2" />
        <p className="text-sm font-medium text-slate-600">No Evidence Graph Available</p>
        <p className="text-xs text-slate-400 mt-0.5">Submit a query or load a demo to see the verification graph.</p>
      </div>
    );
  }

  const isEdgeActive = (edge) => {
    if (hoveredNode) {
      if (hoveredNode.type === 'claim') return edge.claimIdx === hoveredNode.id;
      if (hoveredNode.type === 'ev') return edge.evId === hoveredNode.id;
    }
    if (selectedClaimIdx !== null && selectedClaimIdx !== undefined) {
      return edge.claimIdx === selectedClaimIdx;
    }
    if (selectedEvidenceId) {
      return edge.evId === selectedEvidenceId;
    }
    return true;
  };

  const isClaimActive = (idx) => {
    if (hoveredNode) {
      if (hoveredNode.type === 'claim') return hoveredNode.id === idx;
      if (hoveredNode.type === 'ev') {
        return edges.some(e => e.evId === hoveredNode.id && e.claimIdx === idx);
      }
    }
    if (selectedClaimIdx !== null && selectedClaimIdx !== undefined) {
      return selectedClaimIdx === idx;
    }
    if (selectedEvidenceId) {
      return edges.some(e => e.evId === selectedEvidenceId && e.claimIdx === idx);
    }
    return true;
  };

  const isEvActive = (evId) => {
    if (hoveredNode) {
      if (hoveredNode.type === 'ev') return hoveredNode.id === evId;
      if (hoveredNode.type === 'claim') {
        return edges.some(e => e.claimIdx === hoveredNode.id && e.evId === evId);
      }
    }
    if (selectedClaimIdx !== null && selectedClaimIdx !== undefined) {
      return edges.some(e => e.claimIdx === selectedClaimIdx && e.evId === evId);
    }
    if (selectedEvidenceId) {
      return selectedEvidenceId === evId;
    }
    return true;
  };

  const hasSpecificFocus = hoveredNode !== null || selectedClaimIdx !== null || selectedEvidenceId !== null;

  return (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-xs flex flex-col">
      {/* Header */}
      <div className="px-5 py-3 border-b border-slate-200 bg-slate-50/70 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-bold text-slate-900">
            Evidence Graph
          </h3>
          <p className="text-xs text-slate-500">
            How the generated claim relates to retrieved evidence
          </p>
        </div>

        {/* Legend & Controls */}
        <div className="flex items-center gap-4">
          <div className="hidden sm:flex items-center gap-3 text-xs font-medium">
            <span className="flex items-center gap-1.5 text-emerald-800">
              <span className="w-2.5 h-1 bg-emerald-600 rounded-full" /> Supports
            </span>
            <span className="flex items-center gap-1.5 text-rose-800">
              <span className="w-2.5 h-1 bg-rose-600 rounded-full" /> Contradicts
            </span>
            <span className="flex items-center gap-1.5 text-slate-600">
              <span className="w-2.5 h-1 bg-slate-400 rounded-full" /> Related
            </span>
          </div>

          <div className="flex items-center gap-1 bg-white border border-slate-200 rounded-lg p-0.5">
            <button
              onClick={handleZoomIn}
              className="p-1 rounded hover:bg-slate-100 text-slate-600"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={handleZoomOut}
              className="p-1 rounded hover:bg-slate-100 text-slate-600"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={handleReset}
              className="p-1 rounded hover:bg-slate-100 text-slate-600"
              title="Reset View"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* SVG Canvas */}
      <div 
        ref={containerRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        className="relative w-full h-[320px] bg-slate-50/40 overflow-hidden cursor-grab active:cursor-grabbing select-none"
      >
        <svg viewBox="0 0 760 320" className="w-full h-full">
          <defs>
            <marker id="acad-support" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#15803d" />
            </marker>
            <marker id="acad-contradict" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 10 5 L 0 9 z" fill="#b91c1c" />
            </marker>
          </defs>

          {/* Background drag layer */}
          <rect x="-500" y="-500" width="2000" height="2000" fill="transparent" className="canvas-bg" />

          <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
            {/* Column Titles */}
            <text x="140" y="24" fill="#64748b" fontSize="11" fontWeight="700" textAnchor="middle" className="uppercase tracking-wider">
              CLAIM
            </text>
            <text x="620" y="24" fill="#64748b" fontSize="11" fontWeight="700" textAnchor="middle" className="uppercase tracking-wider">
              EVIDENCE
            </text>

            {/* Connecting Edges */}
            {edges.map((edge) => {
              const active = isEdgeActive(edge);
              const opacity = hasSpecificFocus ? (active ? 1.0 : 0.15) : 0.85;
              const isContradiction = edge.edgeType === 'CONTRADICTS';

              const dx = (edge.x2 - edge.x1) * 0.5;
              const pathD = `M ${edge.x1} ${edge.y1} C ${edge.x1 + dx} ${edge.y1}, ${edge.x2 - dx} ${edge.y2}, ${edge.x2} ${edge.y2}`;

              const midX = (edge.x1 + edge.x2) / 2;
              const midY = (edge.y1 + edge.y2) / 2;

              return (
                <g key={edge.id} className="transition-opacity duration-200">
                  <path
                    d={pathD}
                    fill="none"
                    stroke={edge.color}
                    strokeWidth={edge.strokeWidth}
                    strokeDasharray={edge.strokeDash}
                    strokeOpacity={opacity}
                    markerEnd={isContradiction ? 'url(#acad-contradict)' : 'url(#acad-support)'}
                  />

                  {/* Relationship Label Tag */}
                  {active && (
                    <g transform={`translate(${midX}, ${midY})`}>
                      <rect
                        x="-36"
                        y="-10"
                        width="72"
                        height="20"
                        rx="4"
                        fill="#ffffff"
                        stroke={edge.color}
                        strokeWidth="1.2"
                      />
                      <text
                        x="0"
                        y="4"
                        fill={edge.color}
                        fontSize="9"
                        fontWeight="800"
                        textAnchor="middle"
                        className="font-sans uppercase"
                      >
                        {edge.labelText}
                      </text>
                    </g>
                  )}
                </g>
              );
            })}

            {/* Claim Nodes (Left) */}
            {claimPositions.map((cp) => {
              const active = isClaimActive(cp.idx);
              const isSelected = selectedClaimIdx === cp.idx;
              const consensus = cp.consensus;

              let nodeBg = '#ffffff';
              let nodeBorder = '#2563eb';
              let badgeText = '#1e40af';
              let badgeBg = '#dbeafe';
              let tagText = 'Supported';

              if (consensus < 0) {
                nodeBorder = '#b91c1c';
                badgeText = '#991b1b';
                badgeBg = '#fee2e2';
                tagText = 'Contradicted';
              } else if (consensus < 0.6) {
                nodeBorder = '#b45309';
                badgeText = '#92400e';
                badgeBg = '#fef3c7';
                tagText = 'Uncertain';
              } else {
                nodeBorder = '#15803d';
                badgeText = '#166534';
                badgeBg = '#dcfce7';
                tagText = 'Supported';
              }

              const opacity = hasSpecificFocus ? (active ? 1.0 : 0.25) : 1.0;

              return (
                <g
                  key={cp.id}
                  onClick={() => onSelectClaim(cp.idx)}
                  onMouseEnter={() => setHoveredNode({ type: 'claim', id: cp.idx })}
                  onMouseLeave={() => setHoveredNode(null)}
                  className="cursor-pointer"
                  style={{ opacity }}
                >
                  <rect
                    x={cp.x - 110}
                    y={cp.y - 22}
                    width="170"
                    height="44"
                    rx="6"
                    fill={nodeBg}
                    stroke={isSelected ? '#2563eb' : nodeBorder}
                    strokeWidth={isSelected ? 2.5 : 1.5}
                    className="shadow-xs hover:filter hover:brightness-95"
                  />
                  <text x={cp.x - 98} y={cp.y - 6} fill="#0f172a" fontSize="11" fontWeight="700">
                    Claim {cp.idx + 1}
                  </text>
                  <rect x={cp.x + 10} y={cp.y - 18} width="42" height="15" rx="3" fill={badgeBg} />
                  <text x={cp.x + 31} y={cp.y - 7} fill={badgeText} fontSize="8.5" fontWeight="700" textAnchor="middle">
                    {tagText}
                  </text>
                  <text x={cp.x - 98} y={cp.y + 11} fill="#64748b" fontSize="9.5">
                    {cp.claim.length > 22 ? cp.claim.slice(0, 20) + '...' : cp.claim}
                  </text>
                  <circle cx={cp.x + 75} cy={cp.y} r="4" fill={nodeBorder} />
                </g>
              );
            })}

            {/* Evidence Nodes (Right) */}
            {evPositions.map((ep) => {
              const active = isEvActive(ep.id);
              const isSelected = selectedEvidenceId === ep.id;
              const opacity = hasSpecificFocus ? (active ? 1.0 : 0.25) : 1.0;

              return (
                <g
                  key={ep.id}
                  onClick={() => onSelectEvidence(ep.id)}
                  onMouseEnter={() => setHoveredNode({ type: 'ev', id: ep.id })}
                  onMouseLeave={() => setHoveredNode(null)}
                  className="cursor-pointer"
                  style={{ opacity }}
                >
                  <rect
                    x={ep.x - 60}
                    y={ep.y - 22}
                    width="170"
                    height="44"
                    rx="6"
                    fill="#ffffff"
                    stroke={isSelected ? '#2563eb' : '#cbd5e1'}
                    strokeWidth={isSelected ? 2.5 : 1.5}
                    className="shadow-xs hover:filter hover:brightness-95"
                  />
                  <text x={ep.x - 48} y={ep.y - 6} fill="#1e293b" fontSize="10.5" fontWeight="700">
                    {ep.doc}
                  </text>
                  <text x={ep.x - 48} y={ep.y + 11} fill="#64748b" fontSize="9.5">
                    {ep.snippet.length > 22 ? ep.snippet.slice(0, 20) + '...' : ep.snippet}
                  </text>
                  <circle cx={ep.x - 60} cy={ep.y} r="4" fill="#3b82f6" />
                </g>
              );
            })}
          </g>
        </svg>

        <div className="absolute bottom-2 left-4 text-[10px] text-slate-500 bg-white/90 border border-slate-200 px-2 py-0.5 rounded shadow-2xs">
          Click any claim or evidence node to trace verification path
        </div>
      </div>
    </div>
  );
}
