import React from 'react';
import { ChatStream } from './components/ChatStream';
import { TelemetryBar } from './components/TelemetryBar';
import { StressCard } from './components/StressCard';
import { RecommendationList } from './components/RecommendationList';
import { EvidenceModal } from './components/EvidenceModal';
import { Leaf, BookOpen, FlaskConical } from 'lucide-react';

export const App: React.FC = () => {
  return (
    <div className="min-h-screen" style={{ background: 'var(--canvas)' }}>
      {/* ── Header ─────────────────────────────────────────── */}
      <header
        className="sticky top-0 z-20 border-b"
        style={{
          background: 'white',
          borderColor: 'var(--line)',
          boxShadow: '0 1px 0 0 var(--line-soft)',
        }}
      >
        <div className="max-w-[1440px] mx-auto px-6 h-[62px] flex items-center justify-between gap-6">
          {/* Brand */}
          <div className="flex items-center gap-3 shrink-0">
            <div
              className="flex items-center justify-center w-8 h-8 rounded"
              style={{ background: 'var(--forest-900)' }}
            >
              <Leaf className="w-4 h-4" style={{ color: 'var(--nature-400)' }} />
            </div>
            <div>
              <span
                className="font-semibold text-sm tracking-tight"
                style={{ color: 'var(--forest-900)' }}
              >
                Darukaa.Earth
              </span>
              <span
                className="text-2xs ml-2 font-mono px-1.5 py-0.5 rounded"
                style={{
                  background: 'var(--soft-surface)',
                  color: 'var(--ink-300)',
                  border: '1px solid var(--line)',
                }}
              >
                Environmental Intelligence
              </span>
            </div>
          </div>

          {/* Capability tags */}
          <div className="hidden md:flex items-center gap-3 text-2xs" style={{ color: 'var(--ink-300)' }}>
            <div className="flex items-center gap-1.5">
              <FlaskConical className="w-3.5 h-3.5" style={{ color: 'var(--nature-500)' }} />
              <span>Multi-Metric Reasoning</span>
            </div>
            <span style={{ color: 'var(--line-strong)' }}>·</span>
            <div className="flex items-center gap-1.5">
              <BookOpen className="w-3.5 h-3.5" style={{ color: 'var(--nature-500)' }} />
              <span>FAO · IPCC · IPBES Evidence</span>
            </div>
            <span style={{ color: 'var(--line-strong)' }}>·</span>
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full" style={{ background: 'var(--state-healthy)' }} />
              <span>Connected</span>
            </div>
          </div>
        </div>
      </header>

      {/* ── Main Workspace ──────────────────────────────────── */}
      <main className="max-w-[1440px] mx-auto px-4 sm:px-6 py-6 grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">

        {/* Left — Consultation Stream (5/12 cols on desktop) */}
        <section className="lg:col-span-5">
          <div className="sticky top-[78px]">
            <ChatStream />
          </div>
        </section>

        {/* Right — Intelligence Workspace (7/12 cols on desktop) */}
        <section className="lg:col-span-7 space-y-5">
          <TelemetryBar />
          <StressCard />
          <RecommendationList />

          {/* Empty state when nothing is loaded */}
        </section>
      </main>

      {/* Evidence Provenance Modal */}
      <EvidenceModal />
    </div>
  );
};

export default App;
