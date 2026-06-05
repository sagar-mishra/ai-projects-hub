import React, { useEffect } from 'react';
import { useStore } from '../store/useStore';
import { useNavigate } from 'react-router-dom';
import { 
  Bot, 
  GitBranch, 
  Play, 
  CheckCircle2, 
  XCircle, 
  Clock, 
  Coins, 
  ArrowRight,
  ShieldAlert
} from 'lucide-react';

const Dashboard: React.FC = () => {
  const { 
    agents, 
    workflows, 
    runs, 
    pendingApprovals,
    fetchAgents, 
    fetchWorkflows, 
    fetchRuns,
    fetchPendingApprovals,
    setActiveRunId
  } = useStore();

  const navigate = useNavigate();

  useEffect(() => {
    fetchAgents();
    fetchWorkflows();
    fetchRuns(1, 10);
    fetchPendingApprovals();
  }, []);

  const totalRuns = runs.length;
  const successfulRuns = runs.filter(r => r.status === 'completed').length;
  const failedRuns = runs.filter(r => r.status === 'failed').length;
  const successRate = totalRuns > 0 ? Math.round((successfulRuns / totalRuns) * 100) : 0;
  
  // Estimate total cost
  const totalCost = runs.reduce((acc, r) => acc + (r.cost_usd || 0), 0);

  const handleViewRun = (runId: string) => {
    setActiveRunId(runId);
    navigate('/monitor');
  };

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h2 className="text-3xl font-extrabold tracking-tight text-white font-sans">
          Orchestration Dashboard
        </h2>
        <p className="text-slate-400 text-sm mt-1">
          Monitor your collaborative agent state machines, review execution costs, and decide approval steps.
        </p>
      </div>

      {/* Approvals Banner */}
      {pendingApprovals.length > 0 && (
        <div className="p-4 bg-amber-500/10 border border-amber-500/20 rounded-2xl flex items-center justify-between glow-purple">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/20 flex items-center justify-center text-amber-400">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-white">
                Human-in-the-Loop Action Required
              </h4>
              <p className="text-xs text-slate-400 mt-0.5">
                There are {pendingApprovals.length} workflow run(s) waiting for operator review and input.
              </p>
            </div>
          </div>
          <button 
            onClick={() => navigate('/monitor')}
            className="flex items-center gap-1.5 px-4 py-2 bg-amber-500 hover:bg-amber-600 text-slate-950 rounded-xl text-xs font-bold transition-all duration-300"
          >
            Review Approvals
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Stats row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="glass p-6 rounded-2xl glow-indigo relative overflow-hidden">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider">
              Total Agents
            </span>
            <div className="w-9 h-9 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400">
              <Bot className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">{agents.length}</span>
            <span className="text-xs text-indigo-400 font-medium">configured</span>
          </div>
        </div>

        <div className="glass p-6 rounded-2xl glow-indigo">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider">
              Total Workflows
            </span>
            <div className="w-9 h-9 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400">
              <GitBranch className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">{workflows.length}</span>
            <span className="text-xs text-purple-400 font-medium">graphs loaded</span>
          </div>
        </div>

        <div className="glass p-6 rounded-2xl glow-indigo">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider">
              Today's Success Rate
            </span>
            <div className="w-9 h-9 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-400">
              <CheckCircle2 className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">{successRate}%</span>
            <span className="text-xs text-slate-400 font-medium">
              ({successfulRuns}/{totalRuns} runs)
            </span>
          </div>
        </div>

        <div className="glass p-6 rounded-2xl glow-indigo">
          <div className="flex items-center justify-between">
            <span className="text-slate-400 text-xs font-semibold uppercase tracking-wider">
              Estimated Cost (USD)
            </span>
            <div className="w-9 h-9 rounded-xl bg-cyan-500/10 flex items-center justify-center text-cyan-400">
              <Coins className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-4 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold text-white">
              ${totalCost.toFixed(4)}
            </span>
            <span className="text-xs text-cyan-400 font-medium">Llama-3 usage</span>
          </div>
        </div>
      </div>

      {/* Secondary content split */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Runs Table */}
        <div className="lg:col-span-2 glass rounded-2xl p-6 border border-slate-800">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg font-bold text-white">
              Recent Activity & Runs
            </h3>
            <button 
              onClick={() => navigate('/monitor')} 
              className="text-xs font-bold text-indigo-400 hover:text-indigo-300 transition-colors flex items-center gap-1"
            >
              See Monitor
              <ArrowRight className="w-4.5 h-4.5" />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-900 text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  <th className="py-3 px-4">Run ID</th>
                  <th className="py-3 px-4">Workflow</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Duration/Tokens</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="text-sm divide-y divide-slate-900/60">
                {runs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="text-center py-8 text-slate-500 font-medium">
                      No active execution runs recorded. Start one in the workflow builder!
                    </td>
                  </tr>
                ) : (
                  runs.map((run) => {
                    const wfName = workflows.find(w => w.id === run.workflow_id)?.name || 'Unknown Graph';
                    return (
                      <tr key={run.id} className="hover:bg-slate-900/20 transition-all duration-200">
                        <td className="py-3.5 px-4 font-mono text-xs text-slate-300">
                          {run.id.slice(0, 8)}...
                        </td>
                        <td className="py-3.5 px-4 text-white font-medium">
                          {wfName}
                        </td>
                        <td className="py-3.5 px-4">
                          <span className={`
                            inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold
                            ${run.status === 'completed' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : ''}
                            ${run.status === 'failed' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : ''}
                            ${run.status === 'running' ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 animate-pulse' : ''}
                            ${run.status === 'waiting_approval' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : ''}
                            ${run.status === 'pending' ? 'bg-slate-500/10 text-slate-400 border border-slate-500/20' : ''}
                          `}>
                            {run.status === 'running' && <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 animate-ping"></span>}
                            {run.status}
                          </span>
                        </td>
                        <td className="py-3.5 px-4 text-slate-400 text-xs">
                          <div>Tokens: {run.token_count}</div>
                          <div className="text-[10px] text-slate-500">{new Date(run.started_at).toLocaleTimeString()}</div>
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <button
                            onClick={() => handleViewRun(run.id)}
                            className="px-3 py-1.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-200 text-xs font-semibold rounded-lg transition-colors"
                          >
                            Logs
                          </button>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Quick Launch Cards */}
        <div className="space-y-6">
          <div className="glass p-6 rounded-2xl border border-slate-800 glow-indigo">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Bot className="w-5 h-5 text-indigo-400" />
              Configure Agents
            </h3>
            <p className="text-slate-400 text-xs mt-1.5 leading-relaxed">
              Design custom LLM profiles with custom system prompts, enabled tools, temperature dials, and messaging configurations.
            </p>
            <button 
              onClick={() => navigate('/agents')}
              className="w-full mt-4 py-2.5 bg-slate-900 hover:bg-indigo-900/30 hover:border-indigo-500/30 border border-slate-800 text-slate-200 rounded-xl text-xs font-bold transition-all duration-300 flex items-center justify-center gap-1.5"
            >
              Manage Agents
              <Bot className="w-4 h-4" />
            </button>
          </div>

          <div className="glass p-6 rounded-2xl border border-slate-800 glow-indigo">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <GitBranch className="w-5 h-5 text-purple-400" />
              Workflow Builder
            </h3>
            <p className="text-slate-400 text-xs mt-1.5 leading-relaxed">
              Use a drag-and-drop React Flow canvas to visually assemble multi-agent architectures, routing rules, and verification checks.
            </p>
            <button 
              onClick={() => navigate('/workflows')}
              className="w-full mt-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-all duration-300 flex items-center justify-center gap-1.5 shadow-md shadow-indigo-600/20"
            >
              Open Builder
              <Play className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
