import { useEffect, useState, useCallback } from "react";
import { Search, ChevronUp, ChevronDown } from "lucide-react";
import { api } from "../services/api";
import type { Player, SortField, SortDir } from "../types/player";
import PlayerTable from "../components/PlayerTable";
import LoadingSpinner from "../components/LoadingSpinner";
import ErrorBanner from "../components/ErrorBanner";

const SORT_FIELDS: { value: SortField; label: string }[] = [
  { value: "war", label: "WAR" },
  { value: "salary", label: "Salary" },
  { value: "ops", label: "OPS" },
  { value: "age", label: "Age" },
  { value: "hr", label: "HR" },
  { value: "rbi", label: "RBI" },
];

export default function PlayerBrowser() {
  const [players, setPlayers] = useState<Player[]>([]);
  const [teams, setTeams] = useState<string[]>([]);
  const [positions, setPositions] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState("");
  const [position, setPosition] = useState("");
  const [team, setTeam] = useState("");
  const [sortBy, setSortBy] = useState<SortField>("war");
  const [sortDir, setSortDir] = useState<SortDir>("desc");

  const fetchPlayers = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.players({
        search: search || undefined,
        position: position || undefined,
        team: team || undefined,
        sort_by: sortBy,
        sort_dir: sortDir,
        limit: 200,
      });
      setPlayers(data);
    } catch (e: any) {
      setError(e.message ?? "Failed to fetch players");
    } finally {
      setLoading(false);
    }
  }, [search, position, team, sortBy, sortDir]);

  useEffect(() => {
    Promise.all([api.teams(), api.positions()])
      .then(([t, p]) => {
        setTeams(t.teams);
        setPositions(p.positions);
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    fetchPlayers();
  }, [fetchPlayers]);

  const toggleSort = (field: SortField) => {
    if (sortBy === field) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortBy(field);
      setSortDir("desc");
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Player Browser</h2>
        <p className="text-gray-500 mt-1 text-sm">
          {players.length} players — search, filter, and sort.
        </p>
      </div>

      <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
        <div className="flex flex-wrap gap-3 items-end">
          <div className="flex-1 min-w-48">
            <label className="block text-xs text-gray-500 mb-1.5">Search Player</label>
            <div className="relative">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
              <input
                type="text"
                placeholder="e.g. Aaron Judge"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg pl-9 pr-3 py-2 text-sm text-white placeholder-gray-600 focus:outline-none focus:border-green-500 transition-colors"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs text-gray-500 mb-1.5">Position</label>
            <select
              value={position}
              onChange={(e) => setPosition(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-green-500 transition-colors"
            >
              <option value="">All Positions</option>
              {positions.map((p) => (
                <option key={p} value={p}>{p}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs text-gray-500 mb-1.5">Team</label>
            <select
              value={team}
              onChange={(e) => setTeam(e.target.value)}
              className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white focus:outline-none focus:border-green-500 transition-colors"
            >
              <option value="">All Teams</option>
              {teams.map((t) => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-xs text-gray-500 mb-1.5">Sort By</label>
            <div className="flex gap-1">
              {SORT_FIELDS.map((f) => (
                <button
                  key={f.value}
                  onClick={() => toggleSort(f.value)}
                  className={`flex items-center gap-1 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                    sortBy === f.value
                      ? "bg-green-500 text-gray-950"
                      : "bg-gray-800 text-gray-400 hover:bg-gray-700"
                  }`}
                >
                  {f.label}
                  {sortBy === f.value && (
                    sortDir === "desc" ? <ChevronDown size={12} /> : <ChevronUp size={12} />
                  )}
                </button>
              ))}
            </div>
          </div>

          {(search || position || team) && (
            <button
              onClick={() => { setSearch(""); setPosition(""); setTeam(""); }}
              className="px-3 py-2 rounded-lg text-xs text-gray-400 hover:text-white border border-gray-700 hover:border-gray-500 transition-colors"
            >
              Clear filters
            </button>
          )}
        </div>
      </div>

      {error && <ErrorBanner message={error} />}
      {loading ? (
        <LoadingSpinner message="Loading players..." />
      ) : (
        <PlayerTable players={players} />
      )}
    </div>
  );
}
