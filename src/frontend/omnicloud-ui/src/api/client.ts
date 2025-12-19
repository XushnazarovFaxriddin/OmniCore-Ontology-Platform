import axios, { AxiosInstance, AxiosError } from 'axios';
import type {
  Root,
  RootCreate,
  RootSummary,
  CausalityLink,
  CausalityLinkCreate,
  CausalitySummary,
  EpistemicAnnotation,
  EpistemicAnnotationCreate,
  EpistemicSummary,
  MMOClass,
  MMOClassCreate,
  MMOSlot,
  MMOSlotCreate,
  MMOMetrics,
  MMOSchema,
  GlobalStats,
  GlobalSample,
  GlobalSummary,
  SystemHealth,
  PaginatedResponse,
  SLMRequest,
  SLMResponse,
  ModelSetupStatus,
  ModelSetupStartResponse,
  RootTypeInference,
  EpistemicAnnotationResult,
  ConflictResolution,
  QualityAssessment,
  StrategicPlan,
  EntityEnhancement,
  ConflictType,
} from '../types';

// Get API base URL from environment or default
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';
const AUTH_USERNAME = import.meta.env.VITE_AUTH_USERNAME || 'dashboard';
const AUTH_SCOPES = (import.meta.env.VITE_AUTH_SCOPES || 'read,write')
  .split(',')
  .map((s: string) => s.trim())
  .filter(Boolean);

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Auth-only client (no interceptors) to avoid recursion when auto-fetching tokens.
const authClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

let tokenPromise: Promise<string | null> | null = null;

async function ensureAuthToken(): Promise<string | null> {
  const existing = localStorage.getItem('auth_token');
  if (existing) return existing;

  if (tokenPromise) return tokenPromise;

  tokenPromise = (async () => {
    try {
      const response = await authClient.post<{ access_token: string; token_type: string; expires_in: number }>(
        '/auth/token',
        { username: AUTH_USERNAME, scopes: AUTH_SCOPES }
      );
      const token = response.data?.access_token;
      if (token) {
        localStorage.setItem('auth_token', token);
        return token;
      }
      return null;
    } catch {
      return null;
    } finally {
      tokenPromise = null;
    }
  })();

  return tokenPromise;
}

// Request interceptor for authentication
api.interceptors.request.use(async (config) => {
  const url = config.url || '';
  const isTokenRequest = url.includes('/auth/token');
  if (isTokenRequest) return config;

  const token = localStorage.getItem('auth_token') || (await ensureAuthToken());
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;

    if (error.response?.status === 401) {
      const url = String(originalRequest?.url || '');
      const isTokenRequest = url.includes('/auth/token');

      localStorage.removeItem('auth_token');

      if (!isTokenRequest && originalRequest && !originalRequest._retry) {
        originalRequest._retry = true;
        const token = await ensureAuthToken();
        if (token) {
          originalRequest.headers = originalRequest.headers || {};
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return api(originalRequest);
        }
      }
    }
    return Promise.reject(error);
  }
);

// ==================== Auth API ====================

export const authApi = {
  getToken: async (username: string, scopes: string[] = []) => {
    const response = await api.post<{ access_token: string; token_type: string; expires_in: number }>(
      '/auth/token',
      { username, scopes }
    );
    return response.data;
  },
};

// ==================== Roots API ====================

export const rootsApi = {
  list: async (offset = 0, limit = 50, rootType?: string) => {
    const params: Record<string, string | number> = { offset, limit };
    if (rootType) params.root_type = rootType;
    const response = await api.get<PaginatedResponse<Root>>('/roots', { params });
    return response.data;
  },

  get: async (id: string) => {
    const response = await api.get<Root>(`/roots/${id}`);
    return response.data;
  },

  create: async (data: RootCreate) => {
    const response = await api.post<Root>('/roots', data);
    return response.data;
  },

  update: async (id: string, data: Partial<RootCreate>) => {
    const response = await api.put<Root>(`/roots/${id}`, data);
    return response.data;
  },

  delete: async (id: string) => {
    await api.delete(`/roots/${id}`);
  },

  getSummary: async () => {
    const response = await api.get<RootSummary>('/roots/summary');
    return response.data;
  },

  getByType: async (rootType: string, offset = 0, limit = 50) => {
    const response = await api.get<PaginatedResponse<Root>>(`/roots/by-type/${rootType}`, {
      params: { offset, limit },
    });
    return response.data;
  },
};

