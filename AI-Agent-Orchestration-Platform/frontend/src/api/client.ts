import axios from 'axios';

const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';
export const API_URL = API_BASE;
export const WS_URL = API_BASE.replace(/^http/, 'ws');

const client = axios.create({
  baseURL: `${API_BASE}/api`,
});

export interface Agent {
  id?: string;
  name: string;
  role?: string;
  description?: string;
  system_prompt: string;
  model: string;
  tools_json: string;
  memory_enabled: boolean;
  channel?: string;
  schedule_cron?: string;
  max_tokens: number;
  temperature: number;
  max_iterations: number;
  guardrails_json: string;
  created_at?: string;
  updated_at?: string;
}

export interface Workflow {
  id?: string;
  name: string;
  description?: string;
  graph_json: string;
  version?: number;
  is_template?: boolean;
  template_name?: string;
  created_at?: string;
  updated_at?: string;
}

export interface WorkflowRun {
  id: string;
  workflow_id: string;
  status: 'pending' | 'running' | 'waiting_approval' | 'completed' | 'failed';
  input_json?: string;
  output_json?: string;
  started_at: string;
  completed_at?: string;
  token_count: number;
  cost_usd: number;
  error_message?: string;
}

export interface Message {
  id: string;
  run_id: string;
  sender_agent: string;
  receiver_agent?: string;
  content: string;
  role: string;
  timestamp: string;
}

export interface LogEntry {
  id: string;
  run_id: string;
  agent_id?: string;
  level: string;
  event_type: string;
  payload: any;
  timestamp: string;
}

export interface Approval {
  id: string;
  run_id: string;
  node_id: string;
  question: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
  decided_at?: string;
}

export const api = {
  // Agents CRUD
  getAgents: () => client.get<Agent[]>('/agents').then(r => r.data),
  getAgent: (id: string) => client.get<Agent>(`/agents/${id}`).then(r => r.data),
  createAgent: (agent: Agent) => client.post<Agent>('/agents', agent).then(r => r.data),
  updateAgent: (id: string, agent: Partial<Agent>) => client.put<Agent>(`/agents/${id}`, agent).then(r => r.data),
  deleteAgent: (id: string) => client.delete(`/agents/${id}`).then(r => r.data),
  getAgentMemory: (id: string) => client.get<any[]>(`/agents/${id}/memory`).then(r => r.data),
  clearAgentMemory: (id: string) => client.delete(`/agents/${id}/memory`).then(r => r.data),

  // Workflows CRUD
  getWorkflows: () => client.get<Workflow[]>('/workflows').then(r => r.data),
  getWorkflow: (id: string) => client.get<Workflow>(`/workflows/${id}`).then(r => r.data),
  createWorkflow: (wf: Workflow) => client.post<Workflow>('/workflows', wf).then(r => r.data),
  updateWorkflow: (id: string, wf: Partial<Workflow>) => client.put<Workflow>(`/workflows/${id}`, wf).then(r => r.data),
  deleteWorkflow: (id: string) => client.delete(`/workflows/${id}`).then(r => r.data),
  runWorkflow: (id: string, input: { message: string }) => client.post<{ run_id: string; status: string }>(`/workflows/${id}/run`, input).then(r => r.data),

  // Templates
  getTemplates: () => client.get<any[]>('/templates').then(r => r.data),
  loadTemplate: (key: string) => client.post<Workflow>(`/templates/${key}/load`).then(r => r.data),

  // Runs
  getRuns: (page = 1, limit = 20, status?: string) => 
    client.get<{ total: number; page: number; limit: number; runs: WorkflowRun[] }>('/runs', { params: { page, limit, status } }).then(r => r.data),
  getRun: (id: string) => client.get<WorkflowRun>(`/runs/${id}`).then(r => r.data),
  getRunMessages: (id: string) => client.get<Message[]>(`/runs/${id}/messages`).then(r => r.data),
  getRunLogs: (id: string) => client.get<LogEntry[]>(`/runs/${id}/logs`).then(r => r.data),

  // Approvals
  getApprovals: (status = 'pending') => client.get<Approval[]>('/approvals', { params: { status } }).then(r => r.data),
  decideApproval: (id: string, action: 'approve' | 'reject') => client.post<any>(`/approvals/${id}/decide`, { action }).then(r => r.data),

  // Health
  getHealth: () => axios.get(`${API_BASE}/health`).then(r => r.data),
};
