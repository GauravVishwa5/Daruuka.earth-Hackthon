import React from 'react';
import { useDarukaaStore } from '../store';
import { Droplets, Thermometer, Sprout, LayoutGrid } from 'lucide-react';

interface MetricSlotProps {
  label: string;
  value: string | null;
  unit?: string;
  status?: 'healthy' | 'watch' | 'high' | 'critical' | 'neutral';
  statusLabel?: string;
  threshold?: string;
  icon: React.ReactNode;
}

const MetricSlot: React.FC<MetricSlotProps> = ({
  label, value, unit, status = 'neutral', statusLabel, threshold, icon
}) => {
  const statusColors: Record<string, { bg: string; border: string; text: string }> = {
    healthy:  { bg: 'rgba(46,139,87,0.06)',   border: 'rgba(46,139,87,0.2)',   text: '#237a47' },
    watch:    { bg: 'rgba(194,138,44,0.06)',   border: 'rgba(194,138,44,0.2)',  text: '#9a6c1a' },
    high:     { bg: 'rgba(201,106,50,0.06)',   border: 'rgba(201,106,50,0.2)',  text: '#a04a1a' },
    critical: { bg: 'rgba(182,64,64,0.06)',    border: 'rgba(182,64,64,0.2)',   text: '#922d2d' },
    neutral:  { bg: 'var(--soft-surface)',     border: 'var(--line)',           text: 'var(--ink-300)' },
    pending:  { bg: 'var(--canvas)',           border: 'var(--line-soft)',      text: 'var(--ink-100)' },
  };

  const isPending = value === null || value === undefined;
  const colors = statusColors[isPending ? 'pending' : status];

  return (
    <div
      className="rounded-lg p-3"
      style={{ background: colors.bg, border: `1px solid ${colors.border}` }}
    >
      <div className="flex items-center justify-between mb-1.5">
        <div className="flex items-center gap-1.5 text-2xs font-medium" style={{ color: 'var(--ink-500)' }}>
          {icon}
          <span>{label}</span>
        </div>
        {statusLabel && !isPending && (
          <span className={`status-badge status-badge--${status}`}>{statusLabel}</span>
        )}
      </div>

      <div className="metric-value" style={{ color: isPending ? 'var(--ink-100)' : 'var(--ink-900)' }}>
        {isPending ? '—' : `${value}${unit ? ` ${unit}` : ''}`}
      </div>

      {threshold && (
        <div className="text-2xs mt-1" style={{ color: 'var(--ink-100)' }}>
          {threshold}
        </div>
      )}
    </div>
  );
};

export const TelemetryBar: React.FC = () => {
  const { profile } = useDarukaaStore();

  const soc = profile.soc_percent;
  const rain = profile.annual_rainfall_mm;
  const temp = profile.max_temp_celsius;
  const crop = profile.land_use;

  const hasTelemetry =
    (soc !== null && soc !== undefined) ||
    (rain !== null && rain !== undefined) ||
    (temp !== null && temp !== undefined) ||
    Boolean(crop);

  if (!hasTelemetry) {
    return (
      <div
        className="rounded-xl p-5 border"
        style={{ background: 'white', borderColor: 'var(--line)' }}
      >
        <div className="flex items-center gap-2 mb-1">
          <LayoutGrid className="w-3.5 h-3.5" style={{ color: 'var(--nature-500)' }} />
          <p className="eyebrow eyebrow--accent">Environmental Telemetry</p>
        </div>
        <p className="text-sm" style={{ color: 'var(--ink-300)' }}>
          No metrics collected yet. Start the consultation to accumulate field data.
        </p>
      </div>
    );
  }

  return (
    <div
      className="rounded-xl overflow-hidden"
      style={{ background: 'white', border: '1px solid var(--line)' }}
    >
      <div
        className="px-5 py-3 border-b flex items-center justify-between"
        style={{ borderColor: 'var(--line-soft)', background: 'var(--soft-surface)' }}
      >
        <div className="flex items-center gap-2">
          <LayoutGrid className="w-3.5 h-3.5" style={{ color: 'var(--nature-500)' }} />
          <p className="eyebrow eyebrow--accent">Environmental Telemetry</p>
        </div>
        <span className="text-2xs font-mono" style={{ color: 'var(--ink-100)' }}>
          Slot-accumulated profile
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4">
        <MetricSlot
          label="Soil Carbon (SOC)"
          value={soc !== null && soc !== undefined ? String(soc) : null}
          unit="%"
          status={soc !== null && soc !== undefined ? (soc < 0.5 ? 'critical' : soc < 1.0 ? 'watch' : 'healthy') : 'neutral'}
          statusLabel={soc !== null && soc !== undefined ? (soc < 0.5 ? 'Critical' : soc < 1.0 ? 'Low' : 'Adequate') : undefined}
          threshold="FAO threshold: 0.5%"
          icon={<Sprout className="w-3 h-3" style={{ color: 'var(--state-watch)' }} />}
        />
        <MetricSlot
          label="Annual Rainfall"
          value={rain !== null && rain !== undefined ? String(rain) : null}
          unit="mm"
          status={rain !== null && rain !== undefined ? (rain < 350 ? 'critical' : rain < 500 ? 'high' : rain < 700 ? 'watch' : 'healthy') : 'neutral'}
          statusLabel={rain !== null && rain !== undefined ? (rain < 350 ? 'Arid' : rain < 500 ? 'Semi-arid' : rain < 700 ? 'Marginal' : 'Adequate') : undefined}
          threshold="Semi-arid: < 500 mm"
          icon={<Droplets className="w-3 h-3" style={{ color: 'var(--state-info)' }} />}
        />
        <MetricSlot
          label="Max Temperature"
          value={temp !== null && temp !== undefined ? String(temp) : null}
          unit="°C"
          status={temp !== null && temp !== undefined ? (temp >= 38 ? 'critical' : temp >= 32 ? 'high' : 'healthy') : 'neutral'}
          statusLabel={temp !== null && temp !== undefined ? (temp >= 38 ? 'Extreme heat' : temp >= 32 ? 'Heat stress' : 'Normal') : undefined}
          threshold="IPCC stress threshold: 32°C"
          icon={<Thermometer className="w-3 h-3" style={{ color: 'var(--state-high)' }} />}
        />
        <MetricSlot
          label="Land Use"
          value={crop ? crop.replace(/_/g, ' ') : null}
          status={crop ? (crop.includes('monoculture') ? 'critical' : crop === 'agroforestry' ? 'healthy' : 'watch') : 'neutral'}
          statusLabel={crop ? (crop.includes('monoculture') ? 'Habitat risk' : crop === 'agroforestry' ? 'Diversified' : 'Mixed') : undefined}
          threshold={crop?.includes('monoculture') ? 'Floral corridor severed' : ''}
          icon={<LayoutGrid className="w-3 h-3" style={{ color: 'var(--ink-300)' }} />}
        />
      </div>
    </div>
  );
};