// ==================== Causality API ====================

export const causalityApi = {
  list: async (offset = 0, limit = 50, causalityType?: string) => {
    const params: Record<string, string | number> = { offset, limit };
    if (causalityType) params.causality_type = causalityType;
    const response = await api.get<PaginatedResponse<CausalityLink>>('/causality-links', { params });
    return response.data;
  },

  get: async (id: string) => {
    const response = await api.get<CausalityLink>(`/causality-links/${id}`);
    return response.data;
  },

  create: async (data: CausalityLinkCreate) => {
    const response = await api.post<CausalityLink>('/causality-links', data);
    return response.data;
  },

  update: async (id: string, data: Partial<CausalityLinkCreate>) => {
    const response = await api.put<CausalityLink>(`/causality-links/${id}`, data);
    return response.data;
  },

  delete: async (id: string) => {
    await api.delete(`/causality-links/${id}`);
  },

  getSummary: async () => {
    const response = await api.get<CausalitySummary>('/causality-summary');
    return response.data;
  },

  getByType: async (causalityType: string, offset = 0, limit = 50) => {
    const response = await api.get<PaginatedResponse<CausalityLink>>(
      `/causality-links/by-type/${causalityType}`,
      { params: { offset, limit } }
    );
    return response.data;
  },

  getByEntity: async (entityId: string, offset = 0, limit = 50) => {
    const response = await api.get<PaginatedResponse<CausalityLink>>(
      `/causality-links/by-entity/${entityId}`,
      { params: { offset, limit } }
    );
    return response.data;
  },
};

// ==================== Epistemic API ====================

export const epistemicApi = {
  list: async (offset = 0, limit = 50, basis?: string) => {
    const params: Record<string, string | number> = { offset, limit };
    if (basis) params.basis = basis;
    const response = await api.get<PaginatedResponse<EpistemicAnnotation>>('/annotations', { params });
    return response.data;
  },

  get: async (id: string) => {
    const response = await api.get<EpistemicAnnotation>(`/annotations/${id}`);
    return response.data;
  },

  create: async (data: EpistemicAnnotationCreate) => {
    const response = await api.post<EpistemicAnnotation>('/annotations', data);
    return response.data;
  },

  update: async (id: string, data: Partial<EpistemicAnnotationCreate>) => {
    const response = await api.put<EpistemicAnnotation>(`/annotations/${id}`, data);
    return response.data;
  },

  delete: async (id: string) => {
    await api.delete(`/annotations/${id}`);
  },

  getSummary: async () => {
    const response = await api.get<EpistemicSummary>('/annotations/summary');
    return response.data;
  },

  getByBasis: async (basis: string, offset = 0, limit = 50) => {
    const response = await api.get<PaginatedResponse<EpistemicAnnotation>>(
      `/annotations/by-basis/${basis}`,
      { params: { offset, limit } }
    );
    return response.data;
  },

  getForEntity: async (entityId: string, offset = 0, limit = 50) => {
    const response = await api.get<PaginatedResponse<EpistemicAnnotation>>(
      `/entities/${entityId}/annotations`,
      { params: { offset, limit } }
    );
    return response.data;
  },
};

// ==================== MMO API ====================

export const mmoApi = {
  // Classes
  listClasses: async (offset = 0, limit = 100) => {
    const response = await api.get<PaginatedResponse<MMOClass>>('/classes', {
      params: { offset, limit },
    });
    return response.data;
  },

  getClass: async (id: string) => {
    const response = await api.get<MMOClass>(`/classes/${id}`);
    return response.data;
  },

  createClass: async (data: MMOClassCreate) => {
    const response = await api.post<MMOClass>('/classes', data);
    return response.data;
  },

  updateClass: async (id: string, data: Partial<MMOClassCreate>) => {
    const response = await api.put<MMOClass>(`/classes/${id}`, data);
    return response.data;
  },

  deleteClass: async (id: string) => {
    await api.delete(`/classes/${id}`);
  },

  // Slots
  listSlots: async (offset = 0, limit = 100) => {
    const response = await api.get<PaginatedResponse<MMOSlot>>('/slots', {
      params: { offset, limit },
    });
    return response.data;
  },

  getSlot: async (id: string) => {
    const response = await api.get<MMOSlot>(`/slots/${id}`);
    return response.data;
  },

  createSlot: async (data: MMOSlotCreate) => {
    const response = await api.post<MMOSlot>('/slots', data);
    return response.data;
  },

  deleteSlot: async (id: string) => {
    await api.delete(`/slots/${id}`);
  },

  // Metrics
  getMetrics: async () => {
    const response = await api.get<MMOMetrics>('/metrics');
    return response.data;
  },

  recalculateMetrics: async () => {
    const response = await api.post<MMOMetrics>('/metrics/recalculate');
    return response.data;
  },

  // Schema
  getSchema: async () => {
    const response = await api.get<MMOSchema>('/schema');
    return response.data;
  },
};

