import React, { useEffect, useState } from "react";
import { BudgetBand, RecommendRequest } from "../types/api";
import { fetchCities, fetchCuisines } from "../api/client";

interface PreferenceFormProps {
  onSubmit: (request: RecommendRequest) => void;
  isLoading: boolean;
}

export default function PreferenceForm({ onSubmit, isLoading }: PreferenceFormProps) {
  const [cities, setCities] = useState<string[]>([]);
  const [cuisines, setCuisines] = useState<string[]>([]);
  
  // Form fields state
  const [city, setCity] = useState("");
  const [budget, setBudget] = useState<BudgetBand>("medium");
  const [cuisine, setCuisine] = useState("");
  const [minRating, setMinRating] = useState(4.0);
  const [additionalNotes, setAdditionalNotes] = useState("");

  const [loadingMeta, setLoadingMeta] = useState(false);
  const [metaError, setMetaError] = useState<string | null>(null);

  // Load cities once on mount
  useEffect(() => {
    async function loadCities() {
      setLoadingMeta(true);
      setMetaError(null);
      try {
        const citiesList = await fetchCities();
        setCities(citiesList);
        if (citiesList.length > 0) {
          // Default to first city if available
          setCity(citiesList[0]);
        }
      } catch (err) {
        setMetaError("Failed to fetch cities list. Is backend running?");
      } finally {
        setLoadingMeta(false);
      }
    }
    loadCities();
  }, []);

  // Fetch cuisines whenever city changes
  useEffect(() => {
    if (!city) return;
    async function loadCuisines() {
      try {
        const cuisinesList = await fetchCuisines(city);
        setCuisines(cuisinesList);
        // Reset cuisine field or match it if available in list
        if (cuisinesList.length > 0) {
          setCuisine(cuisinesList[0]);
        } else {
          setCuisine("");
        }
      } catch {
        // Fallback or ignore quietly
      }
    }
    loadCuisines();
  }, [city]);

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!city || !cuisine) return;
    
    onSubmit({
      city,
      budget,
      cuisine,
      min_rating: minRating,
      additional_notes: additionalNotes.trim() || null,
    });
  }

  return (
    <form className="preference-form" onSubmit={handleSubmit}>
      <h3 className="section-label">Configure Engine</h3>
      
      {metaError && (
        <div className="error-banner">
          <span className="material-symbols-outlined error-icon">warning</span>
          <div className="error-details">
            <h4>Form Setup Alert</h4>
            <p>{metaError}</p>
          </div>
        </div>
      )}

      <div className="form-group-grid">
        {/* City Select */}
        <div className="form-field" id="city-select-group">
          <label htmlFor="city-select">Current City</label>
          <div className="select-wrapper">
            <select
              id="city-select"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              disabled={loadingMeta || isLoading}
            >
              {loadingMeta && <option>Loading cities...</option>}
              {cities.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
            <span className="material-symbols-outlined select-arrow">expand_more</span>
          </div>
        </div>

        {/* Cuisine Select */}
        <div className={`form-field ${cuisines.length === 0 ? "disabled" : ""}`} id="cuisine-select-group">
          <label htmlFor="cuisine-select">Cuisine Focus</label>
          <div className="select-wrapper">
            <select
              id="cuisine-select"
              value={cuisine}
              onChange={(e) => setCuisine(e.target.value)}
              disabled={isLoading || cuisines.length === 0}
            >
              {cuisines.length === 0 && <option>No cuisines available</option>}
              {cuisines.map((cuis) => (
                <option key={cuis} value={cuis}>
                  {cuis}
                </option>
              ))}
            </select>
            <span className="material-symbols-outlined select-arrow">expand_more</span>
          </div>
        </div>
      </div>

      {/* Budget Selector */}
      <div className="form-field" id="budget-select-group">
        <label>Budget Range</label>
        <div className="budget-selector">
          {(["low", "medium", "high"] as BudgetBand[]).map((band) => (
            <label
              key={band}
              className={`budget-card ${budget === band ? "active" : ""}`}
              data-band={band}
            >
              <input
                type="radio"
                name="budget"
                value={band}
                checked={budget === band}
                onChange={() => setBudget(band)}
                disabled={isLoading}
              />
              <span className="budget-symbol">
                {band === "low" && "₹"}
                {band === "medium" && "₹₹"}
                {band === "high" && "₹₹₹"}
              </span>
              <span className="budget-label">
                {band === "low" && "Budget"}
                {band === "medium" && "Mid-tier"}
                {band === "high" && "Premium"}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* Minimum Rating Slider */}
      <div className="form-field" id="rating-select-group">
        <div className="slider-header">
          <label htmlFor="rating-slider">Minimum Rating</label>
          <span className="rating-badge-value">{minRating.toFixed(1)} ★</span>
        </div>
        <div className="slider-container">
          <input
            id="rating-slider"
            type="range"
            min="0.0"
            max="4.9"
            step="0.1"
            value={minRating}
            onChange={(e) => setMinRating(parseFloat(e.target.value))}
            disabled={isLoading}
          />
          <div className="slider-labels">
            <span>0.0 ★</span>
            <span>3.0 ★</span>
            <span>4.0 ★</span>
            <span>4.9 ★</span>
          </div>
        </div>
      </div>

      {/* Additional context */}
      <div className="form-field" id="notes-textarea-group">
        <label htmlFor="notes-textarea">
          Additional Notes (Optional)
        </label>
        <div className="textarea-wrapper">
          <textarea
            id="notes-textarea"
            rows={3}
            placeholder="e.g. Roof-top seating preferred, vegan options required..."
            value={additionalNotes}
            onChange={(e) => setAdditionalNotes(e.target.value)}
            maxLength={500}
            disabled={isLoading}
          />
          <div className="textarea-footer">
            <span>Max 500 characters</span>
            <span>{additionalNotes.length}/500</span>
          </div>
        </div>
      </div>

      <button
        type="submit"
        className="submit-btn"
        disabled={isLoading || !city || !cuisine}
      >
        {isLoading ? (
          <div className="spinner-loader">
            <span className="material-symbols-outlined spinner-icon">refresh</span>
            <span>Analyzing Catalog...</span>
          </div>
        ) : (
          <>
            <span className="material-symbols-outlined">auto_awesome</span>
            <span>Get Recommendations</span>
          </>
        )}
      </button>
    </form>
  );
}
