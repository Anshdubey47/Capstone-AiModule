import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Shield, 
  Activity, 
  Zap, 
  Search, 
  AlertTriangle, 
  CheckCircle, 
  Lock, 
  RefreshCcw, 
  LayoutDashboard,
  ShieldAlert,
  BarChart3,
  Terminal,
  Settings,
  Pause,
  Play
} from 'lucide-react';
import Header from './components/Header';
import MetricCard from './components/MetricCard';
import AIInsights from './components/AIInsights';
import ThreatCharts from './components/ThreatCharts';
import EventAuditTable from './components/EventAuditTable';

const API_BASE = "http://localhost:8000";

const App = () => {
  const [isLive, setIsLive] = useState(false);
  const [focusMode, setFocusMode] = useState(false);
  const [metrics, setMetrics] = useState({
    total_events: 0,
    threats_detected: 0,
    avg_confidence: 0,
    system_health: "Optimal"
  });
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const res = await fetch(`${API_BASE}/data`);
      const data = await res.json();
      if (data.metrics) setMetrics(data.metrics);
      if (data.decisions) {
        // Map backend decision format to frontend format
        const mappedEvents = data.decisions.map((d, index) => ({
          id: index,
          status: d.threat ? 'BLOCK' : 'ALLOW',
          srcIp: d.src_ip || 'N/A',
          dstIp: d.dst_ip || 'N/A',
          port: d.dst_port || 'N/A',
          confidence: d.confidence || 0,
          risk: d.threat ? 'Critical' : 'Low',
          perception: d.scores?.perception || 0,
          forecasting: d.scores?.forecasting || 0,
          lstm: d.scores?.lstm || 0,
          rationale: d.rationale || 'No rationale provided.'
        }));
        setEvents(mappedEvents);
      }
      setLoading(false);
    } catch (err) {
      console.error("Failed to fetch data:", err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(() => {
      if (isLive) fetchData();
    }, 5000);
    return () => clearInterval(interval);
  }, [isLive]);

  const toggleAnalysis = async () => {
    if (isLive) {
      setIsLive(false);
      return;
    }
    
    try {
      setIsLive(true);
      await fetch(`${API_BASE}/run-analysis`, { method: 'POST' });
      // Poll faster during analysis to get initial read quicker
      setTimeout(fetchData, 1000);
      setTimeout(fetchData, 3000);
    } catch (err) {
      console.error("Failed to trigger analysis:", err);
      setIsLive(false);
    }
  };

  return (
    <div className="min-h-screen bg-background font-sans text-white pb-12 transition-colors duration-500">
      <Header isLive={isLive} onRun={toggleAnalysis} />
      
      <main className="max-w-[1600px] mx-auto px-6 mt-8 space-y-8">
        {/* HERO METRICS */}
        <section className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          <div className="lg:col-span-1">
            <MetricCard 
              title="Threats Detected" 
              value={metrics.threats_detected} 
              trend={metrics.threats_detected > 0 ? "+8%" : "0%"} 
              isPrimary={true}
              status={metrics.threats_detected > 0 ? 'danger' : 'success'}
              icon={<ShieldAlert className={metrics.threats_detected > 0 ? 'text-danger' : 'text-success'} size={24} />}
            />
          </div>
          <div className="lg:col-span-3 grid grid-cols-1 md:grid-cols-3 gap-6">
            <MetricCard 
              title="Total Events" 
              value={metrics.total_events} 
              trend="+12%" 
              icon={<Activity className="text-primary" size={20} />}
            />
            <MetricCard 
              title="Avg. Confidence" 
              value={`${metrics.avg_confidence}%`} 
              trend="+2%" 
              icon={<Zap className="text-warning" size={20} />}
            />
            <MetricCard 
              title="System Health" 
              value={metrics.system_health} 
              isBadge={true}
              badgeColor="green"
              icon={<CheckCircle className="text-success" size={20} />}
            />
          </div>
        </section>

        {/* MIDDLE SECTION: CHARTS AND INSIGHTS */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <ThreatCharts events={events} />
          </div>
          <div className="lg:col-span-1">
            <AIInsights events={events} />
          </div>
        </div>

        {/* BOTTOM SECTION: AUDIT TABLE */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Terminal className="text-primary" size={24} />
              <h2 className="text-xl font-bold tracking-tight">Real-Time Event Audit</h2>
            </div>
            <button 
              onClick={() => setFocusMode(!focusMode)}
              className={`text-sm px-4 py-1.5 rounded-full border transition-all ${focusMode ? 'bg-primary border-primary text-white' : 'border-border text-muted hover:text-white hover:border-muted'}`}
            >
              {focusMode ? 'Exit Focus Mode' : 'Focus Mode'}
            </button>
          </div>
          <EventAuditTable events={focusMode ? events.filter(e => e.status === 'BLOCK') : events} />
        </section>
      </main>

      {/* ACTION FAB */}
      <motion.div 
        initial={{ y: 100 }}
        animate={{ y: 0 }}
        className="fixed bottom-8 left-1/2 -translate-x-1/2 flex items-center gap-4 bg-card/80 backdrop-blur-xl border border-border p-2 rounded-2xl shadow-2xl z-50 px-6 py-3"
      >
        <span className="text-sm font-medium text-muted mr-4 border-r border-border pr-4">Global Actions</span>
        <button className="flex items-center gap-2 hover:text-danger transition-colors text-sm font-semibold">
          <Lock size={16} /> Block Range
        </button>
        <button className="flex items-center gap-2 hover:text-primary transition-colors text-sm font-semibold">
          <Search size={16} /> Deep Scan
        </button>
        <button className="flex items-center gap-2 hover:text-warning transition-colors text-sm font-semibold">
          <Shield size={16} /> Quarantine
        </button>
      </motion.div>
    </div>
  );
};

export default App;
