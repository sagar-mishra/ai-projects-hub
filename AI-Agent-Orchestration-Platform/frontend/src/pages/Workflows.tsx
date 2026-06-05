import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useStore } from '../store/useStore';
import { useNavigate } from 'react-router-dom';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
  Handle,
  Position,
  MarkerType
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { 
  Play, 
  Save, 
  GitBranch, 
  Layers, 
  Bot, 
  Activity, 
  HelpCircle, 
  ShieldCheck, 
  FileCode,
  Sparkles,
  X,
  Square
} from 'lucide-react';

// Custom Node Components
const TriggerNode = ({ data }: any) => (
  <div className="px-4 py-2.5 rounded-xl border border-emerald-500 bg-emerald-950/30 text-emerald-300 font-semibold text-xs flex items-center gap-2 shadow-lg shadow-emerald-950/15">
    <div className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></div>
    {data.label || 'Trigger'}
    <Handle type="source" position={Position.Bottom} className="!bg-emerald-500" />
  </div>
);

const EndNode = ({ data }: any) => (
  <div className="px-4 py-2.5 rounded-xl border border-rose-500 bg-rose-950/30 text-rose-300 font-semibold text-xs flex items-center gap-2 shadow-lg shadow-rose-950/15">
    <div className="w-2.5 h-2.5 rounded bg-rose-500"></div>
    {data.label || 'End'}
    <Handle type="target" position={Position.Top} className="!bg-rose-500" />
  </div>
);

const AgentNode = ({ data }: any) => (
  <div className="px-4 py-3 rounded-xl border border-indigo-500 bg-slate-900 text-slate-100 min-w-[140px] shadow-lg shadow-indigo-950/20 relative glow-indigo">
    <Handle type="target" position={Position.Top} className="!bg-indigo-500" />
    <div className="flex items-center gap-2">
      <Bot className="w-4 h-4 text-indigo-400 shrink-0" />
      <div>
        <div className="text-[10px] text-indigo-400 font-bold uppercase tracking-wider">Agent Node</div>
        <div className="text-xs font-semibold">{data.agentName || 'Select Agent...'}</div>
      </div>
    </div>
    <Handle type="source" position={Position.Bottom} className="!bg-indigo-500" />
  </div>
);

const ConditionNode = ({ data }: any) => (
  <div className="px-4 py-3 rounded-xl border border-purple-500 bg-slate-900 text-slate-100 min-w-[140px] shadow-lg shadow-purple-950/20 relative">
    <Handle type="target" position={Position.Top} className="!bg-purple-500" />
    <div className="flex items-center gap-2">
      <GitBranch className="w-4 h-4 text-purple-400 shrink-0" />
      <div>
        <div className="text-[10px] text-purple-400 font-bold uppercase tracking-wider">Condition Router</div>
        <div className="text-xs font-semibold">{data.condition || 'Custom Check'}</div>
      </div>
    </div>
    <Handle type="source" position={Position.Bottom} className="!bg-purple-500" />
  </div>
);

const ApprovalNode = ({ data }: any) => (
  <div className="px-4 py-3 rounded-xl border border-amber-500 bg-slate-900 text-slate-100 min-w-[140px] shadow-lg shadow-amber-950/20 relative">
    <Handle type="target" position={Position.Top} className="!bg-amber-500" />
    <div className="flex items-center gap-2">
      <ShieldCheck className="w-4 h-4 text-amber-400 shrink-0" />
      <div>
        <div className="text-[10px] text-amber-400 font-bold uppercase tracking-wider">Approval Step</div>
        <div className="text-xs font-semibold truncate max-w-[120px]">{data.question || 'Approve?'}</div>
      </div>
    </div>
    <Handle type="source" position={Position.Bottom} className="!bg-amber-500" />
  </div>
);

const nodeTypes = {
  trigger: TriggerNode,
  end: EndNode,
  agent: AgentNode,
  condition: ConditionNode,
  approval: ApprovalNode
};

