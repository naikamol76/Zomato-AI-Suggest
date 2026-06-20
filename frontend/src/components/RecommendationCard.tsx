import { Recommendation } from "../types/api";

interface RecommendationCardProps {
  item: Recommendation;
}

const cardImages = [
  "https://images.unsplash.com/photo-1544025162-d76694265947?w=800&auto=format&fit=crop&q=80", // Rank 1: Steak Mughlai Plating
  "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800&auto=format&fit=crop&q=80", // Rank 2: Seafood Continental Pizza
  "https://images.unsplash.com/photo-1482049016688-2d3e1b311543?w=800&auto=format&fit=crop&q=80", // Rank 3: Salads & Healthy Bowls
  "https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=800&auto=format&fit=crop&q=80", // Rank 4: Plated Fish
  "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=800&auto=format&fit=crop&q=80", // Rank 5: Pasta Dishes
];

export default function RecommendationCard({ item }: RecommendationCardProps) {
  const ratingClass = 
    item.rating >= 4.5 ? "rating-excellent" :
    item.rating >= 4.0 ? "rating-great" : "rating-good";

  const budgetIcon = 
    item.budget_band === "low" ? "₹" :
    item.budget_band === "medium" ? "₹₹" : "₹₹₹";

  const rankText = 
    item.rank === 1 ? "Rank #1 · Amber Premium" :
    item.rank === 2 ? "Rank #2 · Coastal Indigo" : `Rank #${item.rank} · Emerald Selection`;

  const cardImage = cardImages[(item.rank - 1) % cardImages.length];

  return (
    <div className="recommendation-card">
      {/* Visual Header Image Banner */}
      <div className="card-image-wrapper">
        <img 
          className="card-image" 
          src={cardImage} 
          alt={item.name} 
        />
        <div className="card-gradient-overlay" />
        
        {/* Header Overlay Overlay */}
        <div className="card-header-content">
          <div className="card-title-group">
            <span className="rank-badge">{rankText}</span>
            <h4 className="restaurant-name">{item.name}</h4>
            <p className="restaurant-locality">
              <span className="material-symbols-outlined">location_on</span>
              {item.locality || "Unknown Locality"}
            </p>
          </div>
          <div className={`card-rating-badge ${ratingClass}`}>
            {item.rating.toFixed(1)} ★
          </div>
        </div>
      </div>

      {/* Info Body */}
      <div className="card-info-body">
        {/* Cuisine Pills */}
        <div className="cuisines-tags">
          {item.cuisines.split(",").map((c) => (
            <span key={c.trim()} className="cuisine-tag">
              {c.trim()}
            </span>
          ))}
        </div>

        {/* Cost Information */}
        <div className="cost-row">
          {item.approx_cost_for_two !== null && (
            <span className="cost-value">
              ₹{item.approx_cost_for_two} for two (Approx.)
            </span>
          )}
          <span className="budget-band-badge" data-band={item.budget_band}>
            {budgetIcon} {item.budget_band.toUpperCase()}
          </span>
        </div>

        {/* Rationale block */}
        <div className="ai-explanation-box">
          <div className="ai-explanation-header">
            <span className="material-symbols-outlined">auto_awesome</span>
            <span>AI Suggestion Rationale</span>
          </div>
          <p className="ai-text">{item.explanation}</p>
        </div>
      </div>
    </div>
  );
}
