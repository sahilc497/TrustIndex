import React from 'react';
import { X, ShieldCheck } from 'lucide-react';

export default function InfoModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs animate-fade-in">
      <div className="bg-white border border-slate-200 rounded-xl max-w-xl w-full p-6 shadow-xl space-y-4 text-slate-700">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-blue-600" />
            <h3 className="font-bold text-base text-slate-900">
              About TRUST Index
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-md text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-3 text-xs leading-relaxed text-slate-600">
          <p>
            <strong>TRUST Index</strong> is an explainable trust verification framework for Retrieval-Augmented Generation (RAG) systems. It validates whether AI-generated answers are truly grounded in retrieved source documents.
          </p>

          <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-1">
            <span className="font-bold text-slate-800 block text-xs">Four Verification Steps:</span>
            <ul className="list-disc pl-4 space-y-0.5 text-slate-600">
              <li><strong>Extract:</strong> Decompose candidate answer into atomic claims.</li>
              <li><strong>Match:</strong> Retrieve source passages and compute semantic similarity.</li>
              <li><strong>Check:</strong> Test bidirectional contradiction using NLI and exact numeric rules.</li>
              <li><strong>Score:</strong> Compute the weakest-link Trust Score (0–100).</li>
            </ul>
          </div>

          <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-1">
            <span className="font-bold text-slate-800 block text-xs">Decision Thresholds:</span>
            <div className="grid grid-cols-3 gap-2 text-center pt-1">
              <div className="p-1.5 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded">
                <strong>80–100</strong><br />Trusted
              </div>
              <div className="p-1.5 bg-amber-50 text-amber-800 border border-amber-200 rounded">
                <strong>50–79</strong><br />Uncertain
              </div>
              <div className="p-1.5 bg-rose-50 text-rose-800 border-rose-200 rounded">
                <strong>0–49</strong><br />Hallucinated
              </div>
            </div>
          </div>
        </div>

        <div className="pt-3 border-t border-slate-100 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
