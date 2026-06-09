import { useEffect, useState, useCallback } from "react";
import {
  Users,
  DollarSign,
  TrendingUp,
  Database,
  Clock,
  RefreshCw,
  Wifi,
  WifiOff,
} from "lucide-react";
import { api } from "../services/api";
import type { HealthResponse, SyncStatus, SyncResult } from "../types/player";
import StatCard from "../components/StatCard";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorBanner from "../components/ErrorBanner";

function fmt_salary(v: number) {
  return `$${(v / 1_000_000).toFixed(2)}M`;
}

function fmt_time(iso: string) {
  return new Date(iso).toLocaleString();
}

function fmt_relative(iso: string | null): string {
  if (!iso) return "Never";
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  return new Date(iso).toLocaleDateString();
}

const ROADMAP = [
  {
    phase: 1,
    title: "Data Pipeline & Player Browser",
    status: "complete",
    desc: "SQLite database, FastAPI backend, searchable player browser, WAR/salary value engine.",
  },
  {
    phase: 2,
    title: "Live MLB API Integration",
    status: "complete",
    desc: "Real-time feeds from MLB Stats API (statsapi.mlb.com) and FanGraphs WAR leaderboards.",
  },
  {
    phase: 3,
    title: "ML Player Valuation",
    status: "upcoming",
    desc: "Train regression/gradient-boost models to predict true player value using 10+ seasons of data.",
  },
  {
    phase: 4,
    title: "Roster Builder",
    status: "upcoming",
    desc: "Build custom 20-player rosters under a salary cap. Optimize for positional balance.",
  },
  {
    phase: 5,
    title: "Win Prediction Engine",
    status: "upcoming",
    desc: "Project team win % based on composite roster WAR and run differential modeling.",
  },
  {
    phase: 6,
    title: "Multi-Season Simulation",
    status: "upcoming",
    desc: "Simulate player aging curves and multi-year contract value trajectories.",
  },
];

