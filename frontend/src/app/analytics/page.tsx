"use client";

import { useState, useEffect } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  CartesianGrid
} from "recharts";
import { BarChart3, Activity, AlertTriangle, MessageSquare, TrendingUp } from "lucide-react";
import { AnalyticsOverview } from "@/lib/types";
import { fetchAnalyticsOverview } from "@/lib/api";

const CLINICAL_COLORS = ["#0D9488", "#0284C7", "#6366F1", "#8B5CF6", "#EC4899", "#F59E0B", "#10B981"];

export default function AnalyticsDashboardPage() {
  const [data, setData] = useState<AnalyticsOverview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const overview = await fetchAnalyticsOverview();
      setData(overview);
    } catch (e) {
      // Handle error
    } finally {
      setLoading(false);
    }
  };

  if (loading || !data) {
    return (
      <div className="flex items-center justify-center h-64 text-slate-400 text-xs">
        Loading clinical epidemiological analytics...
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white border border-slate-200 rounded-lg p-5 flex items-center justify-between shadow-xs">
        <div>
          <div className="flex items-center space-x-2">
            <BarChart3 className="w-5 h-5 text-clinical-teal" />
            <h1 className="text-base font-bold text-clinical-navy">
              Epidemiological Analytics & Population Surveillance
            </h1>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Aggregated symptom patterns, clinical domain queries, intent categorization, and patient query length
            distributions derived from anonymized encounter logs.
          </p>
        </div>
        <span className="text-xs font-mono bg-slate-100 text-slate-600 px-3 py-1 rounded border border-slate-200">
          Cohort: All De-Identified Encounters
        </span>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs">
          <div className="flex justify-between items-center text-slate-500 text-xs">
            <span>Total Triage Encounters</span>
            <Activity className="w-4 h-4 text-clinical-teal" />
          </div>
          <p className="text-2xl font-bold text-clinical-navy mt-2">{data.total_triage_sessions}</p>
          <span className="text-[11px] text-emerald-600 font-medium">100% HIPAA Safe Harbor scrubbed</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs">
          <div className="flex justify-between items-center text-slate-500 text-xs">
            <span>Messages Processed</span>
            <MessageSquare className="w-4 h-4 text-sky-600" />
          </div>
          <p className="text-2xl font-bold text-clinical-navy mt-2">{data.total_messages_processed}</p>
          <span className="text-[11px] text-slate-400">Conversational dialogue turns</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs">
          <div className="flex justify-between items-center text-slate-500 text-xs">
            <span>Emergency Red Flags</span>
            <AlertTriangle className="w-4 h-4 text-red-600" />
          </div>
          <p className="text-2xl font-bold text-red-600 mt-2">{data.emergency_escalations_count}</p>
          <span className="text-[11px] text-red-700 font-medium">Sub-millisecond rescue dispatches</span>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-4 shadow-xs">
          <div className="flex justify-between items-center text-slate-500 text-xs">
            <span>Escalation Acuity Rate</span>
            <TrendingUp className="w-4 h-4 text-amber-600" />
          </div>
          <p className="text-2xl font-bold text-amber-600 mt-2">{data.emergency_escalation_rate_pct}%</p>
          <span className="text-[11px] text-slate-400">Of total presenting cohort</span>
        </div>
      </div>

      {/* Chart Row 1: Symptom Frequencies & Domain Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Symptom Frequency Bar Chart */}
        <div className="lg:col-span-7 bg-white border border-slate-200 rounded-lg p-5 shadow-xs">
          <div className="border-b border-slate-200 pb-2 mb-4">
            <h2 className="text-xs font-bold text-slate-700 uppercase tracking-wide">
              Chief Symptom Presentation Frequency
            </h2>
            <span className="text-[11px] text-slate-400">Total reported complaints in clinical narratives</span>
          </div>

          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.symptom_frequencies} layout="vertical" margin={{ top: 5, right: 20, left: 80, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
                <XAxis type="number" textAnchor="end" tick={{ fontSize: 11, fill: "#64748B" }} />
                <YAxis dataKey="symptom_category" type="category" tick={{ fontSize: 11, fill: "#334155" }} width={120} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#0F172A", border: "none", borderRadius: "4px", color: "#F8FAFC", fontSize: "11px" }}
                />
                <Bar dataKey="frequency_count" fill="#0D9488" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Clinical Domain Queries */}
        <div className="lg:col-span-5 bg-white border border-slate-200 rounded-lg p-5 shadow-xs">
          <div className="border-b border-slate-200 pb-2 mb-4">
            <h2 className="text-xs font-bold text-slate-700 uppercase tracking-wide">
              Clinical Sub-Specialty Distribution
            </h2>
            <span className="text-[11px] text-slate-400">Queries mapped to verified guidelines</span>
          </div>

          <div className="h-64 flex items-center justify-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data.domain_breakdown}
                  dataKey="query_count"
                  nameKey="clinical_domain"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={3}
                >
                  {data.domain_breakdown.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={CLINICAL_COLORS[index % CLINICAL_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: "#0F172A", border: "none", borderRadius: "4px", color: "#F8FAFC", fontSize: "11px" }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-2 gap-2 mt-2 text-[11px] text-slate-600">
            {data.domain_breakdown.map((d, idx) => (
              <div key={d.clinical_domain} className="flex items-center space-x-1.5">
                <span className="w-2.5 h-2.5 rounded-xs" style={{ backgroundColor: CLINICAL_COLORS[idx % CLINICAL_COLORS.length] }} />
                <span className="truncate">{d.clinical_domain}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Chart Row 2: Intent Classification & Token Length Histogram */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Intent Distribution */}
        <div className="lg:col-span-6 bg-white border border-slate-200 rounded-lg p-5 shadow-xs">
          <div className="border-b border-slate-200 pb-2 mb-4">
            <h2 className="text-xs font-bold text-slate-700 uppercase tracking-wide">
              Clinical Intent Classification
            </h2>
            <span className="text-[11px] text-slate-400">Distribution of patient conversational goals</span>
          </div>

          <div className="space-y-3">
            {data.intent_distributions.map((intent) => (
              <div key={intent.intent_label}>
                <div className="flex justify-between text-xs text-slate-700 mb-1">
                  <span className="font-medium">{intent.intent_label}</span>
                  <span className="font-mono text-slate-500">{intent.percentage}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div className="bg-clinical-teal h-2 rounded-full" style={{ width: `${intent.percentage}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Token Histogram */}
        <div className="lg:col-span-6 bg-white border border-slate-200 rounded-lg p-5 shadow-xs">
          <div className="border-b border-slate-200 pb-2 mb-4">
            <h2 className="text-xs font-bold text-slate-700 uppercase tracking-wide">
              Query Token & Length Distribution
            </h2>
            <span className="text-[11px] text-slate-400">Word count density of patient clinical inputs</span>
          </div>

          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data.query_length_distribution} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="token_range" tick={{ fontSize: 11, fill: "#64748B" }} />
                <YAxis tick={{ fontSize: 11, fill: "#64748B" }} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#0F172A", border: "none", borderRadius: "4px", color: "#F8FAFC", fontSize: "11px" }}
                />
                <Bar dataKey="frequency" fill="#0284C7" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
