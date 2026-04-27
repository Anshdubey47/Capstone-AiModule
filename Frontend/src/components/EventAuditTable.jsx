import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, ShieldAlert, CheckCircle, ExternalLink, MoreVertical } from 'lucide-react';

const EventAuditTable = ({ events }) => {
  const [expandedId, setExpandedId] = useState(null);

  const toggleRow = (id) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="glass-card rounded-3xl overflow-hidden border-white/[0.05]">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b border-border bg-white/[0.02]">
              <th className="px-6 py-4 text-[10px] font-bold text-muted uppercase tracking-widest">Verdict</th>
              <th className="px-6 py-4 text-[10px] font-bold text-muted uppercase tracking-widest">Source IP</th>
              <th className="px-6 py-4 text-[10px] font-bold text-muted uppercase tracking-widest">Dest IP</th>
              <th className="px-6 py-4 text-[10px] font-bold text-muted uppercase tracking-widest hidden md:table-cell">Port</th>
              <th className="px-6 py-4 text-[10px] font-bold text-muted uppercase tracking-widest">Confidence</th>
              <th className="px-6 py-4 text-[10px] font-bold text-muted uppercase tracking-widest">Risk Level</th>
              <th className="px-6 py-4 text-right"></th>
            </tr>
          </thead>
          <tbody>
            {events.map((event) => (
              <React.Fragment key={event.id}>
                <tr 
                  onClick={() => toggleRow(event.id)}
                  className={`group cursor-pointer transition-colors border-b border-white/[0.03] ${event.status === 'BLOCK' ? 'hover:bg-danger/[0.03]' : 'hover:bg-primary/[0.03]'} ${expandedId === event.id ? (event.status === 'BLOCK' ? 'bg-danger/[0.05]' : 'bg-primary/[0.05]') : ''}`}
                >
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-[11px] font-bold ${event.status === 'BLOCK' ? 'bg-danger/20 text-danger border border-danger/20' : 'bg-success/20 text-success border border-success/20'}`}>
                      {event.status === 'BLOCK' ? <ShieldAlert size={12} /> : <CheckCircle size={12} />}
                      {event.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono font-medium text-sm">{event.srcIp}</td>
                  <td className="px-6 py-4 font-mono font-medium text-sm">{event.dstIp}</td>
                  <td className="px-6 py-4 font-mono text-muted text-sm hidden md:table-cell">{event.port}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="flex-1 w-24 h-1.5 bg-border rounded-full overflow-hidden">
                        <motion.div 
                          initial={{ width: 0 }}
                          animate={{ width: `${event.confidence * 100}%` }}
                          className={`h-full ${event.status === 'BLOCK' ? 'bg-danger' : 'bg-success'}`}
                        />
                      </div>
                      <span className="text-[11px] font-bold">{(event.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 font-semibold text-sm">
                    <span className={event.risk === 'Critical' ? 'text-danger' : (event.risk === 'High' ? 'text-warning' : 'text-success')}>
                      {event.risk}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2 text-muted group-hover:text-white transition-colors">
                      {expandedId === event.id ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                    </div>
                  </td>
                </tr>

                {/* EXPANDABLE ROW */}
                <AnimatePresence>
                  {expandedId === event.id && (
                    <tr>
                      <td colSpan={7} className="p-0">
                        <motion.div 
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          className="overflow-hidden bg-white/[0.01]"
                        >
                          <div className="p-8 grid grid-cols-1 lg:grid-cols-4 gap-8">
                            <div className="lg:col-span-1 space-y-4">
                              <div>
                                <p className="text-[10px] text-muted font-bold uppercase tracking-widest mb-1.5">AI core scores</p>
                                <div className="space-y-2">
                                  <ScoreMetric label="Perception" value={event.perception} color="primary" />
                                  <ScoreMetric label="Forecasting" value={event.forecasting} color="success" />
                                  <ScoreMetric label="LSTM" value={event.lstm} color="warning" />
                                </div>
                              </div>
                            </div>
                            <div className="lg:col-span-3 space-y-4">
                              <div>
                                <p className="text-[10px] text-muted font-bold uppercase tracking-widest mb-1.5">Agent Rationale</p>
                                <p className="text-sm leading-relaxed text-gray-300 bg-white/[0.03] p-4 rounded-xl border border-white/[0.05]">
                                  {event.rationale}
                                </p>
                              </div>
                              <div className="flex items-center gap-3">
                                <button className="px-4 py-2 rounded-lg bg-danger hover:bg-red-600 text-white text-xs font-bold transition-all shadow-lg shadow-danger/20">
                                  Terminate Session
                                </button>
                                <button className="px-4 py-2 rounded-lg bg-card border border-border hover:bg-border/50 text-white text-xs font-bold transition-all">
                                  Download Logs
                                </button>
                                <button className="px-4 py-2 rounded-lg bg-card border border-border hover:bg-border/50 text-primary text-xs font-bold transition-all flex items-center gap-1.5">
                                  <ExternalLink size={12} /> View Raw Trace
                                </button>
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      </td>
                    </tr>
                  )}
                </AnimatePresence>
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const ScoreMetric = ({ label, value, color }) => (
  <div className="flex items-center justify-between gap-6">
    <span className="text-[11px] font-medium text-gray-400">{label}</span>
    <div className="flex items-center gap-2">
      <span className={`text-[11px] font-bold text-${color}`}>{(value * 100).toFixed(1)}%</span>
    </div>
  </div>
);

export default EventAuditTable;
