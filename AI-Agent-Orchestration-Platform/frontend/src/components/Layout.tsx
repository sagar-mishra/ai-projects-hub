import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  GitBranch, 
  Activity, 
  Layers, 
  Settings as SettingsIcon,
  Bot
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navItems = [
    { to: '/', label: 'Dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
    { to: '/agents', label: 'Agents', icon: <Bot className="w-5 h-5" /> },
    { to: '/workflows', label: 'Workflows', icon: <GitBranch className="w-5 h-5" /> },
    { to: '/monitor', label: 'Monitor', icon: <Activity className="w-5 h-5" /> },
    { to: '/templates', label: 'Templates', icon: <Layers className="w-5 h-5" /> },
  ];

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 glass border-r border-slate-800 flex flex-col justify-between shrink-0">
        <div>
          {/* Logo */}
          <div className="h-20 flex items-center px-6 border-b border-slate-900 gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center glow-indigo">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-extrabold text-base tracking-wider bg-gradient-to-r from-white via-indigo-200 to-indigo-400 bg-clip-text text-transparent">
                PIKA ORCHESTRATOR
              </h1>
              <p className="text-[10px] text-indigo-400/70 font-semibold uppercase tracking-widest -mt-0.5">
                Agentic State Machine
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-4 space-y-1.5">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) => `
                  flex items-center gap-3.5 px-4 py-3 rounded-xl transition-all duration-300 text-sm font-medium
                  ${isActive 
                    ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/20 shadow-[inset_0_1px_1px_rgba(255,255,255,0.05)] font-semibold' 
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/40 border border-transparent'
                  }
                `}
              >
                {item.icon}
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-900/60 text-center">
          <div className="text-[11px] text-slate-500 font-medium">
            Pika Orchestrator
          </div>
          <div className="text-[9px] text-slate-600 mt-0.5">
            Powered by LangGraph & Groq
          </div>
        </div>
      </aside>

      {/* Main Content Pane */}
      <main className="flex-1 flex flex-col min-w-0 overflow-y-auto">
        <header className="h-20 border-b border-slate-900/60 px-8 flex items-center justify-between shrink-0 glass z-10 sticky top-0">
          <div className="flex items-center gap-3">
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-widest">
              Local Orchestrator Status: Connected
            </span>
          </div>
          
          <div className="flex items-center gap-4">
            <span className="text-xs bg-slate-900 border border-slate-800 text-slate-300 px-3 py-1.5 rounded-lg font-medium">
              API Mode: <span className="text-indigo-400 font-bold">Groq Llama-3</span>
            </span>
          </div>
        </header>

        <div className="flex-1 p-8">
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
