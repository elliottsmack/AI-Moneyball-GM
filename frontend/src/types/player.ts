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

export type SortField = "war" | "salary" | "ops" | "age" | "hr" | "rbi";
export type SortDir = "asc" | "desc";
