import { useState } from "react";
import { BarChart2, Users, Star, Activity } from "lucide-react";
import Dashboard from "./pages/Dashboard";
import PlayerBrowser from "./pages/PlayerBrowser";
import Undervalued from "./pages/Undervalued";

type Tab = "dashboard" | "players" | "undervalued";

const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
  { id: "dashboard", label: "Dashboard", icon: <BarChart2 size={16} /> },
  { id: "players", label: "Player Browser", icon: <Users size={16} /> },
  { id: "undervalued", label: "Undervalued", icon: <Star size={16} /> },
];

export default function App() {
  const [active, setActive] = useState<Tab>("dashboard");

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100 font-sans">
      <header className="bg-gray-900 border-b border-gray-800 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-green-500 flex items-center justify-center shadow-lg shadow-green-500/20">
              <Activity size={20} className="text-gray-950" />
            </div>
            <div>
              <h1 className="text-white font-bold text-lg leading-none tracking-tight">
                AI Moneyball GM
              </h1>
              <p className="text-gray-500 text-xs mt-0.5">Baseball Analytics Engine</p>
            </div>
          </div>
          <nav className="flex gap-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActive(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  active === tab.id
                    ? "bg-green-500 text-gray-950"
                    : "text-gray-400 hover:text-white hover:bg-gray-800"
                }`}
              >
                {tab.icon}
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {active === "dashboard" && <Dashboard />}
        {active === "players" && <PlayerBrowser />}
        {active === "undervalued" && <Undervalued />}
      </main>

      <footer className="border-t border-gray-800 mt-16 py-6 text-center text-gray-600 text-sm">
        AI Moneyball GM — Phase 1 &middot; Data Pipeline &amp; Player Browser
      </footer>
    </div>
  );
}
