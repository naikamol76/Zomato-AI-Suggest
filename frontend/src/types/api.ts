export type BudgetBand = "low" | "medium" | "high";

export interface Restaurant {
  restaurant_id: string;
  name: string;
  city: string;
  locality: string | null;
  cuisines: string;
  rating: number;
  votes: number;
  approx_cost_for_two: number | null;
  budget_band: BudgetBand;
}

export interface RecommendRequest {
  city: string;
  budget: BudgetBand;
  cuisine: string;
  min_rating: number;
  additional_notes?: string | null;
}

export interface Recommendation {
  rank: number;
  restaurant_id: string;
  name: string;
  cuisines: string;
  rating: number;
  approx_cost_for_two: number | null;
  budget_band: BudgetBand;
  locality: string | null;
  explanation: string;
}

export interface ResponseMeta {
  candidates_considered: number;
  prompt_version: string;
  model: string;
  summary: string | null;
}

export interface RecommendResponse {
  recommendations: Recommendation[];
  message: string | null;
  meta: ResponseMeta | null;
}

export interface HealthResponse {
  status: string;
  data_loaded: boolean;
  message?: string;
}
