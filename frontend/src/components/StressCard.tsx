import React from 'react';
import { useDarukaaStore } from '../store';
import { AlertTriangle, Shield } from 'lucide-react';

const STRESS_CONFIG: Record<string, { label: string; fillPct: number; status: string }> = {
  CRITICAL: { label: 'Critical', fillPct: 100, status: 'critical' },
  HIGH:     { label: 'High',     fillPct: 75,  status: 'high'     },
  MODERATE: { label: 'Moderate', fillPct: 50,  status: 'watch'    },
  LOW:      { label: 'Low',      fillPct: 20,  status: 'healthy'  },
};

const BAR_COLORS: Record<string, string> = {
  critical: 'var(--state-critical)',
  high:     'var(--state-high)',
  watch:    'var(--state-watch)',
  healthy:  'var(--state-healthy)',
};

interface StressBarProps {
  label: string;
  level: string;
  description?: string;
}

const StressBar: React.FC<StressBarProps> = ({ label, level, description }) => {
  const config = STRESS_CONFIG[level] || STRESS_CONFIG['LOW'];
  const color = BAR_COLORS[config.status];

  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <span className="text-xs font-medium" style={{ color: 'var(--ink-700)' }}>{label}</span>
        <span className={`status-badge status-badge--${config.status}`}>{config.label}</span>
      </div>
      <div
        className="h-1.5 rounded-full overflow-hidden"
        style={{ background: 'var(--mist)' }}
      >
        <div
          className="h-full rounded-full transition-all duration-500"
          style={{ width: `${config.fillPct}%`, background: color }}
        />
      </div>
      {description && (
        <p className="text-2xs mt-1" style={{ color: 'var(--ink-100)' }}>{description}</p>
      )}
    </div>
  );
};

const RISK_META: Record<string, { badge: string; status: string; icon: 'shield' | 'alert'; headline: string }> = {
  CRITICAL_COMPOUND_DEGRADATION: {
    badge: 'Critical Compound Risk',
    status: 'critical',
    icon: 'alert',
    headline: 'Critical compound degradation detected',
  },
  HIGH_COMPOUND_STRESS: {
    badge: 'High Compound Stress',
    status: 'high',
    icon: 'alert',
    headline: 'Multiple stressors interacting',
  },
  MODERATE_ECOLOGICAL_VULNERABILITY: {
    badge: 'Moderate Vulnerability',
    status: 'watch',
    icon: 'shield',
    headline: 'Targeted interventions recommended',
  },
  LOW_STRESS_BALANCED: {
    badge: 'Balanced Agroecosystem',
    status: 'healthy',
    icon: 'shield',
    headline: 'Environmental baseline is healthy',
  },
};

