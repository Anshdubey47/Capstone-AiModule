import React from 'react';
import { motion } from 'framer-motion';
import { Zap, AlertCircle, ArrowRight, BrainCircuit, Fingerprint, Activity } from 'lucide-react';

const InsightItem = ({ icon: Icon, color, text, delay }) => (
  <motion.div 
    initial={{ opacity: 0, x: 20 }}
    animate={{ opacity: 1, x: 0 }}
    transition={{ delay }}
    className="flex items-start gap-4 p-4 rounded-2xl bg-white/[0.03] border border-white/[0.05] hover:border-white/10 transition-colors group cursor-default"
  >
    <div className={`p-2 rounded-lg bg-${color}/10 mt-0.5`}>
      <Icon className={`text-${color}`} size={16} />
    </div>
    <p className="text-sm font-medium leading-relaxed text-gray-300 transition-colors group-hover:text-white line-clamp-2">
      {text}
    </p>
  </motion.div>
);

const AIInsights = ({ events = [] }) => {
  const threats = events.filter(e => e.status === 'BLOCK').slice(0, 3);
  
  return (
    <div className="glass-card rounded-3xl p-6 h-full flex flex-col border-white/[0.05]">
      <div className="flex items-center gap-2 mb-6">
        <div className="relative">
          <Zap className="text-warning fill-warning/20" size={20} />
          <motion.div 
            animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }}
            transition={{ repeat: Infinity, duration: 2 }}
            className="absolute inset-0 bg-warning rounded-full blur-md"
          />
        </div>
        <h2 className="text-lg font-bold tracking-tight">AI Insights</h2>
      </div>

      <div className="space-y-3 flex-1 overflow-y-auto pr-2 scrollbar-hide">
        {threats.length > 0 ? (
          threats.map((t, i) => (
            <InsightItem 
              key={t.id}
              icon={AlertCircle} 
              color="danger" 
              text={t.rationale} 
              delay={i * 0.1}
            />
          ))
        ) : (
          <InsightItem 
            icon={Activity} 
            color="primary" 
            text="No immediate threats detected. System monitoring baseline traffic." 
            delay={0.1}
          />
        )}
      </div>

      <div className="mt-8 pt-6 border-t border-border">
        <p className="text-[10px] text-muted font-bold uppercase tracking-widest mb-3">Suggested Action</p>
        <button className="w-full flex items-center justify-between p-4 rounded-2xl bg-danger/10 border border-danger/20 hover:bg-danger/20 transition-all group">
          <div className="flex items-center gap-3">
            <AlertCircle className="text-danger" size={18} />
            <span className="text-sm font-bold text-danger">
              {threats.length > 0 ? `Block Source IP ${threats[0].srcIp}` : "Enable Enhanced Stealth Mode"}
            </span>
          </div>
          <ArrowRight className="text-danger transform group-hover:translate-x-1 transition-transform" size={16} />
        </button>
      </div>
    </div>
  );
};

export default AIInsights;
