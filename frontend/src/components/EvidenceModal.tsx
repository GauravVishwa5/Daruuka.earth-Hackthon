import React, { useEffect } from 'react';
import { useDarukaaStore } from '../store';
import { X, ExternalLink, BookOpen, Shield } from 'lucide-react';

export const EvidenceModal: React.FC = () => {
  const { selectedEvidence, setSelectedEvidence } = useDarukaaStore();

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setSelectedEvidence(null);
      }
    };
    if (selectedEvidence) {
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [selectedEvidence, setSelectedEvidence]);

  if (!selectedEvidence) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ background: 'rgba(9,46,26,0.55)', backdropFilter: 'blur(4px)' }}
      onClick={(e) => { if (e.target === e.currentTarget) setSelectedEvidence(null); }}
    >
      <div
        className="fade-up w-full max-w-2xl max-h-[88vh] overflow-y-auto rounded-xl"
        style={{
          background: 'white',
          border: '1px solid var(--line)',
          boxShadow: 'var(--modal)',
        }}
      >
        {/* ── Modal header ────────────────────────────────── */}
        <div
          className="sticky top-0 flex items-start justify-between px-6 py-4 border-b z-10"
          style={{ borderColor: 'var(--line-soft)', background: 'var(--soft-surface)' }}
        >
          <div className="flex items-start gap-3 pr-4">
            <div
              className="mt-0.5 w-8 h-8 rounded flex items-center justify-center shrink-0"
              style={{ background: 'rgba(7,138,75,0.1)', border: '1px solid rgba(7,138,75,0.2)' }}
            >
              <BookOpen className="w-4 h-4" style={{ color: 'var(--nature-600)' }} />
            </div>
            <div>
              <p className="eyebrow eyebrow--accent">Scientific provenance</p>
              <h3 className="text-sm font-semibold leading-snug mt-0.5" style={{ color: 'var(--ink-900)' }}>
                {selectedEvidence.title}
              </h3>
            </div>
          </div>
          <button
            onClick={() => setSelectedEvidence(null)}
            className="shrink-0 w-8 h-8 flex items-center justify-center rounded-lg transition"
            style={{ color: 'var(--ink-300)', border: '1px solid var(--line)', background: 'white' }}
            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = 'var(--canvas)'; }}
            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = 'white'; }}
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        <div className="px-6 py-5 space-y-5">
          {/* ── Source metadata ──────────────────────────── */}
          <div className="grid grid-cols-3 gap-3">
            <div
              className="rounded-lg p-3"
              style={{ background: 'var(--canvas)', border: '1px solid var(--line-soft)' }}
            >
              <p className="text-2xs" style={{ color: 'var(--ink-100)' }}>Publisher</p>
              <p className="text-xs font-medium mt-0.5" style={{ color: 'var(--ink-700)' }}>
                {selectedEvidence.publisher}
              </p>
            </div>
            <div
              className="rounded-lg p-3"
              style={{ background: 'var(--canvas)', border: '1px solid var(--line-soft)' }}
            >
              <p className="text-2xs" style={{ color: 'var(--ink-100)' }}>Publication year</p>
              <p className="text-xs font-medium mt-0.5" style={{ color: 'var(--ink-700)' }}>
                {selectedEvidence.year}
              </p>
            </div>
            <div
              className="rounded-lg p-3 flex items-start gap-2"
              style={{ background: 'rgba(46,139,87,0.06)', border: '1px solid rgba(46,139,87,0.2)' }}
            >
              <Shield className="w-3.5 h-3.5 mt-0.5 shrink-0" style={{ color: 'var(--state-healthy)' }} />
              <div>
                <p className="text-2xs" style={{ color: 'var(--state-healthy)' }}>Evidence grade</p>
                <p className="text-xs font-semibold mt-0.5" style={{ color: 'var(--state-healthy)' }}>
                  Tier 1 Consensus
                </p>
              </div>
            </div>
          </div>

          {/* ── Evidence excerpt ─────────────────────────── */}
          <div>
            <p className="eyebrow mb-2">Verbatim evidence excerpt</p>
            <blockquote
              className="rounded-xl px-5 py-4 text-sm leading-relaxed italic"
              style={{
                background: 'var(--canvas)',
                border: '1px solid var(--line)',
                borderLeft: '3px solid var(--nature-400)',
                color: 'var(--ink-700)',
                fontFamily: 'Georgia, "Times New Roman", serif',
              }}
            >
              "{selectedEvidence.excerpt}"
            </blockquote>
          </div>

          {/* ── Why it matters ───────────────────────────── */}
          <div
            className="rounded-xl p-4"
            style={{ background: 'rgba(7,138,75,0.04)', border: '1px solid rgba(7,138,75,0.15)' }}
          >
            <p className="eyebrow eyebrow--accent mb-1">Why this evidence matters</p>
            <p className="text-xs leading-relaxed" style={{ color: 'var(--ink-700)' }}>
              This passage was retrieved from the Darukaa knowledge base because it matches your field's environmental context.
              The quantitative findings in this excerpt are used to validate recommendation metrics and prevent unsupported claims.
            </p>
          </div>

          {/* ── DOI + actions ────────────────────────────── */}
          <div
            className="pt-4 border-t flex flex-col sm:flex-row sm:items-center justify-between gap-3"
            style={{ borderColor: 'var(--line-soft)' }}
          >
            <div>
              <p className="text-2xs" style={{ color: 'var(--ink-100)' }}>Digital Object Identifier</p>
              <p className="text-xs font-mono mt-0.5" style={{ color: 'var(--ink-700)' }}>
                {selectedEvidence.doi || 'Not available'}
              </p>
            </div>
            <div className="flex items-center gap-2">
              {selectedEvidence.doi && (
                <a
                  href={`https://doi.org/${selectedEvidence.doi}`}
                  target="_blank"
                  rel="noreferrer"
                  className="inline-flex items-center gap-1.5 text-xs font-medium px-4 py-2 rounded-lg transition"
                  style={{
                    background: 'var(--forest-800)',
                    color: 'rgba(255,255,255,0.92)',
                    border: '1px solid var(--forest-700)',
                  }}
                >
                  Verify at doi.org
                  <ExternalLink className="w-3 h-3" />
                </a>
              )}
              <button
                onClick={() => setSelectedEvidence(null)}
                className="text-xs px-4 py-2 rounded-lg transition"
                style={{
                  background: 'var(--canvas)',
                  color: 'var(--ink-700)',
                  border: '1px solid var(--line)',
                }}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
