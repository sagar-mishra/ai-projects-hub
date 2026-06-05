import React, { useEffect, useState, useRef } from 'react';
import { useStore } from '../store/useStore';
import { WS_URL, api, LogEntry } from '../api/client';
import { 
  Activity, 
  Bot, 
  User, 
  Terminal, 
  Clock, 
  Coins, 
  AlertOctagon, 
  ShieldAlert, 
  ThumbsUp, 
  ThumbsDown,
  Sparkles
} from 'lucide-react';

const Monitor: React.FC = () => {
  const { 
    runs, 
    activeRunId, 
    activeRun, 
    runLogs, 
    runMessages,
    fetchRuns, 
    setActiveRunId, 
    decideApproval,
    addLiveLog 
  } = useStore();

  const [statusFilter, setStatusFilter] = useState('');
  const wsRef = useRef<WebSocket | null>(null);
  const logEndRef = useRef<HTMLDivElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto-fetch runs list
  useEffect(() => {
    fetchRuns(1, 20, statusFilter);
    const interval = setInterval(() => {
      fetchRuns(1, 20, statusFilter);
    }, 5000); // Poll list updates every 5s
    return () => clearInterval(interval);
  }, [statusFilter]);

  // Handle WebSocket Live Connection
  useEffect(() => {
    if (!activeRunId) return;

    // Load initial run details
    setActiveRunId(activeRunId);

    // Initialize WebSocket
    const ws = new WebSocket(`${WS_URL}/api/ws/logs/${activeRunId}`);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const logData: LogEntry = JSON.parse(event.data);
        addLiveLog(logData);
        
        // Auto-scroll lists
        setTimeout(() => {
          logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
          chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
        }, 100);
      } catch (e) {
        console.error("Error parsing WS message:", e);
      }
    };

    ws.onclose = () => {
      console.log(`WS connection closed for run: ${activeRunId}`);
    };

    return () => {
      ws.close();
      wsRef.current = null;
    };
  }, [activeRunId]);

  // Scroll to bottom on log/message updates
  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [runLogs, runMessages]);

  const handleSelectRun = (runId: string) => {
    setActiveRunId(runId);
  };

  // Find active run's pending approval
  const activeApproval = runLogs.find(
    log => log.event_type === 'approval_requested' && log.payload?.approval_id
  );

  const handleApprovalDecision = async (decision: 'approve' | 'reject') => {
    if (!activeApproval || !activeApproval.payload?.approval_id) return;
    const approvalId = activeApproval.payload.approval_id;
    try {
      await decideApproval(approvalId, decision);
      alert(`Decision '${decision.toUpperCase()}' registered.`);
    } catch {
      alert("Failed to submit approval decision.");
    }
  };

  return (
    <div className="h-[calc(100vh-140px)] flex gap-6 overflow-hidden">
      
      {/* 1. Left Run List Pane */}
      <aside className="w-80 glass border border-slate-850 rounded-2xl flex flex-col overflow-hidden shrink-0">
        <div className="p-4 border-b border-slate-900/60 space-y-3 shrink-0">
          <h3 className="font-bold text-xs text-white uppercase tracking-wider">
            Execution Runs
          </h3>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-xl px-2.5 py-1.5 text-xs outline-none cursor-pointer"
          >
            <option value="">All Statuses</option>
            <option value="running">Running</option>
            <option value="waiting_approval">Waiting Approval</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
        </div>

        <div className="flex-1 overflow-y-auto divide-y divide-slate-900/40 p-2 space-y-1">
          {runs.map((run) => (
            <div
              key={run.id}
              onClick={() => handleSelectRun(run.id)}
              className={`
                p-3 rounded-xl cursor-pointer transition-all duration-200 border text-left
                ${activeRunId === run.id 
                  ? 'bg-indigo-600/10 border-indigo-500/30' 
                  : 'bg-transparent border-transparent hover:bg-slate-900/35'
                }
              `}
            >
              <div className="flex justify-between items-start">
                <span className="font-mono text-[10px] text-slate-400">
                  {run.id.slice(0, 8)}...
                </span>
                <span className={`
                  inline-flex items-center px-2 py-0.2 rounded-full text-[9px] font-bold uppercase
                  ${run.status === 'completed' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : ''}
                  ${run.status === 'failed' ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : ''}
                  ${run.status === 'running' ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 animate-pulse' : ''}
                  ${run.status === 'waiting_approval' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' : ''}
                  ${run.status === 'pending' ? 'bg-slate-500/10 text-slate-400 border border-slate-500/20' : ''}
                `}>
                  {run.status}
                </span>
              </div>
              <div className="text-xs text-white font-semibold mt-1.5 truncate">
                Run ID: {run.id.slice(0, 8)}
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">
                {new Date(run.started_at).toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      </aside>

      {/* Main Console and Timeline splits */}
      {activeRun ? (
        <div className="flex-1 flex gap-6 overflow-hidden">
          
          {/* 2. Center Console Logs Pane */}
          <div className="flex-1 glass border border-slate-850 rounded-2xl flex flex-col overflow-hidden">
            {/* Approval Banner */}
            {activeRun.status === 'waiting_approval' && activeApproval && (
              <div className="p-4 bg-amber-500/15 border-b border-amber-500/20 flex items-center justify-between shrink-0 glow-purple">
                <div className="flex items-center gap-2.5">
                  <ShieldAlert className="w-5 h-5 text-amber-400" />
                  <div>
                    <h4 className="text-xs font-bold text-white uppercase tracking-wide">Approval Action Pending</h4>
                    <p className="text-[10px] text-slate-400 mt-0.5">{activeApproval.payload.question}</p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleApprovalDecision('reject')}
                    className="flex items-center gap-1 px-3 py-1.5 bg-rose-500/20 hover:bg-rose-500/40 border border-rose-500/20 text-rose-300 text-[10px] font-bold rounded-lg transition-colors"
                  >
                    <ThumbsDown className="w-3.5 h-3.5" />
                    Reject
                  </button>
                  <button
                    onClick={() => handleApprovalDecision('approve')}
                    className="flex items-center gap-1 px-3 py-1.5 bg-emerald-500 hover:bg-emerald-600 text-slate-950 text-[10px] font-bold rounded-lg transition-colors"
                  >
                    <ThumbsUp className="w-3.5 h-3.5" />
                    Approve
                  </button>
                </div>
              </div>
            )}

            {/* Logs Console */}
            <div className="flex-1 p-4 overflow-y-auto space-y-2.5 bg-slate-950/40 font-mono text-[11px] leading-relaxed">
              <div className="text-slate-500 border-b border-slate-900 pb-2 mb-3">
                // SYSTEM LOG STREAM INITIALIZED -- RUN ID: {activeRunId}
              </div>

              {runLogs.map((log) => {
                let colorClass = 'text-slate-300';
                let tag = 'INFO';
                
                if (log.event_type === 'llm_call') {
                  colorClass = 'text-sky-400';
                  tag = 'LLM';
                } else if (log.event_type === 'tool_call') {
                  colorClass = 'text-violet-400';
                  tag = 'TOOL-CALL';
                } else if (log.event_type === 'tool_result') {
                  colorClass = 'text-emerald-400';
                  tag = 'TOOL-RESP';
                } else if (log.event_type === 'agent_message') {
                  colorClass = 'text-yellow-400';
                  tag = 'AGENT';
                } else if (log.event_type === 'approval_requested') {
                  colorClass = 'text-amber-400';
                  tag = 'APPROVAL';
                } else if (log.event_type === 'error') {
                  colorClass = 'text-rose-400';
                  tag = 'ERROR';
                }

                // Parse message string from payload or format nicely
                const logMessage = log.payload?.message || log.payload?.content || log.payload?.error || 'Log event triggered.';

                return (
                  <div key={log.id} className="flex gap-2 items-start hover:bg-slate-900/10 py-0.5 rounded transition-all">
                    <span className="text-slate-600 select-none">
                      [{new Date(log.timestamp).toLocaleTimeString()}]
                    </span>
                    <span className={`font-bold shrink-0 text-[10px] px-1.5 rounded bg-slate-900 border border-slate-800 ${colorClass}`}>
                      {tag}
                    </span>
                    <span className={colorClass}>
                      {logMessage}
                    </span>
                  </div>
                );
              })}
              <div ref={logEndRef} />
            </div>

            {/* Cost and metrics footer */}
            <div className="p-4 border-t border-slate-900 bg-slate-950/60 flex items-center justify-between text-xs text-slate-400 shrink-0">
              <div className="flex gap-4">
                <span className="flex items-center gap-1 font-mono">
                  <Terminal className="w-4 h-4 text-slate-500" />
                  Tokens: <span className="text-white font-bold">{activeRun.token_count}</span>
                </span>
                <span className="flex items-center gap-1 font-mono">
                  <Coins className="w-4 h-4 text-slate-500" />
                  Cost: <span className="text-cyan-400 font-bold">${(activeRun.cost_usd || 0).toFixed(6)}</span>
                </span>
              </div>
              <div className="flex items-center gap-1.5 text-slate-500">
                <Clock className="w-3.5 h-3.5" />
                <span>Started {new Date(activeRun.started_at).toLocaleTimeString()}</span>
              </div>
            </div>

          </div>

          {/* 3. Right Messages Timeline Chat Pane */}
          <div className="w-96 glass border border-slate-850 rounded-2xl flex flex-col overflow-hidden shrink-0">
            <div className="p-4 border-b border-slate-900/60 shrink-0">
              <h3 className="font-bold text-xs text-white uppercase tracking-wider">
                Inter-Agent Message Timeline
              </h3>
            </div>

            <div className="flex-1 p-4 overflow-y-auto space-y-4 bg-slate-950/20">
              {runMessages.length === 0 ? (
                <div className="text-center py-12 text-slate-500 text-xs italic">
                  No conversational exchange messages captured yet.
                </div>
              ) : (
                runMessages.map((msg) => {
                  const isHuman = msg.sender_agent === 'human' || msg.sender_agent === 'telegram';
                  return (
                    <div key={msg.id} className={`flex flex-col ${isHuman ? 'items-end' : 'items-start'}`}>
                      <div className="flex items-center gap-1.5 mb-1">
                        {isHuman ? (
                          <>
                            <span className="text-[10px] text-slate-400 font-semibold uppercase">{msg.sender_agent}</span>
                            <User className="w-3.5 h-3.5 text-indigo-400" />
                          </>
                        ) : (
                          <>
                            <Bot className="w-3.5 h-3.5 text-yellow-400" />
                            <span className="text-[10px] text-slate-400 font-semibold uppercase">{msg.sender_agent}</span>
                          </>
                        )}
                      </div>
                      
                      <div className={`
                        max-w-[85%] rounded-2xl px-3.5 py-2.5 text-xs leading-relaxed
                        ${isHuman 
                          ? 'bg-indigo-600/10 text-indigo-200 border border-indigo-500/20 rounded-tr-none' 
                          : 'bg-slate-900 text-slate-200 border border-slate-850 rounded-tl-none glow-indigo'
                        }
                      `}>
                        {msg.content}
                      </div>
                    </div>
                  );
                })
              )}
              <div ref={chatEndRef} />
            </div>
          </div>

        </div>
      ) : (
        <div className="flex-1 glass border border-slate-850 rounded-2xl flex flex-col items-center justify-center p-8 text-center text-slate-500">
          <Activity className="w-12 h-12 text-indigo-500/50 mb-3 animate-pulse" />
          <h4 className="font-bold text-white text-base">No active run selected</h4>
          <p className="text-xs text-slate-400 max-w-sm mt-1">
            Choose an execution run from the history dashboard, message bot in Telegram, or start one visually in the workflow canvas.
          </p>
        </div>
      )}

    </div>
  );
};

export default Monitor;
