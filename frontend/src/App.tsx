import { useEffect, useState } from "react";
import "./App.css";
import { HealthResponse, RecommendRequest, RecommendResponse } from "./types/api";
import { fetchHealth, submitRecommendations } from "./api/client";
import PreferenceForm from "./components/PreferenceForm";
import RecommendationList from "./components/RecommendationList";

export default function App() {
  // App-level state
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [healthLoading, setHealthLoading] = useState(true);
  
  const [results, setResults] = useState<RecommendResponse | null>(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState<string | null>(null);

  // Check health on mount to verify backend is up
  useEffect(() => {
    async function checkHealth() {
      setHealthLoading(true);
      try {
        const healthStatus = await fetchHealth();
        setHealth(healthStatus);
      } catch {
        setHealth(null);
      } finally {
        setHealthLoading(false);
      }
    }
    checkHealth();
  }, []);

  function scrollToElement(id: string) {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }

  async function handleSearch(request: RecommendRequest) {
    setSearchLoading(true);
    setSearchError(null);
    setResults(null);
    
    try {
      const response = await submitRecommendations(request);
      setResults(response);
    } catch (err) {
      setSearchError(err instanceof Error ? err.message : "Recommendations fetch failed.");
    } finally {
      setSearchLoading(false);
    }
  }

  return (
    <div className="app-container">
      {/* Top App Bar Header */}
      <header className="app-header">
        <div className="logo-section">
          <span className="material-symbols-outlined logo-icon">blur_on</span>
          <h1>
            Zomato AI Suggest <span className="header-accent">✦</span>
          </h1>
        </div>
        
        {/* Health Status Indicator */}
        <div className="health-status-indicator">
          {healthLoading ? (
            <span className="status-badge checking">Ping Backend...</span>
          ) : (health?.status === "healthy" || health?.status === "ok") ? (
            <span className="status-badge online">System Connected</span>
          ) : (
            <span className="status-badge offline">Backend Offline</span>
          )}
        </div>
      </header>

      {/* Side Navigation (Desktop Only) */}
      <aside className="app-sidebar">
        <div className="sidebar-title">Preferences</div>
        <nav className="sidebar-nav">
          <button className="sidebar-btn" onClick={() => scrollToElement("city-select-group")}>
            <span className="material-symbols-outlined">location_on</span>
            <span>Location</span>
          </button>
          <button className="sidebar-btn" onClick={() => scrollToElement("cuisine-select-group")}>
            <span className="material-symbols-outlined">restaurant</span>
            <span>Cuisine</span>
          </button>
          <button className="sidebar-btn" onClick={() => scrollToElement("budget-select-group")}>
            <span className="material-symbols-outlined">payments</span>
            <span>Budget</span>
          </button>
          <button className="sidebar-btn" onClick={() => scrollToElement("rating-select-group")}>
            <span className="material-symbols-outlined">star</span>
            <span>Ratings</span>
          </button>
        </nav>
      </aside>

      {/* Main Workspace Layout */}
      <main className="app-main-layout">
        <div className="main-content-container">
          
          {/* Intro State Canvas */}
          {!searchLoading && !searchError && !results && (
            <section className="intro-placeholder">
              <div className="intro-icon-box">
                <span className="material-symbols-outlined intro-icon">flare</span>
              </div>
              <h2>Tailor your cravings</h2>
              <p>
                Our advanced LLM analyzes thousands of menu items, reviews, and kitchen performance 
                metrics to suggest your perfect meal. Configure your options below to begin.
              </p>
            </section>
          )}

          {/* Configuration Form */}
          <PreferenceForm onSubmit={handleSearch} isLoading={searchLoading} />

          {/* Viewport for Errors, Skeletons, and Results */}
          <section className="recommendations-viewport">
            {searchError && (
              <div className="error-banner">
                <span className="material-symbols-outlined error-icon">warning</span>
                <div className="error-details">
                  <h4>Recommendation Engine Failure</h4>
                  <p>{searchError}</p>
                </div>
              </div>
            )}

            {searchLoading && (
              <div className="loading-skeleton-container">
                <div className="skeleton-title shimmer-bg" />
                <div className="skeleton-stats shimmer-bg" style={{ marginTop: '16px' }} />
                <div className="skeleton-grid" style={{ marginTop: '24px' }}>
                  {[1, 2].map((i) => (
                    <div key={i} className="skeleton-card">
                      <div className="skeleton-image shimmer-bg" />
                      <div className="skeleton-body">
                        <div className="skeleton-line title shimmer-bg" />
                        <div className="skeleton-line text-1 shimmer-bg" />
                        <div className="skeleton-line text-2 shimmer-bg" />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {!searchLoading && !searchError && results && (
              <RecommendationList
                items={results.recommendations}
                message={results.message}
                meta={results.meta}
              />
            )}
          </section>

        </div>
      </main>

      {/* Bottom Navigation (Mobile Only) */}
      <nav className="mobile-nav">
        <button className="mobile-btn active">
          <span className="material-symbols-outlined">explore</span>
          <span>Discover</span>
        </button>
        <button className="mobile-btn" onClick={() => scrollToElement("city-select-group")}>
          <span className="material-symbols-outlined">location_on</span>
          <span>Filters</span>
        </button>
        <button className="mobile-btn" onClick={() => scrollToElement("notes-textarea-group")}>
          <span className="material-symbols-outlined">history</span>
          <span>Notes</span>
        </button>
      </nav>
    </div>
  );
}
