import React, { useState, useRef, useEffect } from 'react';
import { useDarukaaStore } from '../store';
import { Send, ArrowRight, RotateCcw } from 'lucide-react';

const PRESETS = [
  {
    label: 'Semi-arid wheat (critical case)',
    message: 'SOC is 0.35%, annual rainfall is 450 mm, max temperature is 34°C, and we grow wheat monoculture.',
    state: 'critical',
  },
  {
    label: 'Diversified agroforestry (resilient)',
    message: 'SOC is 2.4%, annual rainfall is 850 mm, and we manage diversified agroforestry.',
    state: 'healthy',
  },
  {
    label: 'Incomplete field report',
    message: 'My soil is hard and dusty, and pollinators have vanished. What should I plant?',
    state: 'neutral',
  },
];

export const ChatStream: React.FC = () => {
  const { messages, isLoading, sendMessage, resetSession } = useDarukaaStore();
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const text = inputText.trim();
    if (!text || isLoading) return;
    setInputText('');
    sendMessage(text);
  };

  return (
    <div
      className="flex flex-col rounded-xl overflow-hidden"
      style={{
        background: 'white',
        border: '1px solid var(--line)',
        boxShadow: '0 1px 3px rgba(9,46,26,0.05)',
        height: 'calc(100vh - 110px)',
        minHeight: '560px',
      }}
    >
      {/* ── Panel header ──────────────────────────────────── */}
      <div
        className="shrink-0 px-5 py-3.5 flex items-center justify-between border-b"
        style={{ borderColor: 'var(--line-soft)', background: 'var(--soft-surface)' }}
      >
        <div>
          <p className="eyebrow eyebrow--accent">Environmental Consultation</p>
          <h2 className="text-sm font-semibold mt-0.5" style={{ color: 'var(--ink-900)' }}>
            Describe your land's condition
          </h2>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => resetSession()}
            className="flex items-center gap-1 text-2xs px-2 py-1 rounded transition"
            style={{
              background: 'white',
              border: '1px solid var(--line)',
              color: 'var(--ink-500)',
            }}
            title="Start new consultation"
          >
            <RotateCcw className="w-2.5 h-2.5" />
            <span>New Session</span>
          </button>
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 rounded-full" style={{ background: 'var(--state-healthy)' }} />
            <span className="text-2xs" style={{ color: 'var(--ink-300)' }}>System ready</span>
          </div>
        </div>
      </div>

      {/* ── Quick scenario chips ─────────────────────────── */}
      <div
        className="shrink-0 px-4 py-2.5 flex flex-wrap gap-2 border-b"
        style={{ borderColor: 'var(--line-soft)', background: 'var(--canvas)' }}
      >
        <span className="text-2xs self-center" style={{ color: 'var(--ink-100)' }}>Try:</span>
        {PRESETS.map((p) => (
          <button
            key={p.label}
            onClick={() => sendMessage(p.message)}
            className="text-2xs px-2.5 py-1 rounded transition"
            style={{
              background: p.state === 'critical' ? 'rgba(182,64,64,0.07)' :
                          p.state === 'healthy'  ? 'rgba(46,139,87,0.07)' : 'var(--soft-surface)',
              border: `1px solid ${
                p.state === 'critical' ? 'rgba(182,64,64,0.2)' :
                p.state === 'healthy'  ? 'rgba(46,139,87,0.2)'  : 'var(--line)'
              }`,
              color: p.state === 'critical' ? '#922d2d' :
                     p.state === 'healthy'  ? '#237a47' : 'var(--ink-500)',
            }}
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* ── Message stream ────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
        {messages.map((m, idx) => (
          <div key={idx} className={`flex items-start gap-3 ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            {m.role === 'assistant' && (
              <div
                className="w-6 h-6 rounded flex items-center justify-center shrink-0 mt-0.5"
                style={{ background: 'var(--soft-surface)', border: '1px solid var(--line)' }}
              >
                <div className="w-2 h-2 rounded-sm" style={{ background: 'var(--forest-700)' }} />
              </div>
            )}
            <div className={m.role === 'user' ? 'msg-user' : 'msg-system'} style={{ maxWidth: '82%' }}>
              <div className="whitespace-pre-line">{m.content}</div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex items-start gap-3">
            <div
              className="w-6 h-6 rounded flex items-center justify-center shrink-0 mt-0.5"
              style={{ background: 'var(--soft-surface)', border: '1px solid var(--line)' }}
            >
              <div className="w-2 h-2 rounded-sm" style={{ background: 'var(--forest-700)' }} />
            </div>
            <div
              className="px-4 py-3 rounded-xl flex items-center gap-1.5"
              style={{ background: 'white', border: '1px solid var(--line)' }}
            >
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  className="loading-dot w-1.5 h-1.5 rounded-full"
                  style={{ background: 'var(--nature-400)' }}
                />
              ))}
              <span className="text-2xs ml-1.5 font-mono" style={{ color: 'var(--ink-300)' }}>
                Evaluating environmental data…
              </span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* ── Input ─────────────────────────────────────────── */}
      <div className="shrink-0 border-t" style={{ borderColor: 'var(--line-soft)' }}>
        <form onSubmit={handleSubmit} className="flex items-end gap-2 p-3">
          <textarea
            rows={2}
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e as any);
              }
            }}
            placeholder="Describe field conditions, or provide SOC %, rainfall (mm), land use…"
            className="flex-1 resize-none text-sm px-3 py-2.5 rounded-lg"
            style={{
              background: 'var(--canvas)',
              border: '1px solid var(--line)',
              color: 'var(--ink-900)',
              outline: 'none',
              fontFamily: 'inherit',
              lineHeight: '1.5',
            }}
            onFocus={(e) => { e.target.style.borderColor = 'var(--nature-400)'; }}
            onBlur={(e) => { e.target.style.borderColor = 'var(--line)'; }}
          />
          <button
            type="submit"
            disabled={isLoading || !inputText.trim()}
            className="shrink-0 flex items-center gap-1.5 px-4 py-2.5 rounded-lg text-sm font-medium transition"
            style={{
              background: isLoading || !inputText.trim() ? 'var(--soft-surface)' : 'var(--forest-800)',
              color: isLoading || !inputText.trim() ? 'var(--ink-100)' : 'rgba(255,255,255,0.92)',
              border: '1px solid var(--line)',
              cursor: isLoading || !inputText.trim() ? 'not-allowed' : 'pointer',
              height: '62px',
            }}
          >
            <span>Assess</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </form>
        <p className="text-2xs text-center pb-2" style={{ color: 'var(--ink-100)' }}>
          Press Enter to send · Shift+Enter for new line
        </p>
      </div>
    </div>
  );
};