const Workflows: React.FC = () => {
  const { 
    workflows, 
    agents, 
    fetchWorkflows, 
    fetchAgents, 
    createWorkflow, 
    updateWorkflow, 
    deleteWorkflow,
    runWorkflow
  } = useStore();

  const navigate = useNavigate();
  const reactFlowWrapper = useRef<HTMLDivElement>(null);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  
  const [activeWorkflow, setActiveWorkflow] = useState<any | null>(null);
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);

  // Workflow meta form
  const [wfName, setWfName] = useState('');
  const [wfDesc, setWfDesc] = useState('');

  // Selected Node Settings
  const [nodeAgentId, setNodeAgentId] = useState('');
  const [nodeCondition, setNodeCondition] = useState('');
  const [nodeQuestion, setNodeQuestion] = useState('');

  // Edge editing
  const [selectedEdge, setSelectedEdge] = useState<Edge | null>(null);
  const [edgeWhen, setEdgeWhen] = useState('');

  useEffect(() => {
    fetchWorkflows();
    fetchAgents();
  }, []);

  const loadWorkflowIntoCanvas = (wf: any) => {
    setActiveWorkflow(wf);
    setWfName(wf.name);
    setWfDesc(wf.description || '');
    setSelectedNode(null);
    setSelectedEdge(null);

    try {
      const graph = JSON.parse(wf.graph_json);
      
      // Inject details to nodes
      const enrichedNodes = graph.nodes.map((node: any, idx: number) => {
        const defaultPositions: Record<string, { x: number; y: number }> = {
          trigger: { x: 250, y: 50 },
          end: { x: 250, y: 500 },
          agent: { x: 250, y: 150 + idx * 100 },
          condition: { x: 250, y: 250 },
          approval: { x: 250, y: 350 }
        };
        const position = node.position || defaultPositions[node.type] || { x: 250, y: 200 + idx * 50 };
        const data = node.data || {};
        const agent_id = node.agent_id || data.agent_id;
        const question = node.question || data.question;
        const condition = node.condition || data.condition;
        
        const enrichedNode: any = {
          ...node,
          position,
          agent_id,
          question,
          condition,
          data: {
            ...data,
            agent_id,
            question,
            condition,
            label: data.label || (node.type === 'agent' ? 'Agent Node' : node.id)
          }
        };

        if (node.type === 'agent' && agent_id) {
          const agent = agents.find(a => a.id === agent_id);
          enrichedNode.data.agentName = agent?.name || 'Unknown Agent';
        }
        return enrichedNode;
      });

      setNodes(enrichedNodes);
      
      // Enrich edges with labels
      const enrichedEdges = graph.edges.map((edge: any) => {
        if (edge.when) {
          return {
            ...edge,
            label: edge.when,
            labelStyle: { fill: '#a5b4fc', fontWeight: 600, fontSize: '10px' },
            labelBgPadding: [6, 4],
            labelBgRadius: 4,
            labelBgStyle: { fill: '#1e293b', fillOpacity: 0.8 },
            markerEnd: { type: MarkerType.ArrowClosed, color: '#475569' }
          };
        }
        return {
          ...edge,
          markerEnd: { type: MarkerType.ArrowClosed, color: '#475569' }
        };
      });

      setEdges(enrichedEdges);
    } catch {
      // Clear canvas if empty/corrupted
      setNodes([]);
      setEdges([]);
    }
  };

  const createNewWorkflow = () => {
    setActiveWorkflow(null);
    setWfName('New Workflow Graph');
    setWfDesc('');
    
    // Default standard starter nodes
    const initialNodes: Node[] = [
      { id: 'trigger-1', type: 'trigger', position: { x: 250, y: 50 }, data: { label: 'Trigger: Input Message' } },
      { id: 'end-1', type: 'end', position: { x: 250, y: 400 }, data: { label: 'End Pipeline' } }
    ];
    setNodes(initialNodes);
    setEdges([]);
    setSelectedNode(null);
  };

  // Node Drag and Drop Drop Handler
  const onDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent) => {
      event.preventDefault();

      if (!reactFlowWrapper.current) return;
      const reactFlowBounds = reactFlowWrapper.current.getBoundingClientRect();
      const type = event.dataTransfer.getData('application/reactflow');

      // check if the dropped element is valid
      if (typeof type === 'undefined' || !type) {
        return;
      }

      // Calculate position
      const clientX = event.clientX;
      const clientY = event.clientY;
      const position = {
        x: clientX - reactFlowBounds.left - 75,
        y: clientY - reactFlowBounds.top - 20
      };

      const nodeId = `${type}-${Date.now()}`;
      
      let label = '';
      if (type === 'trigger') label = 'Trigger: Input Message';
      if (type === 'end') label = 'End Pipeline';
      if (type === 'agent') label = 'Agent Node';
      if (type === 'condition') label = 'Condition Node';
      if (type === 'approval') label = 'Approval Node';

      const newNode: Node = {
        id: nodeId,
        type,
        position,
        data: { label, agent_id: '', agentName: '', condition: 'output_contains_error', question: 'Approve answer?' }
      };

      setNodes((nds) => nds.concat(newNode));
    },
    [setNodes]
  );

  const onDragStart = (event: React.DragEvent, nodeType: string) => {
    event.dataTransfer.setData('application/reactflow', nodeType);
    event.dataTransfer.effectAllowed = 'move';
  };

  const onConnect = useCallback(
    (params: Connection) => {
      const newEdge: Edge = {
        ...params,
        id: `e-${params.source}-${params.target}`,
        markerEnd: { type: MarkerType.ArrowClosed, color: '#475569' }
      };
      setEdges((eds) => addEdge(newEdge, eds));
    },
    [setEdges]
  );

  // Handle selected Node changes
  const onNodeClick = (_: any, node: Node) => {
    setSelectedNode(node);
    setSelectedEdge(null);
    if (node.type === 'agent') {
      setNodeAgentId(node.data.agent_id as string || '');
    } else if (node.type === 'condition') {
      setNodeCondition(node.data.condition as string || 'output_contains_error');
    } else if (node.type === 'approval') {
      setNodeQuestion(node.data.question as string || 'Approve answer?');
    }
  };

  const onEdgeClick = (_: any, edge: Edge) => {
    setSelectedEdge(edge);
    setSelectedNode(null);
    setEdgeWhen(edge.label as string || '');
  };

  const handleUpdateNodeSettings = () => {
    if (!selectedNode) return;
    
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === selectedNode.id) {
          const updatedData = { ...node.data };
          if (node.type === 'agent') {
            const agent = agents.find(a => a.id === nodeAgentId);
            updatedData.agent_id = nodeAgentId;
            updatedData.agentName = agent?.name || 'Unknown Agent';
          } else if (node.type === 'condition') {
            updatedData.condition = nodeCondition;
          } else if (node.type === 'approval') {
            updatedData.question = nodeQuestion;
          }
          return { ...node, data: updatedData };
        }
        return node;
      })
    );
    setSelectedNode(null);
  };

  const handleUpdateEdgeSettings = () => {
    if (!selectedEdge) return;
    
    setEdges((eds) =>
      eds.map((edge) => {
        if (edge.id === selectedEdge.id) {
          return {
            ...edge,
            label: edgeWhen || undefined,
            labelStyle: { fill: '#a5b4fc', fontWeight: 600, fontSize: '10px' },
            labelBgPadding: [6, 4],
            labelBgRadius: 4,
            labelBgStyle: { fill: '#1e293b', fillOpacity: 0.8 },
          };
        }
        return edge;
      })
    );
    setSelectedEdge(null);
  };

  const handleDeleteSelectedNode = () => {
    if (!selectedNode) return;
    setNodes((nds) => nds.filter((node) => node.id !== selectedNode.id));
    setEdges((eds) => eds.filter((edge) => edge.source !== selectedNode.id && edge.target !== selectedNode.id));
    setSelectedNode(null);
  };

  const handleDeleteSelectedEdge = () => {
    if (!selectedEdge) return;
    setEdges((eds) => eds.filter((edge) => edge.id !== selectedEdge.id));
    setSelectedEdge(null);
  };

  const handleSaveWorkflow = async () => {
    if (!wfName || !wfName.trim()) {
      alert("Workflow name is required.");
      return;
    }

    const invalidAgentNode = nodes.find(n => n.type === 'agent' && !(n.data.agent_id || n.agent_id));
    if (invalidAgentNode) {
      alert(`Error: Agent Node (ID: ${invalidAgentNode.id}) is not configured. Please select an AI agent in the settings panel and try again.`);
      return;
    }

    const cleanNodes = nodes.map(n => ({
      id: n.id,
      type: n.type,
      position: n.position,
      agent_id: n.data.agent_id || n.agent_id,
      condition: n.data.condition || n.condition,
      question: n.data.question || n.question,
      data: {
        agent_id: n.data.agent_id || n.agent_id,
        condition: n.data.condition || n.condition,
        question: n.data.question || n.question,
        label: n.data.label || n.id,
        agentName: n.data.agentName
      }
    }));

    const cleanEdges = edges.map(e => ({
      id: e.id,
      from: e.source,
      to: e.target,
      when: e.label || null
    }));

    const graphJson = JSON.stringify({
      nodes: cleanNodes,
      edges: cleanEdges
    });

    const wfData = {
      name: wfName,
      description: wfDesc,
      graph_json: graphJson
    };

    try {
      if (activeWorkflow && activeWorkflow.id) {
        const updated = await updateWorkflow(activeWorkflow.id, wfData);
        alert("Workflow saved successfully.");
      } else {
        const created = await createWorkflow(wfData);
        setActiveWorkflow(created);
        alert("Workflow created and saved successfully.");
      }
    } catch {
      alert("Failed to save workflow graph schema.");
    }
  };

  const handleTriggerRun = async () => {
    if (!activeWorkflow || !activeWorkflow.id) {
      alert("Please save the workflow graph before running.");
      return;
    }
    
    const message = prompt("Enter input message to trigger workflow run:", "Hello!");
    if (message === null) return;

    try {
      const runId = await runWorkflow(activeWorkflow.id, message);
      setActiveWorkflow(activeWorkflow); // refresh state
      navigate('/monitor');
    } catch {
      alert("Failed to start run.");
    }
  };

  return (
    <div className="h-[calc(100vh-140px)] flex flex-col gap-6">
      
      {/* Top Header Controls bar */}
      <div className="flex justify-between items-center shrink-0">
        <div className="flex gap-4 items-center">
          <div>
            <h2 className="text-3xl font-extrabold tracking-tight text-white font-sans">
              Workflow Canvas
            </h2>
            <p className="text-slate-400 text-sm mt-0.5">
              Graph visualizer to build multi-agent loops and HIL nodes.
            </p>
          </div>
          
          {/* Workflow selectors */}
          <div className="flex items-center gap-2">
            <select
              value={activeWorkflow?.id || ''}
              onChange={(e) => {
                const id = e.target.value;
                if (id) {
                  const wf = workflows.find(w => w.id === id);
                  if (wf) loadWorkflowIntoCanvas(wf);
                } else {
                  createNewWorkflow();
                }
              }}
              className="bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-xl px-3 py-2 text-xs outline-none cursor-pointer"
            >
              <option value="">-- Start New Canvas --</option>
              {workflows.filter(w => !w.is_template).map((w) => (
                <option key={w.id} value={w.id}>{w.name}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={createNewWorkflow}
            className="px-4 py-2 border border-slate-850 hover:bg-slate-900 text-slate-300 rounded-xl text-xs font-bold transition-all duration-300"
          >
            Clear Canvas
          </button>
          
          <button
            onClick={handleSaveWorkflow}
            className="flex items-center gap-1 px-4 py-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-200 rounded-xl text-xs font-bold transition-all duration-300"
          >
            <Save className="w-4 h-4" />
            Save Graph
          </button>

          {activeWorkflow && (
            <button
              onClick={handleTriggerRun}
              className="flex items-center gap-1.5 px-4 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-all duration-300 shadow-lg shadow-indigo-600/20"
            >
              <Play className="w-3.5 h-3.5" />
              Trigger Execution
            </button>
          )}
        </div>
      </div>

      {/* Main visual work area splits */}
      <div className="flex-1 flex gap-6 overflow-hidden min-h-0">
        
        {/* Left Side Node Palette */}
        <aside className="w-52 glass border border-slate-850 p-4 rounded-2xl flex flex-col gap-4 shrink-0">
          <div>
            <h3 className="font-bold text-xs text-white uppercase tracking-wider mb-1">
              Nodes Palette
            </h3>
            <p className="text-[10px] text-slate-500 leading-normal">
              Drag elements onto the builder canvas to wire custom paths.
            </p>
          </div>

          <div className="space-y-2.5">
            <div
              draggable
              onDragStart={(e) => onDragStart(e, 'trigger')}
              className="p-3 border border-emerald-500/30 hover:border-emerald-500/50 bg-emerald-950/15 rounded-xl cursor-grab text-xs font-semibold text-emerald-300 flex items-center gap-2.5 select-none"
            >
              <Play className="w-4 h-4 text-emerald-400" />
              Trigger Node
            </div>

            <div
              draggable
              onDragStart={(e) => onDragStart(e, 'agent')}
              className="p-3 border border-indigo-500/30 hover:border-indigo-500/50 bg-indigo-950/15 rounded-xl cursor-grab text-xs font-semibold text-indigo-300 flex items-center gap-2.5 select-none"
            >
              <Bot className="w-4 h-4 text-indigo-400" />
              Agent Node
            </div>
            
            <div
              draggable
              onDragStart={(e) => onDragStart(e, 'condition')}
              className="p-3 border border-purple-500/30 hover:border-purple-500/50 bg-purple-950/15 rounded-xl cursor-grab text-xs font-semibold text-purple-300 flex items-center gap-2.5 select-none"
            >
              <GitBranch className="w-4 h-4 text-purple-400" />
              Condition Node
            </div>

            <div
              draggable
              onDragStart={(e) => onDragStart(e, 'approval')}
              className="p-3 border border-amber-500/30 hover:border-amber-500/50 bg-amber-950/15 rounded-xl cursor-grab text-xs font-semibold text-amber-300 flex items-center gap-2.5 select-none"
            >
              <ShieldCheck className="w-4 h-4 text-amber-400" />
              Approval Node
            </div>

            <div
              draggable
              onDragStart={(e) => onDragStart(e, 'end')}
              className="p-3 border border-rose-500/30 hover:border-rose-500/50 bg-rose-950/15 rounded-xl cursor-grab text-xs font-semibold text-rose-300 flex items-center gap-2.5 select-none"
            >
              <Square className="w-4 h-4 text-rose-400" />
              End Node
            </div>
          </div>
        </aside>

        {/* Center Canvas */}
        <div ref={reactFlowWrapper} className="flex-1 glass border border-slate-850 rounded-2xl overflow-hidden relative">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            onDragOver={onDragOver}
            onDrop={onDrop}
            nodeTypes={nodeTypes}
            onNodeClick={onNodeClick}
            onEdgeClick={onEdgeClick}
            fitView
          >
            <Controls position="top-right" />
            <MiniMap 
              nodeColor={(n) => {
                if (n.type === 'trigger') return '#10b981';
                if (n.type === 'end') return '#f43f5e';
                if (n.type === 'agent') return '#6366f1';
                if (n.type === 'condition') return '#a855f7';
                return '#f59e0b';
              }} 
              maskColor="rgba(2, 6, 23, 0.7)" 
              style={{ backgroundColor: '#0f172a', border: '1px solid #1e293b' }}
            />
            <Background color="#334155" gap={16} />
          </ReactFlow>
        </div>

        {/* Right Settings Panel */}
        <aside className="w-72 glass border border-slate-850 rounded-2xl shrink-0 overflow-y-auto">
          {/* Graph Meta Config */}
          <div className="p-4 border-b border-slate-900/60 space-y-3">
            <h3 className="font-bold text-xs text-white uppercase tracking-wider">
              Workflow Settings
            </h3>
            <div>
              <label className="text-[10px] text-slate-500 font-bold block mb-1">Graph Name</label>
              <input
                type="text"
                value={wfName}
                onChange={(e) => setWfName(e.target.value)}
                placeholder="Graph name..."
                className="w-full bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-lg px-2.5 py-1.5 text-xs outline-none"
              />
            </div>
            <div>
              <label className="text-[10px] text-slate-500 font-bold block mb-1">Description</label>
              <textarea
                value={wfDesc}
                onChange={(e) => setWfDesc(e.target.value)}
                placeholder="Describe workflow purpose..."
                rows={2}
                className="w-full bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-lg px-2.5 py-1.5 text-xs outline-none resize-none"
              />
            </div>
          </div>

          {/* Node Config */}
          {selectedNode && (
            <div className="p-4 space-y-4">
              <div className="flex justify-between items-center">
                <h4 className="font-extrabold text-xs text-white uppercase tracking-wider">
                  Node Configuration
                </h4>
                <button onClick={() => setSelectedNode(null)} className="text-slate-500 hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="text-[10px] text-slate-400 bg-slate-900/50 p-2 border border-slate-900 rounded-lg font-mono">
                ID: {selectedNode.id}
              </div>

              {selectedNode.type === 'agent' && (
                <div>
                  <label className="text-[10px] text-slate-500 font-bold block mb-1">Select AI Agent*</label>
                  <select
                    value={nodeAgentId}
                    onChange={(e) => {
                      const val = e.target.value;
                      setNodeAgentId(val);
                      setNodes((nds) =>
                        nds.map((node) => {
                          if (node.id === selectedNode.id) {
                            const agent = agents.find(a => a.id === val);
                            return {
                              ...node,
                              agent_id: val,
                              data: {
                                ...node.data,
                                agent_id: val,
                                agentName: agent?.name || 'Unknown Agent'
                              }
                            };
                          }
                          return node;
                        })
                      );
                    }}
                    className="w-full bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-lg px-2.5 py-2 text-xs outline-none cursor-pointer"
                  >
                    <option value="">-- Choose Agent --</option>
                    {agents.map(a => (
                      <option key={a.id} value={a.id}>{a.name} ({a.role || 'Agent'})</option>
                    ))}
                  </select>
                </div>
              )}

              {selectedNode.type === 'condition' && (
                <div>
                  <label className="text-[10px] text-slate-500 font-bold block mb-1">Condition Expression*</label>
                  <select
                    value={nodeCondition}
                    onChange={(e) => {
                      const val = e.target.value;
                      setNodeCondition(val);
                      setNodes((nds) =>
                        nds.map((node) => {
                          if (node.id === selectedNode.id) {
                            return {
                              ...node,
                              condition: val,
                              data: {
                                ...node.data,
                                condition: val
                              }
                            };
                          }
                          return node;
                        })
                      );
                    }}
                    className="w-full bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-lg px-2.5 py-2 text-xs outline-none cursor-pointer"
                  >
                    <option value="output_contains_error">Output Contains Error</option>
                    <option value="is_faq">Triage FAQ Category</option>
                    <option value="is_complaint">Triage Complaint Category</option>
                    <option value="is_escalate">Triage Escalate Category</option>
                  </select>
                </div>
              )}

              {selectedNode.type === 'approval' && (
                <div>
                  <label className="text-[10px] text-slate-500 font-bold block mb-1">HIL Gate Question*</label>
                  <input
                    type="text"
                    value={nodeQuestion}
                    onChange={(e) => {
                      const val = e.target.value;
                      setNodeQuestion(val);
                      setNodes((nds) =>
                        nds.map((node) => {
                          if (node.id === selectedNode.id) {
                            return {
                              ...node,
                              question: val,
                              data: {
                                ...node.data,
                                question: val
                              }
                            };
                          }
                          return node;
                        })
                      );
                    }}
                    placeholder="e.g. Escalate to operator?"
                    className="w-full bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-lg px-2.5 py-2 text-xs outline-none"
                  />
                </div>
              )}

              <div className="pt-2 border-t border-slate-900/60 flex items-center justify-between gap-2">
                <button
                  onClick={handleDeleteSelectedNode}
                  className="px-2.5 py-1.5 bg-rose-950/20 hover:bg-rose-950/40 border border-rose-500/20 text-rose-400 text-[10px] font-bold rounded-lg transition-colors"
                >
                  Delete Node
                </button>
                <button
                  onClick={handleUpdateNodeSettings}
                  className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-[10px] font-bold rounded-lg transition-colors"
                >
                  Apply Settings
                </button>
              </div>
            </div>
          )}

          {/* Edge Config */}
          {selectedEdge && (
            <div className="p-4 space-y-4">
              <div className="flex justify-between items-center">
                <h4 className="font-extrabold text-xs text-white uppercase tracking-wider">
                  Edge Router Config
                </h4>
                <button onClick={() => setSelectedEdge(null)} className="text-slate-500 hover:text-white">
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div>
                <label className="text-[10px] text-slate-500 font-bold block mb-1">Routing Condition (when)*</label>
                <input
                  type="text"
                  value={edgeWhen}
                  onChange={(e) => {
                    const val = e.target.value;
                    setEdgeWhen(val);
                    setEdges((eds) =>
                      eds.map((edge) => {
                        if (edge.id === selectedEdge.id) {
                          return {
                            ...edge,
                            label: val || undefined,
                            labelStyle: { fill: '#a5b4fc', fontWeight: 600, fontSize: '10px' },
                            labelBgPadding: [6, 4],
                            labelBgRadius: 4,
                            labelBgStyle: { fill: '#1e293b', fillOpacity: 0.8 },
                          };
                        }
                        return edge;
                      })
                    );
                  }}
                  placeholder="e.g. true, false, approved, rejected, FAQ"
                  className="w-full bg-slate-900 border border-slate-800 focus:border-indigo-500 rounded-lg px-2.5 py-2 text-xs outline-none"
                />
                <span className="text-[9px] text-slate-500 mt-1 block">
                  Defines the trigger output keyword mapping to route along this edge path.
                </span>
              </div>

              <div className="pt-2 border-t border-slate-900/60 flex items-center justify-between gap-2">
                <button
                  onClick={handleDeleteSelectedEdge}
                  className="px-2.5 py-1.5 bg-rose-950/20 hover:bg-rose-950/40 border border-rose-500/20 text-rose-400 text-[10px] font-bold rounded-lg transition-colors"
                >
                  Delete Edge
                </button>
                <button
                  onClick={handleUpdateEdgeSettings}
                  className="px-3 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white text-[10px] font-bold rounded-lg transition-colors"
                >
                  Apply Route
                </button>
              </div>
            </div>
          )}

          {!selectedNode && !selectedEdge && (
            <div className="p-8 text-center text-xs text-slate-500 font-medium">
              Click a node or routing line edge on the canvas to configure its settings.
            </div>
          )}
        </aside>
      </div>

    </div>
  );
};

export default Workflows;
