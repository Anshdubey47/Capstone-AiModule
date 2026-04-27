import React from 'react';
import { Shield, Play, Layout, Cpu } from 'lucide-react';

const Header = ({ isLive, onRun }) => {
  return (
    <header className="h-20 border-b border-border bg-background/50 backdrop-blur-md sticky top-0 z-40 px-8 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <div className="w-10 h-10 bg-primary/20 rounded-xl flex items-center justify-center border border-primary/30">
          <Shield className="text-primary" size={24} />
        </div>
        <div>
          <h1 className="text-xl font-bold tracking-tight">Zero-Day Defense System</h1>
          <p className="text-xs text-muted font-medium uppercase tracking-wider flex items-center gap-1.5 line-clamp-1">
            <Cpu size={12} /> Multi-layered Agentic AI Network Protection
          </p>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="hidden xl:flex items-center gap-6 mr-6 border-r border-border pr-6">
          <div className="text-right">
            <p className="text-[10px] text-muted font-bold uppercase tracking-widest">Network Status</p>
            <p className="text-sm font-semibold text-success flex items-center gap-1 justify-end">
              <span className="w-2 h-2 rounded-full bg-success animate-pulse" /> Protected
            </p>
          </div>
          <div className="text-right">
            <p className="text-[10px] text-muted font-bold uppercase tracking-widest">AI Core</p>
            <p className="text-sm font-semibold">v3.4.1 (Stable)</p>
          </div>
        </div>
        
        <button className="secondary-button text-sm flex items-center gap-2">
          <Layout size={16} /> Deploy
        </button>
        <button 
          onClick={onRun}
          className={`prime-button text-sm flex items-center gap-2 ${isLive ? 'bg-danger shadow-danger/20 hover:bg-red-600' : ''}`}
        >
          {isLive ? <Pause size={16} /> : <Play size={16} />}
          {isLive ? 'Stop Analysis' : 'Run Live Analysis'}
        </button>
      </div>
    </header>
  );
};

const Pause = ({ size }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="6" y="4" width="4" height="16" /><rect x="14" y="4" width="4" height="16" />
  </svg>
);

export default Header;
