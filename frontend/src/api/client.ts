import { HealthResponse, RecommendRequest, RecommendResponse } from "../types/api";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function fetchHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/api/v1/health`);
  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`);
  }
  return response.json() as Promise<HealthResponse>;
}

export async function fetchCities(): Promise<string[]> {
  const response = await fetch(`${API_BASE}/api/v1/metadata/cities`);
  if (!response.ok) {
    throw new Error(`Failed to fetch cities list: ${response.statusText}`);
  }
  const data = (await response.json()) as { cities: string[] };
  return data.cities;
}

export async function fetchCuisines(city?: string): Promise<string[]> {
  const url = city 
    ? `${API_BASE}/api/v1/metadata/cuisines?city=${encodeURIComponent(city)}`
    : `${API_BASE}/api/v1/metadata/cuisines`;
  
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch cuisines list: ${response.statusText}`);
  }
  const data = (await response.json()) as { cuisines: string[] };
  return data.cuisines;
}

export async function submitRecommendations(request: RecommendRequest): Promise<RecommendResponse> {
  const response = await fetch(`${API_BASE}/api/v1/recommendations`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    let errorDetail = "";
    try {
      const errJson = await response.json() as { detail?: string | Array<{ msg: string }> };
      if (errJson && errJson.detail) {
        if (typeof errJson.detail === "string") {
          errorDetail = errJson.detail;
        } else if (Array.isArray(errJson.detail)) {
          errorDetail = errJson.detail.map(d => d.msg).join(", ");
        }
      }
    } catch {
      // ignore
    }
    throw new Error(errorDetail || `Request failed with HTTP status ${response.status}`);
  }

  return response.json() as Promise<RecommendResponse>;
}
