import axios from "axios";
import type { Player, PlayerWithScore, HealthResponse } from "../types/player";

const client = axios.create({ baseURL: "/api" });

export interface PlayerQuery {
  search?: string;
  position?: string;
  team?: string;
  sort_by?: string;
  sort_dir?: string;
  limit?: number;
  skip?: number;
}

export const api = {
  health: (): Promise<HealthResponse> =>
    client.get<HealthResponse>("/health").then((r) => r.data),

  players: (params: PlayerQuery = {}): Promise<Player[]> =>
    client.get<Player[]>("/players", { params }).then((r) => r.data),

  player: (id: number): Promise<Player> =>
    client.get<Player>(`/players/${id}`).then((r) => r.data),

  undervalued: (top_n = 20): Promise<PlayerWithScore[]> =>
    client.get<PlayerWithScore[]>("/players/undervalued", { params: { top_n } }).then((r) => r.data),

  teams: (): Promise<{ teams: string[] }> =>
    client.get<{ teams: string[] }>("/teams").then((r) => r.data),

  positions: (): Promise<{ positions: string[] }> =>
    client.get<{ positions: string[] }>("/teams/positions").then((r) => r.data),
};
