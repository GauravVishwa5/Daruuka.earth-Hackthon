import React from 'react';
import { useDarukaaStore, Recommendation } from '../store';
import { ExternalLink, ChevronRight, TrendingUp, AlertCircle, Clock } from 'lucide-react';

const RANK_COLORS = ['var(--nature-600)', 'var(--ink-700)', 'var(--ink-300)'];

interface RecCardProps {
  rec: Recommendation;
  rank: number;
  onEvidenceClick: (src: any) => void;
}

const RecCard: React.FC<RecCardProps> = ({ rec, rank, onEvidenceClick }) => {
  const isTop = rank === 1;
  const rankColor = RANK_COLORS[Math.min(rank - 1, 2)];

  return (
    <div
      className="rounded-xl overflow-hidden transition-shadow"
      style={{
        background: 'white',
        border: `1px solid ${isTop ? 'rgba(7,138,75,0.3)' : 'var(--line)'}`,
        boxShadow: isTop ? '0 1px 12px rgba(7,138,75,0.08)' : 'none',
      }}
    >
      {/* ── Header ────────────────────────────────────────── */}
      <div
        className="px-5 py-4 border-b"
        style={{
          borderColor: 'var(--line-soft)',
          background: isTop ? 'rgba(7,138,75,0.04)' : 'var(--soft-surface)',
        }}
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <span
              className="shrink-0 w-7 h-7 rounded flex items-center justify-center text-xs font-bold font-mono"
              style={{ background: isTop ? 'var(--nature-600)' : 'var(--soft-surface)', color: isTop ? 'white' : 'var(--ink-300)', border: '1px solid var(--line)' }}
            >
              {rank.toString().padStart(2, '0')}
            </span>
            <div>
              <h4 className="text-sm font-semibold leading-snug" style={{ color: 'var(--ink-900)' }}>
                {rec.name}
              </h4>
              <div className="flex items-center gap-2 mt-1">
                <p className="text-2xs capitalize" style={{ color: 'var(--ink-300)' }}>
                  {rec.category?.replace(/_/g, ' ')}
                </p>
                {rec.time_horizon && (
                  <span
                    className="text-2xs px-2 py-0.5 rounded-full font-medium flex items-center gap-1"
                    style={{ background: 'rgba(7,138,75,0.08)', color: 'var(--nature-600)', border: '1px solid rgba(7,138,75,0.2)' }}
                    title={rec.time_horizon.note}
                  >
                    <Clock className="w-2.5 h-2.5" />
                    {rec.time_horizon.category} ({rec.time_horizon.seasons} {rec.time_horizon.seasons === 1 ? 'season' : 'seasons'})
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="shrink-0 text-right">
            <span className="text-2xs" style={{ color: 'var(--ink-100)' }}>DSI Score</span>
            <div className="font-mono text-sm font-semibold" style={{ color: rankColor }}>
              {rec.decision_score}
            </div>
          </div>
        </div>
      </div>

      <div className="px-5 py-4 space-y-4">
        {/* ── DSI Component Breakdown ─────────────────────── */}
        {rec.dsi_components && (
          <div className="rounded-md p-2.5" style={{ background: 'var(--canvas)', border: '1px solid var(--line-soft)' }}>
            <p className="eyebrow mb-1.5" style={{ fontSize: '10px' }}>DSI Component Decomposition</p>
            <div className="grid grid-cols-3 gap-1.5 text-2xs font-mono">
              <div>Env Fit: <span className="font-semibold" style={{ color: 'var(--ink-700)' }}>{rec.dsi_components.environmental_fit}</span></div>
              <div>Evidence: <span className="font-semibold" style={{ color: 'var(--ink-700)' }}>{rec.dsi_components.evidence_strength}</span></div>
              <div>Bio Gain: <span className="font-semibold" style={{ color: 'var(--ink-700)' }}>{rec.dsi_components.biodiversity_gain}</span></div>
              <div>Soil Gain: <span className="font-semibold" style={{ color: 'var(--ink-700)' }}>{rec.dsi_components.soil_gain}</span></div>
              <div>Feasibility: <span className="font-semibold" style={{ color: 'var(--ink-700)' }}>{rec.dsi_components.feasibility}</span></div>
              <div>Risk Penalty: <span className="font-semibold" style={{ color: rec.dsi_components.risk_penalty > 0.3 ? 'var(--state-critical)' : 'var(--ink-700)' }}>{rec.dsi_components.risk_penalty}</span></div>
            </div>
          </div>
        )}

        {/* ── Benefits ──────────────────────────────────────── */}
        {Object.keys(rec.primary_benefits).length > 0 && (
          <div>
            <p className="eyebrow mb-2">
              <TrendingUp className="w-3 h-3 inline mr-1" style={{ color: 'var(--nature-500)' }} />
              Expected improvements
            </p>
            <div className="grid grid-cols-2 gap-2">
              {Object.entries(rec.primary_benefits).map(([key, val]) => (
                <div
                  key={key}
                  className="rounded-md p-2"
                  style={{ background: 'var(--canvas)', border: '1px solid var(--line-soft)' }}
                >
                  <p className="text-2xs capitalize" style={{ color: 'var(--ink-300)' }}>
                    {key.replace(/_/g, ' ')}
                  </p>
                  <p className="text-xs font-semibold font-mono mt-0.5" style={{ color: 'var(--nature-600)' }}>
                    {typeof val === 'number' ? `+${val}` : String(val)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── Tradeoff ──────────────────────────────────────── */}
        {rec.tradeoffs?.length > 0 && (
          <div
            className="rounded-md p-3"
            style={{ background: 'rgba(194,138,44,0.06)', border: '1px solid rgba(194,138,44,0.2)' }}
          >
            <p className="text-2xs font-medium mb-1 flex items-center gap-1.5" style={{ color: 'var(--state-watch)' }}>
              <AlertCircle className="w-3 h-3" />
              Management precondition
            </p>
            <p className="text-xs" style={{ color: 'var(--ink-700)' }}>
              <span className="font-medium">{rec.tradeoffs[0].risk}.</span>{' '}
              {rec.tradeoffs[0].mitigation}
            </p>
          </div>
        )}

        {/* ── Water penalty ─────────────────────────────────── */}
        {rec.water_penalty_applied && (
          <div
            className="rounded-md px-3 py-2 flex items-center gap-2"
            style={{ background: 'rgba(71,124,134,0.06)', border: '1px solid rgba(71,124,134,0.2)' }}
          >
            <AlertCircle className="w-3.5 h-3.5 shrink-0" style={{ color: 'var(--state-info)' }} />
            <p className="text-2xs" style={{ color: 'var(--state-info)' }}>
              Water-use penalty applied — ranked down for dryland water deficit context
            </p>
          </div>
        )}

        {/* ── Evidence sources ──────────────────────────────── */}
        {rec.evidence_sources?.length > 0 && (
          <div>
            <p className="eyebrow mb-2">Scientific provenance</p>
            <div className="flex flex-wrap gap-2">
              {rec.evidence_sources.map((src: any) => (
                <button
                  key={src.chunk_id}
                  onClick={() => onEvidenceClick(src)}
                  className="source-pill"
                >
                  {src.publisher?.split(' ').find((w: string) => ['FAO','IPCC','IPBES'].includes(w)) || src.publisher?.split(' ')[0]}
                  <span>·</span>
                  {src.year}
                  <ExternalLink className="w-2.5 h-2.5" />
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export const RecommendationList: React.FC = () => {
  const { recommendations, validation, setSelectedEvidence } = useDarukaaStore();

  if (!recommendations || recommendations.length === 0) return null;

  return (
    <div className="space-y-4">
      {/* ── Section header ───────────────────────────────── */}
      <div className="flex items-center justify-between">
        <div>
          <p className="eyebrow eyebrow--accent">Recommended interventions</p>
          <h2 className="text-sm font-semibold mt-0.5" style={{ color: 'var(--ink-900)' }}>
            Ranked by Darukaa Decision Score (DSI)
          </h2>
        </div>

        {validation && (
          <div
            className="rounded-lg px-3 py-2 flex items-center gap-2"
            style={{ background: 'white', border: '1px solid var(--line)' }}
          >
            <div>
              <p className="text-2xs" style={{ color: 'var(--ink-300)' }}>Evidence confidence</p>
              <p
                className="text-xs font-semibold"
                style={{
                  color: validation.confidence_badge === 'HIGH' ? 'var(--state-healthy)' :
                         validation.confidence_badge === 'MEDIUM' ? 'var(--state-watch)' : 'var(--state-high)',
                }}
              >
                {validation.confidence_badge}
              </p>
            </div>
            <div
              className="text-lg font-mono font-bold"
              style={{
                color: validation.confidence_badge === 'HIGH' ? 'var(--state-healthy)' :
                       validation.confidence_badge === 'MEDIUM' ? 'var(--state-watch)' : 'var(--state-high)',
              }}
            >
              {Math.round(validation.confidence_score * 100)}%
            </div>
          </div>
        )}
      </div>

      {/* ── Cards ────────────────────────────────────────── */}
      {recommendations.map((rec) => (
        <RecCard
          key={rec.slug}
          rec={rec}
          rank={rec.rank}
          onEvidenceClick={setSelectedEvidence}
        />
      ))}

      {/* ── Evidence audit ledger ────────────────────────── */}
      {validation && validation.evidence_ledger.length > 0 && (
        <div
          className="rounded-xl p-4"
          style={{ background: 'white', border: '1px solid var(--line)' }}
        >
          <p className="eyebrow mb-3">Evidence audit ledger</p>
          <div className="space-y-1.5">
            {validation.evidence_ledger.slice(0, 5).map((entry: any, i: number) => (
              <div key={i} className="flex items-start gap-2">
                <span
                  className="status-badge shrink-0 mt-0.5"
                  style={{
                    fontSize: '0.55rem',
                    padding: '1px 5px',
                    background:
                      entry.action === 'RETAINED' ? 'rgba(46,139,87,0.1)' :
                      entry.action === 'STRIPPED_NUMBER' ? 'rgba(182,64,64,0.1)' :
                      'rgba(194,138,44,0.1)',
                    color:
                      entry.action === 'RETAINED' ? '#237a47' :
                      entry.action === 'STRIPPED_NUMBER' ? '#922d2d' : '#9a6c1a',
                    borderColor:
                      entry.action === 'RETAINED' ? 'rgba(46,139,87,0.2)' :
                      entry.action === 'STRIPPED_NUMBER' ? 'rgba(182,64,64,0.2)' : 'rgba(194,138,44,0.2)',
                  }}
                >
                  {entry.action}
                </span>
                <p className="text-2xs leading-snug" style={{ color: 'var(--ink-500)' }}>
                  {typeof entry.claim === 'string' ? entry.claim.slice(0, 90) : ''}
                </p>
              </div>
            ))}
          </div>
          <p className="text-2xs mt-3 italic" style={{ color: 'var(--ink-100)' }}>
            Anti-hallucination validator: {validation.claims_stripped} ungrounded figures sanitized ·{' '}
            {validation.claims_supported} claims evidence-backed
          </p>
        </div>
      )}
    </div>
  );
};
