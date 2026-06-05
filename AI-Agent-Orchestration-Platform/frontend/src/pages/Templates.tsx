import React, { useEffect } from 'react';
import { useStore } from '../store/useStore';
import { useNavigate } from 'react-router-dom';
import { 
  Layers, 
  ArrowRight, 
  GitBranch, 
  HelpCircle, 
  ShieldAlert, 
  Calculator,
  Search,
  CheckCircle,
  FileCode
} from 'lucide-react';

const Templates: React.FC = () => {
  const { templates, fetchTemplates, loadTemplate } = useStore();
  const navigate = useNavigate();

  useEffect(() => {
    fetchTemplates();
  }, []);

  const handleLoadTemplate = async (key: string) => {
    try {
      const wf = await loadTemplate(key);
      alert(`Template loaded successfully: ${wf.name}`);
      navigate('/workflows');
    } catch {
      alert("Failed to load template.");
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-extrabold tracking-tight text-white font-sans">
          Pre-built Workflow Templates
        </h2>
        <p className="text-slate-400 text-sm mt-1">
          Select one of our workflow blueprints to instantiate agents, routing conditions, and connection edges automatically.
        </p>
      </div>

      {/* Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        
        {/* Card 1: Research Pipeline */}
        <div className="glass rounded-2xl p-6 border border-slate-800 flex flex-col justify-between hover:border-slate-700 transition-all duration-300 relative glow-indigo overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-2xl"></div>
          <div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center border border-indigo-500/20 glow-indigo">
                <Search className="w-5.5 h-5.5" />
              </div>
              <h3 className="font-extrabold text-lg text-white">Research Pipeline</h3>
            </div>
            
            <p className="text-slate-400 text-xs mt-4 leading-relaxed">
              Linear multi-agent research machine: A **Researcher** searches online sources via DuckDuckGo and submits structured results. A **Fact Checker** verifies claims and corrects assertions. A **Summarizer** drafts a Markdown report for Telegram.
            </p>

            <div className="mt-6 pt-4 border-t border-slate-900/60 space-y-2">
              <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Agents Loaded</div>
              <div className="flex flex-wrap gap-1.5">
                <span className="px-2 py-0.5 bg-slate-900 border border-slate-800 text-slate-300 rounded text-[10px]">Researcher</span>
                <span className="px-2 py-0.5 bg-slate-900 border border-slate-800 text-slate-300 rounded text-[10px]">Fact Checker</span>
                <span className="px-2 py-0.5 bg-slate-900 border border-slate-800 text-slate-300 rounded text-[10px]">Summarizer</span>
              </div>
            </div>

            <div className="mt-4 space-y-2">
              <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Visual Connections</div>
              <div className="text-xs font-mono text-slate-400 flex items-center gap-1.5">
                <span>Trigger</span>
                <ArrowRight className="w-3 h-3 text-slate-600" />
                <span className="text-indigo-400">Researcher</span>
                <ArrowRight className="w-3 h-3 text-slate-600" />
                <span className="text-indigo-400">Fact Checker</span>
                <ArrowRight className="w-3 h-3 text-slate-600" />
                <span className="text-indigo-400">Summarizer</span>
                <ArrowRight className="w-3 h-3 text-slate-600" />
                <span>End</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => handleLoadTemplate('research_pipeline')}
            className="w-full mt-8 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold transition-all duration-300 flex items-center justify-center gap-1.5"
          >
            Instantiate Research Blueprints
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

        {/* Card 2: Support Triage */}
        <div className="glass rounded-2xl p-6 border border-slate-800 flex flex-col justify-between hover:border-slate-700 transition-all duration-300 relative glow-indigo overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-2xl"></div>
          <div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center border border-purple-500/20 glow-purple">
                <GitBranch className="w-5.5 h-5.5" />
              </div>
              <h3 className="font-extrabold text-lg text-white">Support Triage</h3>
            </div>
            
            <p className="text-slate-400 text-xs mt-4 leading-relaxed">
              Branching multi-agent support router: A **Classifier** reads messages and routes them. FAQ requests map to **FAQ Bot** (with calculator). Complaints route to **Resolver** (offering discounts). Escalations trigger a **Human-in-the-Loop** operator approval request.
            </p>

            <div className="mt-6 pt-4 border-t border-slate-900/60 space-y-2">
              <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Agents Loaded</div>
              <div className="flex flex-wrap gap-1.5">
                <span className="px-2 py-0.5 bg-slate-900 border border-slate-800 text-slate-300 rounded text-[10px]">Classifier</span>
                <span className="px-2 py-0.5 bg-slate-900 border border-slate-800 text-slate-300 rounded text-[10px]">FAQ Bot</span>
                <span className="px-2 py-0.5 bg-slate-900 border border-slate-800 text-slate-300 rounded text-[10px]">Resolver</span>
              </div>
            </div>

            <div className="mt-4 space-y-2">
              <div className="text-[10px] text-slate-500 font-bold uppercase tracking-wider">Visual Connections</div>
              <div className="text-xs font-mono text-slate-400 flex items-center gap-1.5">
                <span>Trigger</span>
                <ArrowRight className="w-3 h-3 text-slate-600" />
                <span className="text-indigo-400">Classifier</span>
                <ArrowRight className="w-3 h-3 text-slate-600" />
                <span>Condition</span>
                <span className="text-[10px] text-slate-600 px-1 border border-slate-900 rounded font-sans">FAQ / COMPLAINT / ESCALATE</span>
              </div>
            </div>
          </div>

          <button
            onClick={() => handleLoadTemplate('support_triage')}
            className="w-full mt-8 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-xs font-bold transition-all duration-300 flex items-center justify-center gap-1.5"
          >
            Instantiate Triage Blueprints
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>

      </div>
    </div>
  );
};

export default Templates;
