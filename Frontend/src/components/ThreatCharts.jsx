import React from 'react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, Cell
} from 'recharts';

const ThreatCharts = ({ events = [] }) => {
  // Map events to score distribution data
  const scoreData = events.slice(-15).map((e, idx) => ({
    time: `E${idx + 1}`,
    perception: e.perception,
    forecasting: e.forecasting,
    lstm: e.lstm
  }));

  // Calculate histogram data from confidence
  const histData = [
    { range: '0-20%', count: events.filter(e => e.confidence < 0.2).length },
    { range: '20-40%', count: events.filter(e => e.confidence >= 0.2 && e.confidence < 0.4).length },
    { range: '40-60%', count: events.filter(e => e.confidence >= 0.4 && e.confidence < 0.6).length },
    { range: '60-80%', count: events.filter(e => e.confidence >= 0.6 && e.confidence < 0.8).length },
    { range: '80-100%', count: events.filter(e => e.confidence >= 0.8).length },
  ];

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-card w-48 border border-border p-3 rounded-xl shadow-2xl backdrop-blur-md">
          <p className="text-[10px] text-muted font-bold uppercase tracking-widest mb-2">{label}</p>
          {payload.map((entry, index) => (
            <div key={index} className="flex items-center justify-between gap-4 mb-1">
              <span className="text-xs font-medium text-gray-400 capitalize">{entry.name}:</span>
              <span className="text-xs font-bold" style={{ color: entry.color }}>
                {(entry.value * 100).toFixed(0)}%
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 h-full">
      {/* SCORE DISTRIBUTION */}
      <div className="md:col-span-2 glass-card rounded-3xl p-6 border-white/[0.05]">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-lg font-bold tracking-tight">Score Distribution</h2>
            <p className="text-xs text-muted">Agentic AI cross-layer analysis (last 15 events)</p>
          </div>
          <div className="flex gap-4">
            <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-primary" /><span className="text-[10px] font-bold text-muted uppercase">Perception</span></div>
            <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-success" /><span className="text-[10px] font-bold text-muted uppercase">Forecasting</span></div>
            <div className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-warning" /><span className="text-[10px] font-bold text-muted uppercase">LSTM</span></div>
          </div>
        </div>

        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={scoreData}>
              <defs>
                <linearGradient id="colorPerc" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1F2937" />
              <XAxis 
                dataKey="time" 
                axisLine={false} 
                tickLine={false} 
                tick={{ fill: '#4B5563', fontSize: 10, fontWeight: 600 }}
                dy={10}
              />
              <YAxis 
                axisLine={false} 
                tickLine={false} 
                tick={{ fill: '#4B5563', fontSize: 10 }}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="perception" stroke="#3B82F6" strokeWidth={3} fillOpacity={1} fill="url(#colorPerc)" />
              <Area type="monotone" dataKey="forecasting" stroke="#22C55E" strokeWidth={3} fill="transparent" />
              <Area type="monotone" dataKey="lstm" stroke="#F59E0B" strokeWidth={3} fill="transparent" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* THREAT PROBABILITY */}
      <div className="md:col-span-1 glass-card rounded-3xl p-6 border-white/[0.05]">
        <div className="mb-8">
          <h2 className="text-lg font-bold tracking-tight">Threat Probability</h2>
          <p className="text-xs text-muted">Distribution of event confidence</p>
        </div>

        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={histData}>
              <Tooltip 
                cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    return (
                      <div className="bg-card border border-border p-2 rounded-lg shadow-xl">
                        <p className="text-xs font-bold text-primary">{payload[0].value} events</p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {histData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={index > 3 ? '#EF4444' : (index > 2 ? '#F59E0B' : '#3B82F6')} 
                    fillOpacity={0.8}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default ThreatCharts;
