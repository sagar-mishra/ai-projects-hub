import { create } from 'zustand';
import { api, Agent, Workflow, WorkflowRun, Message, LogEntry, Approval } from '../api/client';

interface PlatformState {
  agents: Agent[];
  workflows: Workflow[];
  runs: WorkflowRun[];
  activeRunId: string | null;
  activeRun: WorkflowRun | null;
  runLogs: LogEntry[];
  runMessages: Message[];
  pendingApprovals: Approval[];
  templates: any[];
  isLoading: boolean;
  error: string | null;

  fetchAgents: () => Promise<void>;
  fetchWorkflows: () => Promise<void>;
  fetchRuns: (page?: number, limit?: number, status?: string) => Promise<void>;
  fetchPendingApprovals: () => Promise<void>;
  fetchTemplates: () => Promise<void>;
  
  createAgent: (agent: Agent) => Promise<Agent>;
  updateAgent: (id: string, agent: Partial<Agent>) => Promise<Agent>;
  deleteAgent: (id: string) => Promise<void>;
  clearAgentMemory: (id: string) => Promise<void>;

  createWorkflow: (wf: Workflow) => Promise<Workflow>;
  updateWorkflow: (id: string, wf: Partial<Workflow>) => Promise<Workflow>;
  deleteWorkflow: (id: string) => Promise<void>;
  runWorkflow: (id: string, message: string) => Promise<string>;

  loadTemplate: (key: string) => Promise<Workflow>;
  setActiveRunId: (id: string | null) => Promise<void>;
  decideApproval: (id: string, action: 'approve' | 'reject') => Promise<void>;
  addLiveLog: (log: LogEntry) => void;
  setLiveLogs: (logs: LogEntry[]) => void;
  setLiveMessages: (msgs: Message[]) => void;
}

export const useStore = create<PlatformState>((set, get) => ({
  agents: [],
  workflows: [],
  runs: [],
  activeRunId: null,
  activeRun: null,
  runLogs: [],
  runMessages: [],
  pendingApprovals: [],
  templates: [],
  isLoading: false,
  error: null,

  fetchAgents: async () => {
    set({ isLoading: true });
    try {
      const data = await api.getAgents();
      set({ agents: data, isLoading: false });
    } catch (e: any) {
      set({ error: e.message, isLoading: false });
    }
  },

  fetchWorkflows: async () => {
    set({ isLoading: true });
    try {
      const data = await api.getWorkflows();
      set({ workflows: data, isLoading: false });
    } catch (e: any) {
      set({ error: e.message, isLoading: false });
    }
  },

  fetchRuns: async (page = 1, limit = 20, status?: string) => {
    set({ isLoading: true });
    try {
      const data = await api.getRuns(page, limit, status);
      set({ runs: data.runs, isLoading: false });
    } catch (e: any) {
      set({ error: e.message, isLoading: false });
    }
  },

  fetchPendingApprovals: async () => {
    try {
      const data = await api.getApprovals('pending');
      set({ pendingApprovals: data });
    } catch (e: any) {
      console.error(e);
    }
  },

  fetchTemplates: async () => {
    try {
      const data = await api.getTemplates();
      set({ templates: data });
    } catch (e: any) {
      console.error(e);
    }
  },

  createAgent: async (agent) => {
    const data = await api.createAgent(agent);
    get().fetchAgents();
    return data;
  },

  updateAgent: async (id, agent) => {
    const data = await api.updateAgent(id, agent);
    get().fetchAgents();
    return data;
  },

  deleteAgent: async (id) => {
    await api.deleteAgent(id);
    get().fetchAgents();
  },

  clearAgentMemory: async (id) => {
    await api.clearAgentMemory(id);
  },

  createWorkflow: async (wf) => {
    const data = await api.createWorkflow(wf);
    get().fetchWorkflows();
    return data;
  },

  updateWorkflow: async (id, wf) => {
    const data = await api.updateWorkflow(id, wf);
    get().fetchWorkflows();
    return data;
  },

  deleteWorkflow: async (id) => {
    await api.deleteWorkflow(id);
    get().fetchWorkflows();
  },

  runWorkflow: async (id, message) => {
    const result = await api.runWorkflow(id, { message });
    get().fetchRuns();
    return result.run_id;
  },

  loadTemplate: async (key) => {
    const wf = await api.loadTemplate(key);
    get().fetchWorkflows();
    return wf;
  },

  setActiveRunId: async (id) => {
    set({ activeRunId: id, runLogs: [], runMessages: [] });
    if (!id) {
      set({ activeRun: null });
      return;
    }
    
    try {
      const run = await api.getRun(id);
      const logs = await api.getRunLogs(id);
      const msgs = await api.getRunMessages(id);
      set({ activeRun: run, runLogs: logs, runMessages: msgs });
    } catch (e: any) {
      console.error(e);
    }
  },

  decideApproval: async (id, action) => {
    await api.decideApproval(id, action);
    get().fetchPendingApprovals();
    
    // Refresh active run if showing
    const activeId = get().activeRunId;
    if (activeId) {
      get().setActiveRunId(activeId);
    }
  },

  addLiveLog: (log) => {
    set((state) => {
      // Check if log already exists by checking payload or message
      if (state.runLogs.some(l => l.id === log.id)) {
        return {};
      }
      
      const newLogs = [...state.runLogs, log];
      
      // If it is an agent message event, update live messages too
      let newMessages = state.runMessages;
      if (log.event_type === 'agent_message' && log.payload) {
        const payload = log.payload;
        const exists = state.runMessages.some(m => m.content === payload.content && m.sender_agent === payload.agent_name);
        if (!exists) {
          newMessages = [
            ...state.runMessages,
            {
              id: log.id || Math.random().toString(),
              run_id: log.run_id,
              sender_agent: payload.agent_name || 'agent',
              content: payload.content || '',
              role: 'assistant',
              timestamp: log.timestamp
            }
          ];
        }
      }

      return {
        runLogs: newLogs,
        runMessages: newMessages
      };
    });
  },

  setLiveLogs: (logs) => set({ runLogs: logs }),
  setLiveMessages: (msgs) => set({ runMessages: msgs }),
}));
