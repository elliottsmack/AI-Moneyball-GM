export interface Player {
  player_id: number;
  name: string;
  age: number;
  team: string;
  position: string;
  salary: number;
  war: number;
  ops: number;
  obp: number;
  slg: number;
  hr: number;
  rbi: number;
  stolen_bases: number;
  mlb_id?: number | null;
  data_source?: string | null;
  season?: number | null;
  games_played?: number | null;
  batting_avg?: number | null;
  last_synced?: string | null;
}

export interface PlayerWithScore extends Player {
  value_score: number;
}

export interface HealthStats {
  total: number;
  avg_salary: number;
  avg_war: number;
  avg_ops: number;
}

export interface HealthResponse {
  status: string;
  database: string;
  timestamp: string;
  stats: HealthStats;
}

export interface SyncStatus {
  data_source: "live" | "mock";
  season: number | null;
  player_count: number;
  live_count: number;
  mock_count: number;
  last_synced: string | null;
  is_syncing: boolean;
  last_sync_result: Record<string, unknown> | null;
}

export interface SyncResult {
  status: "complete" | "error" | "already_running";
  source?: string;
  season?: number;
  created?: number;
  cleared_mock?: number;
  war_matched?: number;
  salary_matched?: number;
  synced_at?: string;
  message?: string;
  error?: string;
}

export type SortField = "war" | "salary" | "ops" | "age" | "hr" | "rbi";
export type SortDir = "asc" | "desc";
