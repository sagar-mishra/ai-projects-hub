import React, { useEffect, useState } from 'react';
import { useStore } from '../store/useStore';
import { api, Agent } from '../api/client';
import { 
  Bot, 
  Trash2, 
  Edit3, 
  Layers, 
  BrainCircuit, 
  Cpu, 
  AlertTriangle, 
  X,
  Sparkles,
  Plus
} from 'lucide-react';

const AVAILABLE_TOOLS = ['web_search', 'http_request', 'calculator', 'summarizer'];
const AVAILABLE_MODELS = [
  { id: 'llama-3.1-8b-instant', name: 'Llama 3.1 8B (Groq)' },
  { id: 'llama3-70b-8192', name: 'Llama 3 70B (Groq)' },
  { id: 'mixtral-8x7b-32768', name: 'Mixtral 8x7B (Groq)' },
  { id: 'llama3', name: 'Llama 3 (Local Ollama)' },
];

const Agents: React.FC = () => {
  const { agents, fetchAgents, createAgent, updateAgent, deleteAgent, clearAgentMemory } = useStore();

  const [isOpen, setIsOpen] = useState(false);
  const [editingAgent, setEditingAgent] = useState<Agent | null>(null);
  const [memoryAgent, setMemoryAgent] = useState<Agent | null>(null);
  const [memoryItems, setMemoryItems] = useState<any[]>([]);

  // Form State
  const [name, setName] = useState('');
  const [role, setRole] = useState('');
  const [description, setDescription] = useState('');
  const [systemPrompt, setSystemPrompt] = useState('');
  const [model, setModel] = useState('llama-3.1-8b-instant');
  const [memoryEnabled, setMemoryEnabled] = useState(true);
  const [channel, setChannel] = useState('');
  const [scheduleCron, setScheduleCron] = useState('');
  const [maxTokens, setMaxTokens] = useState(1000);
  const [temperature, setTemperature] = useState(0.7);
  const [maxIterations, setMaxIterations] = useState(10);
  const [forbiddenTopics, setForbiddenTopics] = useState('');
  
  // Enabled tools local state
  const [enabledTools, setEnabledTools] = useState<string[]>([]);

  useEffect(() => {
    fetchAgents();
  }, []);

  const openNewForm = () => {
    setEditingAgent(null);
    setName('');
    setRole('');
    setDescription('');
    setSystemPrompt('');
    setModel('llama-3.1-8b-instant');
    setMemoryEnabled(true);
    setChannel('');
    setScheduleCron('');
    setMaxTokens(1000);
    setTemperature(0.7);
    setMaxIterations(10);
    setForbiddenTopics('');
    setEnabledTools([]);
    setIsOpen(true);
  };

  const openEditForm = (agent: Agent) => {
    setEditingAgent(agent);
    setName(agent.name);
    setRole(agent.role || '');
    setDescription(agent.description || '');
    setSystemPrompt(agent.system_prompt);
    setModel(agent.model);
    setMemoryEnabled(agent.memory_enabled);
    setChannel(agent.channel || '');
    setScheduleCron(agent.schedule_cron || '');
    setMaxTokens(agent.max_tokens);
    setTemperature(agent.temperature);
    setMaxIterations(agent.max_iterations);
    
    // Parse tools list
    try {
      setEnabledTools(JSON.parse(agent.tools_json));
    } catch {
      setEnabledTools([]);
    }

    // Parse forbidden topics guardrails
    try {
      const guardrails = JSON.parse(agent.guardrails_json);
      setForbiddenTopics(guardrails.forbidden_topics?.join(', ') || '');
    } catch {
      setForbiddenTopics('');
    }

    setIsOpen(true);
  };

  const handleToolToggle = (tool: string) => {
    if (enabledTools.includes(tool)) {
      setEnabledTools(enabledTools.filter(t => t !== tool));
    } else {
      setEnabledTools([...enabledTools, tool]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const guardrailsObj = {
      forbidden_topics: forbiddenTopics.split(',').map(t => t.trim()).filter(Boolean)
    };

    const agentData: Agent = {
      name,
      role,
      description,
      system_prompt: systemPrompt,
      model,
      tools_json: JSON.stringify(enabledTools),
      memory_enabled: memoryEnabled,
      channel: channel || undefined,
      schedule_cron: scheduleCron || undefined,
      max_tokens: Number(maxTokens),
      temperature: Number(temperature),
      max_iterations: Number(maxIterations),
      guardrails_json: JSON.stringify(guardrailsObj)
    };

    try {
      if (editingAgent && editingAgent.id) {
        await updateAgent(editingAgent.id, agentData);
      } else {
        await createAgent(agentData);
      }
      setIsOpen(false);
    } catch (err) {
      alert("Failed to save agent config. Check field schemas.");
    }
  };

  const handleClearMemory = async (agentId: string) => {
    if (confirm("Are you sure you want to clear this agent's SQL memory database? This resets their context state.")) {
      await clearAgentMemory(agentId);
      if (memoryAgent && memoryAgent.id === agentId) {
        setMemoryItems([]);
      }
    }
  };

  const handleViewMemory = async (agent: Agent) => {
    if (!agent.id) return;
    try {
      const items = await api.getAgentMemory(agent.id);
      setMemoryAgent(agent);
      setMemoryItems(items);
    } catch {
      alert("Error loading agent memory logs.");
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-3xl font-extrabold tracking-tight text-white font-sans">
            AI Agent Registry
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Build and register reusable agent nodes, inject custom prompts, toggle skills/tools, and configure communication endpoints.
          </p>
        </div>
        <button
          onClick={openNewForm}
          className="flex items-center gap-1.5 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-all duration-300 shadow-lg shadow-indigo-600/20"
        >
          <Plus className="w-4.5 h-4.5" />
          Create Agent
        </button>
      </div>

      {/* Grid List */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {agents.map((agent) => {
          let tools: string[] = [];
          try {
            tools = JSON.parse(agent.tools_json);
          } catch {}

          return (
            <div key={agent.id} className="glass rounded-2xl p-6 border border-slate-800 flex flex-col justify-between hover:border-slate-700 transition-all duration-300 relative glow-indigo">
              <div>
                {/* Title */}
                <div className="flex items-start justify-between">
                  <div className="flex gap-3">
                    <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center border border-indigo-500/20">
                      <Bot className="w-5.5 h-5.5" />
                    </div>
                    <div>
                      <h3 className="font-bold text-base text-white">{agent.name}</h3>
                      <p className="text-xs text-indigo-400 font-semibold">{agent.role || 'Generalist'}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-1.5">
                    <button
                      onClick={() => openEditForm(agent)}
                      className="p-1.5 hover:bg-slate-900 rounded-lg text-slate-400 hover:text-white transition-colors"
                      title="Edit Agent Config"
                    >
                      <Edit3 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => agent.id && deleteAgent(agent.id)}
                      className="p-1.5 hover:bg-slate-900 rounded-lg text-slate-400 hover:text-rose-400 transition-colors"
                      title="Delete Agent"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Description */}
                <p className="text-xs text-slate-400 mt-4 leading-relaxed line-clamp-3">
                  {agent.description || 'No description provided.'}
                </p>

                {/* Stats */}
                <div className="mt-4 pt-4 border-t border-slate-900/60 grid grid-cols-2 gap-2 text-xs text-slate-400">
                  <div>
                    <span className="text-[10px] text-slate-500 block uppercase font-bold">Model</span>
                    <span className="text-slate-300 font-mono text-[11px] truncate block">{agent.model}</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-500 block uppercase font-bold">Channel</span>
                    <span className="text-slate-300 font-medium block">{agent.channel || 'None'}</span>
                  </div>
                </div>

                {/* Skills/Tools */}
                <div className="mt-4">
                  <span className="text-[10px] text-slate-500 block uppercase font-bold mb-1.5">Enabled Skills</span>
                  <div className="flex flex-wrap gap-1.5">
                    {tools.length === 0 ? (
                      <span className="text-[10px] text-slate-600 italic">None enabled</span>
                    ) : (
                      tools.map((t) => (
                        <span key={t} className="px-2 py-0.5 bg-slate-900 border border-slate-800 text-slate-300 rounded text-[10px] font-mono">
                          {t}
                        </span>
                      ))
                    )}
                  </div>
                </div>
              </div>

              {/* Memory panel trigger */}
              <div className="mt-6 pt-4 border-t border-slate-900/60 flex items-center justify-between">
                <button
                  onClick={() => handleViewMemory(agent)}
                  className="flex items-center gap-1 text-[11px] font-bold text-indigo-400 hover:text-indigo-300 transition-colors"
                >
                  <BrainCircuit className="w-3.5 h-3.5" />
                  View Memory State
                </button>
                
                {agent.memory_enabled && (
                  <button
                    onClick={() => agent.id && handleClearMemory(agent.id)}
                    className="text-[10px] font-semibold text-slate-500 hover:text-rose-400 transition-colors"
                  >
                    Clear Memory
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Memory Viewer Modal */}
      {memoryAgent && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="glass max-w-2xl w-full rounded-2xl border border-slate-800 p-6 flex flex-col max-h-[80vh] glow-purple">
            <div className="flex items-center justify-between border-b border-slate-900 pb-3 mb-4">
              <h3 className="font-extrabold text-lg text-white flex items-center gap-2">
                <BrainCircuit className="w-5.5 h-5.5 text-indigo-400" />
                Memory state: {memoryAgent.name}
              </h3>
              <button 
                onClick={() => setMemoryAgent(null)}
                className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-900"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto space-y-4">
              {memoryItems.length === 0 ? (
                <p className="text-sm text-slate-500 italic text-center py-8">
                  Agent has no messages recorded in its SQL database checkpointer.
                </p>
              ) : (
                memoryItems.map((item, idx) => (
                  <div key={idx} className="p-3 bg-slate-900/50 border border-slate-800/80 rounded-xl space-y-2">
                    <div className="flex justify-between items-center text-[10px]">
                      <span className="font-bold text-indigo-400 uppercase tracking-wider">
                        Key: {item.key}
                      </span>
                      <span className="text-slate-500">
                        {new Date(item.updated_at).toLocaleString()}
                      </span>
                    </div>
                    <pre className="text-xs font-mono text-slate-300 whitespace-pre-wrap overflow-x-auto bg-slate-950 p-2.5 rounded-lg border border-slate-900">
                      {JSON.stringify(item.value, null, 2)}
                    </pre>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      )}

      {/* Slide-over Slider Form Panel */}
      {isOpen && (
        <div className="fixed inset-0 z-40 overflow-hidden">
          <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-xs transition-opacity" onClick={() => setIsOpen(false)} />
          
          <div className="absolute inset-y-0 right-0 max-w-full flex pl-10">
            <div className="w-screen max-w-lg glass border-l border-slate-800 flex flex-col h-full overflow-hidden shadow-2xl relative">
              
              {/* Form Header */}
              <div className="p-6 border-b border-slate-900/60 flex items-center justify-between shrink-0">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Bot className="w-5.5 h-5.5 text-indigo-400" />
                  {editingAgent ? 'Edit Agent Configuration' : 'Register New Agent'}
                </h3>
                <button
                  onClick={() => setIsOpen(false)}
                  className="text-slate-400 hover:text-white p-1 hover:bg-slate-900 rounded-lg transition-colors"
                >
                  <X className="w-5.5 h-5.5" />
                </button>
              </div>

              {/* Scrollable Form Body */}
              <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-6">
                
                {/* 1. Name */}
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Agent Name*</label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Researcher"
                    className="w-full bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-xl px-3.5 py-2.5 text-sm outline-none transition-colors"
                  />
                </div>

                {/* 2. Role */}
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Agent Role / Specialty</label>
                  <input
                    type="text"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    placeholder="e.g. Fact Checker, Web Searcher"
                    className="w-full bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-xl px-3.5 py-2.5 text-sm outline-none transition-colors"
                  />
                </div>

                {/* 3. Description */}
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Description</label>
                  <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Describe what this agent specializes in..."
                    rows={2}
                    className="w-full bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-xl px-3.5 py-2.5 text-sm outline-none transition-colors resize-none"
                  />
                </div>

                {/* 4. System Prompt */}
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">System Prompt / Instructions*</label>
                  <textarea
                    required
                    value={systemPrompt}
                    onChange={(e) => setSystemPrompt(e.target.value)}
                    placeholder="You are an AI research analyst. Your goal is to..."
                    rows={6}
                    className="w-full bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-xl px-3.5 py-2.5 text-xs font-mono outline-none transition-colors"
                  />
                </div>

                {/* 5. Model Selector */}
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">LLM Model*</label>
                  <select
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-xl px-3.5 py-2.5 text-sm outline-none transition-colors cursor-pointer"
                  >
                    {AVAILABLE_MODELS.map(m => (
                      <option key={m.id} value={m.id}>{m.name}</option>
                    ))}
                  </select>
                </div>

                {/* 6. Parameters (Temperature, Max Tokens, Max Iterations) */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">
                      Temperature: {temperature}
                    </label>
                    <input
                      type="range"
                      min="0.0"
                      max="1.0"
                      step="0.05"
                      value={temperature}
                      onChange={(e) => setTemperature(parseFloat(e.target.value))}
                      className="w-full h-2 bg-slate-900 rounded-lg appearance-none cursor-pointer accent-indigo-500"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">Max Iterations</label>
                    <input
                      type="number"
                      value={maxIterations}
                      onChange={(e) => setMaxIterations(parseInt(e.target.value))}
                      className="w-full bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-xl px-3.5 py-2 text-sm outline-none"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">Max Tokens Limit</label>
                    <input
                      type="number"
                      value={maxTokens}
                      onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                      className="w-full bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-xl px-3.5 py-2 text-sm outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-semibold text-slate-300 block mb-1">Schedule (Cron)</label>
                    <input
                      type="text"
                      value={scheduleCron}
                      onChange={(e) => setScheduleCron(e.target.value)}
                      placeholder="e.g. */5 * * * * or None"
                      className="w-full bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-xl px-3.5 py-2 text-sm outline-none"
                    />
                  </div>
                </div>

                {/* 7. Memory Toggle */}
                <div className="flex items-center justify-between p-3 bg-slate-900/40 border border-slate-900 rounded-xl">
                  <div>
                    <label className="text-xs font-bold text-white block">Agent SQL Memory</label>
                    <span className="text-[10px] text-slate-500">Persist conversations across workflow executions</span>
                  </div>
                  <input
                    type="checkbox"
                    checked={memoryEnabled}
                    onChange={(e) => setMemoryEnabled(e.target.checked)}
                    className="w-5 h-5 rounded text-indigo-600 bg-slate-900 border-slate-800 focus:ring-0 cursor-pointer accent-indigo-500"
                  />
                </div>

                {/* 8. Channel Dropdown */}
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">Messaging Channel</label>
                  <select
                    value={channel}
                    onChange={(e) => setChannel(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-xl px-3.5 py-2.5 text-sm outline-none transition-colors"
                  >
                    <option value="">None</option>
                    <option value="telegram">Telegram Bot</option>
                  </select>
                </div>

                {/* 9. Tools Checklist */}
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-2">Enabled Tools / Skills</label>
                  <div className="grid grid-cols-2 gap-3">
                    {AVAILABLE_TOOLS.map(tool => (
                      <label key={tool} className="flex items-center gap-2.5 p-2.5 bg-slate-900/40 border border-slate-900 rounded-xl cursor-pointer hover:border-slate-800 transition-colors">
                        <input
                          type="checkbox"
                          checked={enabledTools.includes(tool)}
                          onChange={() => handleToolToggle(tool)}
                          className="w-4.5 h-4.5 accent-indigo-500 cursor-pointer"
                        />
                        <span className="text-xs font-mono text-slate-300">{tool}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* 10. Guardrails / Forbidden Topics */}
                <div>
                  <label className="text-xs font-semibold text-slate-300 block mb-1">
                    Guardrails: Forbidden Topics (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={forbiddenTopics}
                    onChange={(e) => setForbiddenTopics(e.target.value)}
                    placeholder="e.g. pricing, database_credentials, politics"
                    className="w-full bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-xl px-3.5 py-2.5 text-sm outline-none transition-colors"
                  />
                </div>
              </form>

              {/* Form Footer Buttons */}
              <div className="p-6 border-t border-slate-900/60 flex items-center justify-end gap-3 shrink-0">
                <button
                  type="button"
                  onClick={() => setIsOpen(false)}
                  className="px-4 py-2.5 border border-slate-800 hover:bg-slate-900 text-slate-300 rounded-xl text-xs font-bold transition-all duration-300"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmit}
                  className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-all duration-300 shadow-lg shadow-indigo-600/20"
                >
                  {editingAgent ? 'Save Changes' : 'Create Agent'}
                </button>
              </div>

            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Agents;