export default function Dashboard() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [syncStatus, setSyncStatus] = useState<SyncStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [syncResult, setSyncResult] = useState<SyncResult | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [h, s] = await Promise.all([api.health(), api.syncStatus()]);
      setHealth(h);
      setSyncStatus(s);
      setError(null);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Failed to reach API";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSync = async () => {
    setSyncing(true);
    setSyncResult(null);
    try {
      const result = await api.triggerSync();
      setSyncResult(result);
      await loadData();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Sync failed";
      setSyncResult({ status: "error", message: msg });
    } finally {
      setSyncing(false);
    }
  };

  if (loading) return <LoadingSpinner message="Connecting to analytics engine..." />;

  const isLive = syncStatus?.data_source === "live";

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">Analytics Dashboard</h2>
          <p className="text-gray-500 mt-1 text-sm">
            Real-time stats from your player database.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border ${
              isLive
                ? "bg-green-500/10 border-green-500/30 text-green-400"
                : "bg-yellow-500/10 border-yellow-500/30 text-yellow-400"
            }`}
          >
            {isLive ? <Wifi size={12} /> : <WifiOff size={12} />}
            {isLive
              ? `Live · ${syncStatus?.season ?? ""} Season`
              : "Mock Data · Phase 1"}
          </div>

          <button
            onClick={handleSync}
            disabled={syncing}
            className="flex items-center gap-2 px-4 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed text-white text-xs font-semibold transition-colors"
          >
            <RefreshCw size={13} className={syncing ? "animate-spin" : ""} />
            {syncing ? "Syncing…" : "Sync Live Data"}
          </button>
        </div>
      </div>

      {error && (
        <ErrorBanner
          message={`Backend unavailable: ${error}. Make sure the API server is running.`}
        />
      )}

      {syncResult && (
        <div
          className={`rounded-xl border p-4 text-sm ${
            syncResult.status === "complete"
              ? "border-green-500/40 bg-green-500/5 text-green-300"
              : "border-red-500/40 bg-red-500/5 text-red-300"
          }`}
        >
          {syncResult.status === "complete" ? (
            <span>
              ✓ Live sync complete — <strong>{syncResult.created}</strong> players
              loaded from MLB Stats API + FanGraphs · Season{" "}
              <strong>{syncResult.season}</strong> ·{" "}
              {syncResult.war_matched} WAR values matched ·{" "}
              {syncResult.salary_matched} salaries matched
            </span>
          ) : (
            <span>✗ Sync failed: {syncResult.message ?? syncResult.error}</span>
          )}
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="Total Players"
          value={health?.stats.total ?? "—"}
          icon={<Users size={18} />}
          accent="green"
          sub="in database"
        />
        <StatCard
          label="Avg Salary"
          value={health ? fmt_salary(health.stats.avg_salary) : "—"}
          icon={<DollarSign size={18} />}
          accent="yellow"
          sub="per player"
        />
        <StatCard
          label="Avg WAR"
          value={health ? health.stats.avg_war.toFixed(2) : "—"}
          icon={<TrendingUp size={18} />}
          accent="blue"
          sub="wins above replacement"
        />
        <StatCard
          label="Avg OPS"
          value={health ? health.stats.avg_ops.toFixed(3) : "—"}
          icon={<Database size={18} />}
          accent="purple"
          sub="on-base + slugging"
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <Database size={16} className="text-green-400" />
            <h3 className="text-white font-semibold text-sm">Database Status</h3>
          </div>
          <div className="flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                health?.database === "connected" ? "bg-green-400" : "bg-red-400"
              } animate-pulse`}
            />
            <span
              className={`text-sm font-medium ${
                health?.database === "connected" ? "text-green-400" : "text-red-400"
              }`}
            >
              {health?.database === "connected" ? "Connected" : health?.database ?? "Offline"}
            </span>
          </div>
          <p className="text-gray-500 text-xs mt-2">SQLite · moneyball.db</p>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <Clock size={16} className="text-blue-400" />
            <h3 className="text-white font-semibold text-sm">Last Synced</h3>
          </div>
          <p className="text-white text-sm font-medium">
            {fmt_relative(syncStatus?.last_synced ?? null)}
          </p>
          <p className="text-gray-500 text-xs mt-2">
            {syncStatus?.last_synced ? fmt_time(syncStatus.last_synced) : "No live sync yet"}
          </p>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            {isLive ? (
              <Wifi size={16} className="text-green-400" />
            ) : (
              <WifiOff size={16} className="text-yellow-400" />
            )}
            <h3 className="text-white font-semibold text-sm">Data Source</h3>
          </div>
          <div className="flex items-center gap-2">
            <span
              className={`text-sm font-semibold ${isLive ? "text-green-400" : "text-yellow-400"}`}
            >
              {isLive ? "MLB Stats API + FanGraphs" : "Mock Data (2024)"}
            </span>
          </div>
          <p className="text-gray-500 text-xs mt-2">
            {isLive
              ? `${syncStatus?.live_count} live · Season ${syncStatus?.season}`
              : `${syncStatus?.mock_count ?? 0} players · Click Sync to load real data`}
          </p>
        </div>
      </div>

      <div>
        <h3 className="text-white font-semibold mb-4">Development Roadmap</h3>
        <div className="space-y-3">
          {ROADMAP.map((item) => (
            <div
              key={item.phase}
              className={`rounded-xl border p-4 flex items-start gap-4 ${
                item.status === "complete"
                  ? "border-green-500/40 bg-green-500/5"
                  : "border-gray-800 bg-gray-900/50"
              }`}
            >
              <div
                className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 text-sm font-bold ${
                  item.status === "complete"
                    ? "bg-green-500 text-gray-950"
                    : "bg-gray-800 text-gray-500"
                }`}
              >
                {item.phase}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span
                    className={`font-semibold text-sm ${
                      item.status === "complete" ? "text-green-400" : "text-gray-300"
                    }`}
                  >
                    Phase {item.phase}: {item.title}
                  </span>
                  {item.status === "complete" && (
                    <span className="text-xs bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full font-medium">
                      Complete
                    </span>
                  )}
                </div>
                <p className="text-gray-500 text-xs mt-1">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
