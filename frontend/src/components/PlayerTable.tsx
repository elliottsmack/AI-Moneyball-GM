import type { Player } from "../types/player";

function fmt_salary(v: number) {
  if (v >= 1_000_000) return `$${(v / 1_000_000).toFixed(1)}M`;
  return `$${v.toLocaleString()}`;
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
  SP: "bg-indigo-500/20 text-indigo-300",
  RP: "bg-violet-500/20 text-violet-300",
};

interface Props {
  players: Player[];
  extraCol?: { header: string; render: (p: Player) => React.ReactNode };
}

export default function PlayerTable({ players, extraCol }: Props) {
  if (players.length === 0) {
    return (
      <div className="text-center py-16 text-gray-500">
        No players found.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl border border-gray-800">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-gray-900 border-b border-gray-800 text-gray-400 text-xs uppercase tracking-wider">
            <th className="text-left px-4 py-3">Player</th>
            <th className="text-center px-3 py-3">Pos</th>
            <th className="text-left px-3 py-3">Team</th>
            <th className="text-right px-3 py-3">Age</th>
            <th className="text-right px-3 py-3">Salary</th>
            <th className="text-right px-3 py-3">WAR</th>
            <th className="text-right px-3 py-3">OPS</th>
            <th className="text-right px-3 py-3">OBP</th>
            <th className="text-right px-3 py-3">SLG</th>
            <th className="text-right px-3 py-3">HR</th>
            <th className="text-right px-3 py-3">RBI</th>
            <th className="text-right px-3 py-3">SB</th>
            {extraCol && <th className="text-right px-3 py-3">{extraCol.header}</th>}
          </tr>
        </thead>
        <tbody>
          {players.map((p, i) => {
            const posCls = POSITION_COLORS[p.position] ?? "bg-gray-700/30 text-gray-300";
            return (
              <tr
                key={p.player_id}
                className={`border-b border-gray-800/50 hover:bg-gray-800/40 transition-colors ${
                  i % 2 === 0 ? "bg-gray-900/20" : ""
                }`}
              >
                <td className="px-4 py-3 font-medium text-white whitespace-nowrap">{p.name}</td>
                <td className="px-3 py-3 text-center">
                  <span className={`px-2 py-0.5 rounded text-xs font-semibold ${posCls}`}>
                    {p.position}
                  </span>
                </td>
                <td className="px-3 py-3 text-gray-300 font-mono text-xs">{p.team}</td>
                <td className="px-3 py-3 text-right text-gray-400">{p.age}</td>
                <td className="px-3 py-3 text-right text-gray-300">{fmt_salary(p.salary)}</td>
                <td className="px-3 py-3 text-right">
                  <span className={`font-semibold ${p.war >= 5 ? "text-green-400" : p.war >= 3 ? "text-yellow-400" : "text-gray-400"}`}>
                    {p.war.toFixed(1)}
                  </span>
                </td>
                <td className="px-3 py-3 text-right text-gray-300">{p.ops.toFixed(3)}</td>
                <td className="px-3 py-3 text-right text-gray-400">{p.obp.toFixed(3)}</td>
                <td className="px-3 py-3 text-right text-gray-400">{p.slg.toFixed(3)}</td>
                <td className="px-3 py-3 text-right text-gray-400">{p.hr}</td>
                <td className="px-3 py-3 text-right text-gray-400">{p.rbi}</td>
                <td className="px-3 py-3 text-right text-gray-400">{p.stolen_bases}</td>
                {extraCol && (
                  <td className="px-3 py-3 text-right">{extraCol.render(p)}</td>
                )}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
