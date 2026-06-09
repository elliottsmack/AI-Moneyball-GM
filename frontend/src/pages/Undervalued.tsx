import { useEffect, useState } from "react";
import { Star, Cpu, TrendingUp } from "lucide-react";
import { api } from "../services/api";
import type { PlayerWithScore } from "../types/player";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorBanner from "../components/ErrorBanner";

function fmt_salary(v: number) {
  return `$${(v / 1_000_000).toFixed(1)}M`;
}

const POSITION_COLORS: Record<string, string> = {
  C: "bg-purple-500/20 text-purple-300",
  "1B": "bg-blue-500/20 text-blue-300",
  "2B": "bg-cyan-500/20 text-cyan-300",
  "3B": "bg-teal-500/20 text-teal-300",
  SS: "bg-green-500/20 text-green-300",
  LF: "bg-yellow-500/20 text-yellow-300",
  CF: "bg-orange-500/20 text-orange-300",
  RF: "bg-red-500/20 text-red-300",
  DH: "bg-pink-500/20 text-pink-300",
};

function ValueBar({ score, max }: { score: number; max: number }) {
  const pct = Math.min((score / max) * 100, 100);
  return (
    <div className="w-24 h-1.5 bg-gray-800 rounded-full overflow-hidden">
      <div
        className="h-full bg-gradient-to-r from-green-500 to-emerald-400 rounded-full transition-all"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}

export default function Undervalued() {
  const [players, setPlayers] = useState<PlayerWithScore[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [topN, setTopN] = useState(20);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api
      .undervalued(topN)
      .then(setPlayers)
      .catch((e) => setError(e.message ?? "Failed to fetch undervalued players"))
      .finally(() => setLoading(false));
  }, [topN]);

  const maxScore = players.length > 0 ? players[0].value_score : 1;

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Undervalued Players</h2>
        <p className="text-gray-500 mt-1 text-sm">
          Ranked by value score (WAR per $1M salary). Phase 3 will replace this with an ML model.
        </p>
      </div>

      <div className="flex items-start gap-4">
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex items-start gap-3 flex-1">
          <div className="w-9 h-9 rounded-lg bg-green-500/10 flex items-center justify-center flex-shrink-0">
            <TrendingUp size={16} className="text-green-400" />
          </div>
          <div>
            <p className="text-white font-semibold text-sm">Current Algorithm</p>
            <code className="text-green-400 text-xs bg-gray-800 px-2 py-0.5 rounded mt-1 inline-block">
              value_score = WAR / (salary_in_millions)
            </code>
            <p className="text-gray-500 text-xs mt-1">
              Simple, transparent, and interpretable. Designed to be swapped for an ML model in Phase 3.
            </p>
          </div>
        </div>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 flex items-start gap-3 flex-1">
          <div className="w-9 h-9 rounded-lg bg-purple-500/10 flex items-center justify-center flex-shrink-0">
            <Cpu size={16} className="text-purple-400" />
          </div>
          <div>
            <p className="text-white font-semibold text-sm">Phase 3 — ML Valuation</p>
            <p className="text-gray-500 text-xs mt-1">
              Gradient boosting model trained on 10+ seasons. Will factor in age curves, park effects, injury history, and contract years.
            </p>
          </div>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Star size={15} className="text-yellow-400" />
          <span className="text-white font-semibold text-sm">Top {topN} Undervalued Players</span>
        </div>
        <div className="flex gap-1">
          {[10, 20, 30].map((n) => (
            <button
              key={n}
              onClick={() => setTopN(n)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                topN === n ? "bg-green-500 text-gray-950" : "bg-gray-800 text-gray-400 hover:bg-gray-700"
              }`}
            >
              Top {n}
            </button>
          ))}
        </div>
      </div>

      {error && <ErrorBanner message={error} />}
      {loading ? (
        <LoadingSpinner message="Calculating value scores..." />
      ) : (
        <div className="overflow-x-auto rounded-xl border border-gray-800">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-900 border-b border-gray-800 text-gray-400 text-xs uppercase tracking-wider">
                <th className="text-left px-4 py-3 w-10">#</th>
                <th className="text-left px-4 py-3">Player</th>
                <th className="text-center px-3 py-3">Pos</th>
                <th className="text-left px-3 py-3">Team</th>
                <th className="text-right px-3 py-3">Salary</th>
                <th className="text-right px-3 py-3">WAR</th>
                <th className="text-right px-3 py-3">OPS</th>
                <th className="text-right px-3 py-3">HR</th>
                <th className="text-right px-3 py-3">Value Score</th>
                <th className="px-3 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {players.map((p, i) => {
                const posCls = POSITION_COLORS[p.position] ?? "bg-gray-700/30 text-gray-300";
                const isTop3 = i < 3;
                return (
                  <tr
                    key={p.player_id}
                    className={`border-b border-gray-800/50 hover:bg-gray-800/40 transition-colors ${
                      isTop3 ? "bg-green-500/5" : i % 2 === 0 ? "bg-gray-900/20" : ""
                    }`}
                  >
                    <td className="px-4 py-3">
                      <span className={`text-xs font-bold ${isTop3 ? "text-yellow-400" : "text-gray-600"}`}>
                        {i + 1}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-medium text-white whitespace-nowrap">
                      {isTop3 && <Star size={12} className="inline mr-1.5 text-yellow-400" />}
                      {p.name}
                    </td>
                    <td className="px-3 py-3 text-center">
                      <span className={`px-2 py-0.5 rounded text-xs font-semibold ${posCls}`}>
                        {p.position}
                      </span>
                    </td>
                    <td className="px-3 py-3 text-gray-300 font-mono text-xs">{p.team}</td>
                    <td className="px-3 py-3 text-right text-gray-300">{fmt_salary(p.salary)}</td>
                    <td className="px-3 py-3 text-right">
                      <span className={`font-semibold ${p.war >= 5 ? "text-green-400" : p.war >= 3 ? "text-yellow-400" : "text-gray-400"}`}>
                        {p.war.toFixed(1)}
                      </span>
                    </td>
                    <td className="px-3 py-3 text-right text-gray-300">{p.ops.toFixed(3)}</td>
                    <td className="px-3 py-3 text-right text-gray-400">{p.hr}</td>
                    <td className="px-3 py-3 text-right">
                      <span className="text-green-400 font-bold">{p.value_score.toFixed(3)}</span>
                    </td>
                    <td className="px-3 py-3">
                      <ValueBar score={p.value_score} max={maxScore} />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
