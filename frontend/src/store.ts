import { create } from 'zustand';
import { API_BASE_URL } from './config';

export interface CausalFactor {
  stressor: string;
  severity: string;
  why: string;
  how: string;
  what: string;
}

export interface Assessment {
  compound_risk: string;
  stress_levels: {
    soil_stress?: string;
    water_stress?: string;
    biodiversity_stress?: string;
    thermal_stress?: string;
    ph_stress?: string;
  };
  causal_factors: CausalFactor[];
  water_penalty_active: boolean;
  summary_text: string;
  thermal_stress?: number;
  ph_stress?: number;
}

export interface Recommendation {
  rank: number;
  slug: string;
  name: string;
  category: string;
  decision_score: number;
  water_penalty_applied: boolean;
  time_horizon?: {
    category: string;
    seasons: number;
    note: string;
  };
  dsi_components?: {
    environmental_fit: number;
    evidence_strength: number;
    biodiversity_gain: number;
    soil_gain: number;
    feasibility: number;
    risk_penalty: number;
  };
  primary_benefits: Record<string, any>;
  tradeoffs: Array<{ risk: string; severity: string; mitigation: string }>;
  evidence_sources: Array<{
    chunk_id: string;
    title: string;
    publisher: string;
    year: number;
    doi: string;
    excerpt: string;
  }>;
}

export interface ValidationReport {
  confidence_score: number;
  confidence_badge: 'HIGH' | 'MODERATE' | 'LOW';
  claims_evaluated: number;
  claims_supported: number;
  claims_stripped: number;
  evidence_ledger: Array<{
    claim: string;
    status: string;
    action: string;
    detail: string;
  }>;
}

export interface EnvironmentalProfile {
  soc_percent?: number | null;
  annual_rainfall_mm?: number | null;
  max_temp_celsius?: number | null;
  land_use?: string | null;
  soil_ph?: number | null;
}

interface DarukaaState {
  sessionId: string;
  messages: Array<{ role: 'user' | 'assistant'; content: string }>;
  profile: EnvironmentalProfile;
  assessment: Assessment | null;
  recommendations: Recommendation[];
  validation: ValidationReport | null;
  selectedEvidence: any | null;
  isLoading: boolean;
  error: string | null;

  sendMessage: (text: string) => Promise<void>;
  setSelectedEvidence: (chunk: any | null) => void;
  loadPreset: (preset: 'semi_arid_wheat' | 'healthy_pasture') => Promise<void>;
  resetSession: () => void;
}

export const useDarukaaStore = create<DarukaaState>((set, get) => ({
  sessionId: 'session-' + Math.random().toString(36).substring(2, 9),
  messages: [
    {
      role: 'assistant',
      content: 'Welcome to **Darukaa.Earth**. I am your AI Environmental Scientist & Decision Engine. Describe your field symptoms or provide your Soil Organic Carbon (SOC), annual rainfall, and cropping system to evaluate compound degradation risk.'
    }
  ],
  profile: {},
  assessment: null,
  recommendations: [],
  validation: null,
  selectedEvidence: null,
  isLoading: false,
  error: null,

  resetSession: () => set({
    sessionId: 'session-' + Math.random().toString(36).substring(2, 9),
    messages: [
      {
        role: 'assistant',
        content: 'Welcome to **Darukaa.Earth**. I am your AI Environmental Scientist & Decision Engine. Describe your field symptoms or provide your Soil Organic Carbon (SOC), annual rainfall, and cropping system to evaluate compound degradation risk.'
      }
    ],
    profile: {},
    assessment: null,
    recommendations: [],
    validation: null,
    selectedEvidence: null,
    isLoading: false,
    error: null,
  }),

  setSelectedEvidence: (chunk) => set({ selectedEvidence: chunk }),

  sendMessage: async (text: string) => {
    const { sessionId, messages, profile } = get();
    const updatedMessages = [...messages, { role: 'user' as const, content: text }];
    set({ messages: updatedMessages, isLoading: true, error: null });

    try {
      const res = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message: text })
      });

      if (!res.ok) {
        throw new Error(`API returned HTTP ${res.status}`);
      }

      const data = await res.json();
      set({
        isLoading: false,
        messages: [...updatedMessages, { role: 'assistant', content: data.response }],
        profile: data.profile || profile,
        assessment: data.assessment || null,
        recommendations: data.recommendations || [],
        validation: data.validation || null
      });
    } catch (err: any) {
      set({
        isLoading: false,
        error: err.message || 'Failed to connect to Darukaa API',
        messages: [
          ...updatedMessages,
          { role: 'assistant', content: `⚠️ Error: ${err.message}. Please check that the backend is active.` }
        ]
      });
    }
  },

  loadPreset: async (preset) => {
    if (preset === 'semi_arid_wheat') {
      await get().sendMessage('SOC is 0.35%, annual rainfall is 450 mm, max temperature is 34°C, and we grow wheat monoculture.');
    } else {
      await get().sendMessage('SOC is 2.4%, annual rainfall is 850 mm, and we manage diversified agroforestry.');
    }
  }
}));
