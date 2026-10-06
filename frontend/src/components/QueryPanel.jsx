import React from 'react';
import { Search, Send, Play } from 'lucide-react';
import { DEMO_SCENARIOS } from '../data/demoScenarios';

export default function QueryPanel({
  query,
  setQuery,
  onVerify,
  loading,
  forceHallucination,
  onSelectDemo
}) {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim() || loading) return;
    onVerify(query, forceHallucination);
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
        <h3 className="text-sm font-bold text-slate-900">
          Ask a Question
        </h3>
        <span className="text-xs text-slate-500">
          Query the enterprise knowledge base or select a demo scenario
        </span>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="What would you like to verify? (e.g. How many annual paid leaves do employees get?)"
              disabled={loading}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg pl-10 pr-4 py-2.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-600 transition-colors"
            />
          </div>

          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 active:bg-blue-800 text-white font-semibold text-sm flex items-center gap-1.5 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shrink-0 shadow-xs"
          >
            <span>Verify Answer</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Quick Demo Buttons for Professor Demo */}
        <div className="pt-2 border-t border-slate-100 flex flex-col sm:flex-row sm:items-center gap-2">
          <span className="text-xs font-semibold text-slate-700 shrink-0">
            Demo Examples:
          </span>

          <div className="flex flex-wrap items-center gap-2">
            {DEMO_SCENARIOS.map((demo) => {
              const isUncertain = demo.expectedStatus === 'Uncertain';
              const isHallu = demo.expectedStatus === 'Hallucinated';

              let style = 'bg-emerald-50 text-emerald-800 border-emerald-300 hover:bg-emerald-100';
              let label = 'Supported Example';
              if (isUncertain) {
                style = 'bg-amber-50 text-amber-800 border-amber-300 hover:bg-amber-100';
                label = 'Unsupported Example';
              } else if (isHallu) {
                style = 'bg-rose-50 text-rose-800 border-rose-300 hover:bg-rose-100';
                label = 'Contradiction Example';
              }

              return (
                <button
                  key={demo.id}
                  type="button"
                  onClick={() => onSelectDemo(demo)}
                  disabled={loading}
                  className={`px-3 py-1.5 rounded-md border text-xs font-medium flex items-center gap-1.5 transition-colors disabled:opacity-50 ${style}`}
                >
                  <Play className="w-3 h-3 fill-current" />
                  <span>{label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </form>
    </div>
  );
}
