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

// AI/SLM Types
export type AIAgentRole = 'platonist' | 'nominalist' | 'pragmatist' | 'moderator';
export type ConflictType = 'classification' | 'relationship' | 'property' | 'definition';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: Record<string, unknown>;
}

export interface AIModel {
  id: string;
  name: string;
  provider: string;
  status: 'available' | 'unavailable' | 'loading';
  capabilities: string[];
}

export interface SLMRequest {
  prompt: string;
  task_type?: string;
  max_tokens?: number;
  temperature?: number;
  model?: string;
}

export interface SLMResponse {
  response: string;
  model_id: string;
  confidence: number;
  tokens_used: number;
  latency_ms: number;
}

export interface RootTypeInference {
  entity_name: string;
  root_type: RootType;
  confidence: number;
  reasoning: string;
}

export interface CausalityExtraction {
  source: string;
  target: string;
  causality_type: CausalityType;
  confidence: number;
  reasoning: string;
}

export interface EpistemicAnnotationResult {
  certainty: number;
  basis: EpistemicBasis;
  reasoning: string;
  supporting_evidence: string[];
  source_reliability: number;
}

export interface DebateRound {
  round_number: number;
  agent_role: AIAgentRole;
  argument: string;
  confidence: number;
  supporting_evidence: string[];
}

export interface ConflictResolution {
  conflict_id: string;
  rounds: DebateRound[];
  consensus_reached: boolean;
  consensus_threshold: number;
  final_resolution: string;
  supporting_agents: AIAgentRole[];
  contextual_axiom?: string;
}

export interface QualityAssessment {
  name: string;
  overall_score: number;
  consistency_score: number;
  completeness_score: number;
  clarity_score: number;
  recommendation: 'integrate' | 'review' | 'reject';
  issues: string[];
  suggestions: string[];
}

export interface StrategicPlan {
  period: string;
  objectives: string[];
  actions: string[];
  metrics_targets: Record<string, number>;
  requires_human_approval: boolean;
  priority_areas: string[];
}

export interface EntityEnhancement {
  entity_id: string;
  enhancement_type: string;
  original_value?: string;
  enhanced_value: string;
  confidence: number;
  rationale: string;
  model_id: string;
}
