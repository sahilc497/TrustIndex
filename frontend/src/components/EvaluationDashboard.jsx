import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Scale } from 'lucide-react';
import { FROZEN_RESEARCH_METRICS } from '../data/demoScenarios';

export default function EvaluationDashboard() {
  const [showFullEvaluation, setShowFullEvaluation] = useState(false);
  const { rag_comparison } = FROZEN_RESEARCH_METRICS;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* 1. Header Banner */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-blue-700 bg-blue-50 px-2 py-0.5 rounded border border-blue-200">
              Chapter 4 Experimental Results
            </span>
            <h2 className="text-lg font-bold text-slate-900 mt-1">
              Research Results
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Empirical evaluation across RAG generation interventions and independent verification
            </p>
          </div>

          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-700">
            <Scale className="w-4 h-4 text-emerald-600" />
            <span>Experimental Results Frozen</span>
          </div>
        </div>
      </div>

      {/* 2. Key Numbers First (Section 14) */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <div className="bg-white border border-slate-200 rounded-xl p-3.5 text-center shadow-xs">
          <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block">
            RAG Hallucination
          </span>
          <span className="text-xl font-bold text-slate-800 mt-1 block">
            23.4% → 24.7%
          </span>
          <span className="text-[10px] text-slate-400 mt-0.5 block">Baseline vs Conciseness</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-3.5 text-center shadow-xs">
          <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block">
            Exact McNemar
          </span>
          <span className="text-xl font-bold text-amber-700 mt-1 block">
            p = 1.0000
          </span>
          <span className="text-[10px] text-slate-400 mt-0.5 block">Statistically Invariant</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-3.5 text-center shadow-xs">
          <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block">
            TRUST Accuracy
          </span>
          <span className="text-xl font-bold text-blue-600 mt-1 block">
            97.7%
          </span>
          <span className="text-[10px] text-slate-400 mt-0.5 block">N = 130 Benchmark</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-3.5 text-center shadow-xs">
          <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block">
            Detection F1
          </span>
          <span className="text-xl font-bold text-blue-600 mt-1 block">
            98.5%
          </span>
          <span className="text-[10px] text-slate-400 mt-0.5 block">Recall = 100%</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-3.5 text-center shadow-xs">
          <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block">
            Unseen Accuracy
          </span>
          <span className="text-xl font-bold text-emerald-700 mt-1 block">
            100.0%
          </span>
          <span className="text-[10px] text-slate-400 mt-0.5 block">N = 42 Partition</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-3.5 text-center shadow-xs">
          <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block">
            Invalid → Trusted
          </span>
          <span className="text-xl font-bold text-emerald-700 mt-1 block">
            0 / 100
          </span>
          <span className="text-[10px] text-emerald-800 font-semibold mt-0.5 block">0.0% Violations</span>
        </div>
      </div>

      {/* 3. Research Message / Key Finding (Section 15) */}
      <div className="bg-white border-l-4 border-l-blue-600 border border-slate-200 rounded-xl p-5 shadow-xs space-y-2">
        <span className="text-xs font-bold uppercase tracking-wider text-blue-700 block">
          Key Research Finding
        </span>
        <p className="text-sm text-slate-800 font-medium leading-relaxed">
          "Within the evaluated experimental setup, retrieval- and prompting-level interventions did not reliably reduce hallucination in the tested RAG configuration."
        </p>
        <p className="text-xs text-slate-600 leading-relaxed">
          In contrast, TRUST Index adds an independent post-generation verification layer that checks generated claims against available evidence, catching 100% of invalid claims without modifying the generator model.
        </p>
      </div>

      {/* 4. Expandable Detailed Evaluation Section */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs">
        <button
          onClick={() => setShowFullEvaluation(!showFullEvaluation)}
          className="w-full flex items-center justify-between text-sm font-semibold text-slate-800 hover:text-blue-600 transition-colors"
        >
          <span>View Full Evaluation Breakdown</span>
          {showFullEvaluation ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {showFullEvaluation && (
          <div className="mt-4 pt-4 border-t border-slate-100 space-y-6 text-xs text-slate-700 animate-fade-in">
            {/* Condition A–E Table */}
            <div>
              <h4 className="font-bold text-slate-900 mb-2">
                Table 4.1: RAG Generation Interventions (N = 77)
              </h4>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border border-slate-200 rounded-lg">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-600">
                    <tr>
                      <th className="p-2">Condition</th>
                      <th className="p-2">Retrieval</th>
                      <th className="p-2">Prompt Strategy</th>
                      <th className="p-2">Claims/Ans</th>
                      <th className="p-2">Hallu Rate</th>
                      <th className="p-2">McNemar Sig</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-slate-700">
                    {rag_comparison.conditions.map((c) => (
                      <tr key={c.id}>
                        <td className="p-2 font-medium">{c.name}</td>
                        <td className="p-2">{c.retrieval}</td>
                        <td className="p-2">{c.prompt}</td>
                        <td className="p-2">{c.claims_per_answer}</td>
                        <td className="p-2 font-bold">{c.hallucination_rate}%</td>
                        <td className="p-2 text-slate-500">{c.mcnemar_p}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Verification Partition Details */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 space-y-1.5">
                <h5 className="font-bold text-slate-800">Controlled Benchmark (N = 130)</h5>
                <p>Binary Accuracy: <strong>97.7%</strong> (127/130)</p>
                <p>Detection Recall: <strong>100.0%</strong> (100/100 invalid outputs flagged)</p>
                <p>Three-way Accuracy: <strong>84.6%</strong> (Macro F1 = 84.0%)</p>
                <p>False Trust Rate: <strong>0.0%</strong> (0/100 invalid labeled Trusted)</p>
              </div>

              <div className="p-3.5 rounded-lg bg-slate-50 border border-slate-200 space-y-1.5">
                <h5 className="font-bold text-slate-800">Unseen Partition (N = 42)</h5>
                <p>Binary Accuracy: <strong>100.0%</strong> (42/42)</p>
                <p>Detection Precision: <strong>100.0%</strong> (Zero false alarms)</p>
                <p>Safety Violations: <strong>0 / 36</strong> (0.0% on unseen non-supported)</p>
                <p>Score Separation: <strong>H = 100.56</strong> (Kruskal-Wallis p &lt; 0.0001)</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