// ==================== Global API ====================

export const globalApi = {
  getStats: async () => {
    const response = await api.get<GlobalStats>('/global/stats');
    return response.data;
  },

  getSample: async (sampleSize = 5) => {
    const response = await api.get<GlobalSample>('/global/sample', {
      params: { sample_size: sampleSize },
    });
    return response.data;
  },

  getSummary: async () => {
    const response = await api.get<GlobalSummary>('/global/summary');
    return response.data;
  },

  getSystemHealth: async () => {
    const response = await api.get<SystemHealth>('/system/health');
    return response.data;
  },
};

// ==================== Health API ====================

export const healthApi = {
  getOverview: async () => {
    const response = await api.get<SystemHealth>('/health/overview');
    return response.data;
  },
};

// ==================== AI/SLM API ====================

const SLM_API_URL = import.meta.env.VITE_SLM_API_URL || '/api/slm';

const slmApi: AxiosInstance = axios.create({
  baseURL: SLM_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // Longer timeout for AI operations
});

slmApi.interceptors.request.use(async (config) => {
  const token = localStorage.getItem('auth_token') || (await ensureAuthToken());
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

slmApi.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');

      if (originalRequest && !originalRequest._retry) {
        originalRequest._retry = true;
        const token = await ensureAuthToken();
        if (token) {
          originalRequest.headers = originalRequest.headers || {};
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return slmApi(originalRequest);
        }
      }
    }
    return Promise.reject(error);
  }
);

