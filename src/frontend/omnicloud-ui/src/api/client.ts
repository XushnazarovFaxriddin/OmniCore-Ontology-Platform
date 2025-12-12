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
} from '../types';

// Get API base URL from environment or default
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor for authentication
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
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

export default api;