export const StressCard: React.FC = () => {
  const { assessment } = useDarukaaStore();

  if (!assessment) {
    return (
      <div
        className="rounded-xl p-5 border"
        style={{ background: 'white', borderColor: 'var(--line)' }}
      >
        <p className="eyebrow eyebrow--accent mb-1">Environmental Assessment</p>
        <p className="text-sm" style={{ color: 'var(--ink-300)' }}>
          Awaiting environmental telemetry. Provide Soil Organic Carbon, rainfall, and land use to compute compound stress.
        </p>
      </div>
    );
  }

  const meta = RISK_META[assessment.compound_risk] || RISK_META['MODERATE_ECOLOGICAL_VULNERABILITY'];
  const sl = assessment.stress_levels;
  const isAlert = meta.status === 'critical' || meta.status === 'high';

  return (
    <div
      className="rounded-xl overflow-hidden"
      style={{ background: 'white', border: '1px solid var(--line)' }}
    >
      {/* ── Status Header ─────────────────────────────────── */}
      <div
        className="px-5 py-4 border-b"
        style={{
          background: isAlert ? 'rgba(182,64,64,0.04)' : 'var(--soft-surface)',
          borderColor: 'var(--line-soft)',
        }}
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex items-start gap-3">
            <div
              className="mt-0.5 w-8 h-8 rounded flex items-center justify-center shrink-0"
              style={{
                background: isAlert ? 'rgba(182,64,64,0.1)' : 'rgba(46,139,87,0.1)',
                border: `1px solid ${isAlert ? 'rgba(182,64,64,0.2)' : 'rgba(46,139,87,0.2)'}`,
              }}
            >
              {isAlert
                ? <AlertTriangle className="w-4 h-4" style={{ color: 'var(--state-critical)' }} />
                : <Shield className="w-4 h-4" style={{ color: 'var(--state-healthy)' }} />
              }
            </div>
            <div>
              <p className="eyebrow eyebrow--accent">Environmental Assessment</p>
              <h3 className="text-sm font-semibold mt-0.5" style={{ color: 'var(--ink-900)' }}>
                {meta.headline}
              </h3>
            </div>
          </div>
          <span className={`status-badge status-badge--${meta.status} shrink-0`}>{meta.badge}</span>
        </div>
      </div>

      <div className="p-5 space-y-5">
        {/* ── Stress bars ─────────────────────────────────── */}
        <div className="space-y-3">
          <StressBar
            label="Soil degradation"
            level={sl.soil_stress || 'LOW'}
            description={sl.soil_stress === 'CRITICAL' ? 'SOC below FAO structural aggregate threshold' : undefined}
          />
          <StressBar
            label="Hydrological deficit"
            level={sl.water_stress || 'LOW'}
            description={sl.water_stress === 'HIGH' ? 'Rainfall below semi-arid threshold — water penalty active' : undefined}
          />
          <StressBar
            label="Habitat & biodiversity pressure"
            level={sl.biodiversity_stress || 'LOW'}
            description={sl.biodiversity_stress === 'HIGH' ? 'Monoculture severing native floral corridors' : undefined}
          />
          {sl.thermal_stress && sl.thermal_stress !== 'LOW' && (
            <StressBar
              label="Thermal stress"
              level={sl.thermal_stress}
              description={sl.thermal_stress === 'CRITICAL' ? 'Extreme temperatures accelerate SOC oxidation' : 'Elevated temperature compounding evaporative deficit'}
            />
          )}
          {sl.ph_stress && sl.ph_stress !== 'LOW' && (
            <StressBar
              label="Soil pH constraint"
              level={sl.ph_stress}
              description={sl.ph_stress === 'HIGH' ? 'Acidic/alkaline conditions locking phosphorus & micronutrients' : 'Mild pH departure from neutral range'}
            />
          )}
        </div>

        <hr style={{ borderColor: 'var(--line-soft)', margin: '0' }} />

        {/* ── Causal summary ──────────────────────────────── */}
        {assessment.summary_text && (
          <div>
            <p className="eyebrow mb-2">Compound Interaction</p>
            <p className="text-sm leading-relaxed" style={{ color: 'var(--ink-700)' }}>
              {assessment.summary_text}
            </p>
          </div>
        )}

        {/* ── Key factors ─────────────────────────────────── */}
        {(assessment as any).key_factors?.length > 0 && (
          <div>
            <p className="eyebrow mb-2">Key Drivers</p>
            <div className="space-y-1.5">
              {((assessment as any).key_factors as string[]).map((f, i) => (
                <div key={i} className="flex items-start gap-2">
                  <div
                    className="mt-1.5 w-1 h-1 rounded-full shrink-0"
                    style={{ background: 'var(--state-high)' }}
                  />
                  <p className="text-xs" style={{ color: 'var(--ink-700)' }}>{f}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── Causal factors ──────────────────────────────── */}
        {assessment.causal_factors?.length > 0 && (
          <div>
            <p className="eyebrow mb-2">Causal Mechanisms</p>
            <div className="space-y-2">
              {assessment.causal_factors.slice(0, 3).map((cf: any, i: number) => (
                <div
                  key={i}
                  className="rounded-lg p-3"
                  style={{ background: 'var(--canvas)', border: '1px solid var(--line-soft)' }}
                >
                  <div className="flex items-center gap-2 mb-1">
                    <span
                      className="text-2xs font-mono px-1.5 py-0.5 rounded"
                      style={{
                        background: cf.severity === 'CRITICAL' ? 'rgba(182,64,64,0.1)' : 'rgba(201,106,50,0.1)',
                        color: cf.severity === 'CRITICAL' ? 'var(--state-critical)' : 'var(--state-high)',
                        border: `1px solid ${cf.severity === 'CRITICAL' ? 'rgba(182,64,64,0.2)' : 'rgba(201,106,50,0.2)'}`,
                      }}
                    >
                      {cf.severity}
                    </span>
                    <span className="text-2xs font-medium" style={{ color: 'var(--ink-500)' }}>
                      {cf.stressor?.replace(/_/g, ' ')}
                    </span>
                  </div>
                  <p className="text-xs" style={{ color: 'var(--ink-700)' }}>{cf.why}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* ── Heuristic disclaimer ─────────────────────────── */}
        {(assessment as any).heuristic_label && (
          <p className="text-2xs italic" style={{ color: 'var(--ink-100)' }}>
            Stress scores computed by {(assessment as any).heuristic_label}. Thresholds derived from FAO / IPCC / IPBES institutional baselines.
          </p>
        )}
      </div>
    </div>
  );
};
