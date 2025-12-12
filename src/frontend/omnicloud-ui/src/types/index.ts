// Root Types
export type RootType = 'EXTANT' | 'ABSTRACT' | 'MENTAL' | 'FICTIVE';

export interface Root {
  id: string;
  name: string;
  root_type: RootType;
  description?: string;
  metadata?: Record<string, unknown>;
  import_source?: string;
  ai_enhancement_trace?: string;
  created_at: string;
  updated_at: string;
}

export interface RootCreate {
  name: string;
  root_type: RootType;
  description?: string;
  metadata?: Record<string, unknown>;
  import_source?: string;
}

export interface RootSummary {
  total_count: number;
  by_type: Record<string, number>;
}

// Causality Types
export type CausalityType = 'EFFICIENT' | 'FINAL' | 'MATERIAL' | 'FORMAL' | 'EMERGENT';

export interface CausalityLink {
  id: string;
  source_entity_id: string;
  target_entity_id: string;
  causality_type: CausalityType;
  confidence: number;
  description?: string;
  metadata?: Record<string, unknown>;
  ai_confidence?: number;
  rationale_trace?: string;
  created_at: string;
  updated_at: string;
}

export interface CausalityLinkCreate {
  source_entity_id: string;
  target_entity_id: string;
  causality_type: CausalityType;
  confidence?: number;
  description?: string;
  metadata?: Record<string, unknown>;
}

export interface CausalitySummary {
  total_count: number;
  by_type: Record<string, number>;
  avg_confidence: number;
}

// Epistemic Types
export type EpistemicBasis = 'axiomatic' | 'empirical' | 'consensus' | 'speculative';

export interface EpistemicAnnotation {
  id: string;
  entity_id: string;
  certainty: number;
  basis: EpistemicBasis;
  source?: string;
  note?: string;
  timestamp: string;
}

export interface EpistemicAnnotationCreate {
  entity_id: string;
  certainty: number;
  basis: EpistemicBasis;
  source?: string;
  note?: string;
}

export interface EpistemicSummary {
  total_count: number;
  by_basis: Record<string, number>;
  avg_certainty: number;
  certainty_distribution: Record<string, number>;
}

// MMO Types
export interface MMOClass {
  id: string;
  name: string;
  description?: string;
  parent_class_id?: string;
  properties: string[];
  constraints?: Record<string, unknown>;
  created_at: string;
}

export interface MMOClassCreate {
  name: string;
  description?: string;
  parent_class_id?: string;
  properties?: string[];
  constraints?: Record<string, unknown>;
}

export interface MMOSlot {
  id: string;
  name: string;
  domain_class_id: string;
  range_type: string;
  cardinality: string;
  description?: string;
  created_at: string;
}

export interface MMOSlotCreate {
  name: string;
  domain_class_id: string;
  range_type: string;
  cardinality?: string;
  description?: string;
}

export interface MMOMetrics {
  completeness: number;
  coverage: number;
  coherence: number;
  utility: number;
  inclusivity: number;
  mmo_score: number;
  last_updated: string;
}

export interface MMOSchema {
  classes: MMOClass[];
  slots: MMOSlot[];
  metrics: MMOMetrics;
}

// Global Types
export interface GlobalStats {
  total_roots: number;
  total_causality_links: number;
  total_epistemic_annotations: number;
  total_mmo_classes: number;
  total_mmo_slots: number;
  roots_by_type: Record<string, number>;
  causality_by_type: Record<string, number>;
  epistemic_by_basis: Record<string, number>;
  avg_causality_confidence: number;
  avg_epistemic_certainty: number;
  last_updated: string;
}

export interface GlobalSample {
  sample_roots: Root[];
  sample_causality_links: CausalityLink[];
  sample_annotations: EpistemicAnnotation[];
  sample_mmo_classes: MMOClass[];
}

export interface GlobalSummary {
  stats: GlobalStats;
  sample: GlobalSample;
  health: SystemHealth;
}

// Health Types
export type HealthStatus = 'healthy' | 'degraded' | 'unhealthy' | 'up' | 'down';

export interface ServiceHealth {
  name: string;
  status: HealthStatus;
  latency_ms: number;
  last_check: string;
  error?: string;
}

export interface SystemHealth {
  status: HealthStatus;
  services: Record<string, ServiceHealth>;
  timestamp: string;
}

// Pagination Types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  offset: number;
  limit: number;
  has_more: boolean;
}