export const aiApi = {
  // Health & Models
  getHealth: async () => {
    const response = await slmApi.get<any>('/health');
    const providers = response.data?.details?.providers ?? response.data?.providers ?? {};
    return { status: response.data?.status ?? 'unknown', providers };
  },

  listModels: async () => {
    // Prefer backend model status endpoint (stable shape) and map to UI-friendly list.
    const response = await slmApi.get<ModelSetupStatus>('/models/status');
    const status = response.data;

    if (!status?.ollama_available || !Array.isArray(status.models_available)) {
      return [];
    }

    return status.models_available.map((modelName) => ({
      id: modelName,          // Use actual model name so it can be passed back to /generate
      name: modelName,
      provider: 'Ollama',
      status: 'available',
      capabilities: ['text-generation', 'analysis', 'reasoning'],
    }));
  },

  getModelStatus: async () => {
    const response = await slmApi.get<ModelSetupStatus>('/models/status');
    return response.data;
  },

  setupModels: async () => {
    const response = await slmApi.post<ModelSetupStartResponse>('/models/setup');
    return response.data;
  },

  // Core Generation
  generate: async (request: SLMRequest) => {
    const response = await slmApi.post<SLMResponse>('/generate', request);
    return response.data;
  },

  // Chat - for conversational AI
  chat: async (messages: { role: string; content: string }[], context?: string) => {
    const systemPrompt = context
      ? `You are OmniCore AI Assistant, an expert in ontology management and knowledge engineering. Context: ${context}`
      : 'You are OmniCore AI Assistant, an expert in ontology management, knowledge engineering, and semantic technologies.';

    const prompt = messages.map(m => `${m.role}: ${m.content}`).join('\n');
    const response = await slmApi.post<SLMResponse>('/generate', {
      prompt: `${systemPrompt}\n\n${prompt}\nassistant:`,
      task_type: 'general',
      max_tokens: 1024,
      temperature: 0.7,
    });
    return response.data;
  },

  // Root Type Inference
  inferRootType: async (entityName: string, description: string, context?: string, source?: string) => {
    const response = await slmApi.post<RootTypeInference>('/infer-root-type', {
      entity_name: entityName,
      description,
      context: context || '',
      source: source || '',
    });
    return response.data;
  },

  batchInferRootTypes: async (entities: { entity_name: string; description: string; context?: string; source?: string }[]) => {
    const response = await slmApi.post<RootTypeInference[]>('/batch-infer-root-types', entities);
    return response.data;
  },

  // Causality Extraction
  extractCausality: async (entities: string[], descriptions: string[], context?: string) => {
    const response = await slmApi.post<{ relationships: Array<{
      source: string;
      target: string;
      causality_type: string;
      confidence: number;
      reasoning: string;
    }> }>('/extract-causality', {
      entities,
      descriptions,
      context: context || '',
    });
    return response.data;
  },

  // Epistemic Annotation
  annotateEpistemic: async (entityName: string, claim: string, source?: string, context?: string) => {
    const response = await slmApi.post<EpistemicAnnotationResult>('/annotate-epistemic', {
      entity_name: entityName,
      claim,
      source: source || '',
      context: context || '',
    });
    return response.data;
  },

  // Conflict Resolution
  resolveConflict: async (
    conflictId: string,
    conflictType: ConflictType,
    entityA: string,
    entityB: string,
    description: string,
    maxRounds?: number
  ) => {
    const response = await slmApi.post<ConflictResolution>('/resolve-conflict', {
      conflict_id: conflictId,
      conflict_type: conflictType,
      entity_a: entityA,
      entity_b: entityB,
      description,
      max_rounds: maxRounds || 5,
    });
    return response.data;
  },

  // Quality Assessment
  assessQuality: async (
    name: string,
    source: string,
    domain: string,
    tripleCount: number,
    sampleClasses: string[],
    sampleProperties: string[]
  ) => {
    const response = await slmApi.post<QualityAssessment>('/assess-quality', {
      name,
      source,
      domain,
      triple_count: tripleCount,
      sample_classes: sampleClasses,
      sample_properties: sampleProperties,
    });
    return response.data;
  },

  // Strategic Planning
  generateStrategicPlan: async (metrics: Record<string, number>, gaps: string[]) => {
    const response = await slmApi.post<StrategicPlan>('/strategic-plan', {
      metrics,
      gaps,
    });
    return response.data;
  },

  // Entity Enhancement
  enhanceEntity: async (entityId: string, entityName: string, entityDescription: string, enhancementTypes?: string[]) => {
    const response = await slmApi.post<{ enhancements: EntityEnhancement[] }>('/enhance-entity', {
      entity_id: entityId,
      entity_name: entityName,
      entity_description: entityDescription,
      enhancement_types: enhancementTypes || ['root_hint', 'epistemic'],
    });
    return response.data;
  },

  // Smart Search - AI-powered semantic search
  smartSearch: async (query: string, entityTypes?: string[], limit?: number) => {
    const resultLimit = limit ?? 10;
    const response = await slmApi.post<SLMResponse>('/generate', {
      prompt: `Analyze this search query and identify relevant ontology concepts:
Query: "${query}"
${entityTypes ? `Filter to types: ${entityTypes.join(', ')}` : ''}

Respond with JSON containing:
- interpreted_query: what the user is looking for
- suggested_entities: list of entity names that might match (max ${resultLimit})
- related_concepts: related ontological concepts
- search_tips: suggestions for refining the search`,
      task_type: 'general',
      max_tokens: 512,
      temperature: 0.3,
    });
    return response.data;
  },

  // Ontology Suggestions
  suggestOntologyImprovements: async (stats: Record<string, number>) => {
    const response = await slmApi.post<SLMResponse>('/generate', {
      prompt: `Based on these ontology statistics, suggest improvements:
${JSON.stringify(stats, null, 2)}

Provide JSON with:
- gaps: areas needing more coverage
- quality_issues: potential quality problems
- recommendations: specific actionable improvements
- priority: high/medium/low for each recommendation`,
      task_type: 'general',
      max_tokens: 1024,
      temperature: 0.4,
    });
    return response.data;
  },
};

export default api;
