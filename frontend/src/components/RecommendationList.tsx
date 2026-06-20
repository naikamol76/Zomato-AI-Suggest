import { Recommendation, ResponseMeta } from "../types/api";
import RecommendationCard from "./RecommendationCard";

interface RecommendationListProps {
  items: Recommendation[];
  message: string | null;
  meta: ResponseMeta | null;
}

export default function RecommendationList({ items, message, meta }: RecommendationListProps) {
  if (items.length === 0) {
    return (
      <div className="empty-state-container">
        <span className="material-symbols-outlined empty-state-icon">no_food</span>
        <h3>No Suggestions Found</h3>
        <p className="empty-state-message">
          {message || "We couldn't find any restaurants matching your strict criteria. Try relaxing your filters."}
        </p>
      </div>
    );
  }

  return (
    <div className="recommendations-container">
      <div className="recommendations-header">
        <h3 className="section-label">AI Suggestions For You</h3>
        {message && <p className="success-message">{message}</p>}
      </div>

      {/* Meta Statistics Panel */}
      {meta && (
        <div className="meta-stats-panel">
          <div className="meta-stats-flex">
            <div className="meta-badges-row">
              <div className="meta-badge candidates">
                {meta.candidates_considered} Candidates Considered
              </div>
              <div className="meta-badge model">
                {meta.model}
              </div>
              <div className="meta-badge model" style={{ backgroundColor: 'rgba(255, 185, 95, 0.1)', color: 'var(--accent-warning)', border: '1px solid rgba(255, 185, 95, 0.2)' }}>
                Prompt: {meta.prompt_version}
              </div>
            </div>
            <span className="material-symbols-outlined meta-history-icon">history</span>
          </div>
          {meta.summary && (
            <div className="meta-summary-box">
              <p className="summary-content">
                "{meta.summary}"
              </p>
            </div>
          )}
        </div>
      )}

      {/* Grid of Cards */}
      <div className="recommendations-grid">
        {items.map((item) => (
          <RecommendationCard key={item.restaurant_id} item={item} />
        ))}
      </div>
    </div>
  );
}
