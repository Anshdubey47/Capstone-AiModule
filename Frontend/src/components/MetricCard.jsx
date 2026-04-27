import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown } from 'lucide-react';

const MetricCard = ({ title, value, trend, isPrimary, status, icon, isBadge, badgeColor }) => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -5, boxShadow: isPrimary && status === 'danger' ? '0 10px 40px -10px rgba(239, 68, 68, 0.4)' : '0 10px 30px -10px rgba(0, 0, 0, 0.3)' }}
      className={`glass-card p-6 rounded-3xl relative overflow-hidden group transition-all duration-300 ${isPrimary ? 'h-full' : ''}`}
    >
      {/* Background Subtle Gradient */}
      <div className={`absolute top-0 right-0 w-32 h-32 blur-[80px] -mr-8 -mt-8 opacity-20 pointer-events-none transition-opacity group-hover:opacity-40 ${status === 'danger' ? 'bg-danger' : 'bg-primary'}`} />

      <div className="flex flex-col h-full justify-between gap-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className={`p-2 rounded-xl transition-colors ${isPrimary && status === 'danger' ? 'bg-danger/20' : 'bg-white/5'}`}>
              {icon}
            </div>
            <span className="text-sm font-semibold text-muted tracking-tight">{title}</span>
          </div>
          {trend && (
            <div className={`flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full ${trend.startsWith('+') ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'}`}>
              {trend.startsWith('+') ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
              {trend}
            </div>
          )}
        </div>

        <div className="flex items-end justify-between mt-2">
          {isBadge ? (
            <div className="flex items-center gap-2">
              <span className="text-3xl font-bold tracking-tight">{value}</span>
              <span className={`px-2.5 py-0.5 rounded-md text-[10px] font-extrabold uppercase tracking-widest ${badgeColor === 'green' ? 'bg-success/20 text-success border border-success/30' : 'bg-primary/20 text-primary border border-primary/30'}`}>
                Active
              </span>
            </div>
          ) : (
            <h3 className={`text-4xl lg:text-5xl font-black tracking-tight ${isPrimary && status === 'danger' ? 'text-danger drop-shadow-[0_0_15px_rgba(239,68,68,0.5)]' : ''}`}>
              {value}
            </h3>
          )}
        </div>

        {isPrimary && status === 'danger' && (
          <motion.div 
            animate={{ opacity: [0.4, 0.7, 0.4] }}
            transition={{ repeat: Infinity, duration: 2 }}
            className="absolute inset-0 border-2 border-danger/20 rounded-3xl pointer-events-none"
          />
        )}
      </div>
    </motion.div>
  );
};

export default MetricCard;
