/**
 * V4.0: ReviewCard Component
 * Displays individual restaurant reviews with star ratings
 */
import React from 'react';
import { Star, StarHalf, CheckCircle } from 'lucide-react';

const ReviewCard = ({ review }) => {
  const { username, rating, comment, review_date, is_verified_purchase, helpful_count } = review;

  // Render star rating
  const renderStars = (rating) => {
    const stars = [];
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 !== 0;

    for (let i = 0; i < fullStars; i++) {
      stars.push(
        <Star
          key={`full-${i}`}
          className="w-4 h-4 fill-yellow-400 text-yellow-400"
        />
      );
    }

    if (hasHalfStar) {
      stars.push(
        <StarHalf
          key="half"
          className="w-4 h-4 fill-yellow-400 text-yellow-400"
        />
      );
    }

    // Fill remaining with empty stars
    const remaining = 5 - Math.ceil(rating);
    for (let i = 0; i < remaining; i++) {
      stars.push(
        <Star
          key={`empty-${i}`}
          className="w-4 h-4 text-gray-300"
        />
      );
    }

    return stars;
  };

  // Format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4 shadow-sm hover:shadow-md transition-shadow duration-200 mb-3">
      {/* Header with username and verified badge */}
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-orange-400 to-red-400 flex items-center justify-center text-white font-semibold text-sm">
            {username.charAt(0).toUpperCase()}
          </div>
          <span className="font-semibold text-gray-800">{username}</span>
          {is_verified_purchase && (
            <div className="flex items-center gap-1 bg-green-50 px-2 py-0.5 rounded-full">
              <CheckCircle className="w-3 h-3 text-green-600" />
              <span className="text-xs text-green-700 font-medium">Verified</span>
            </div>
          )}
        </div>
        <span className="text-xs text-gray-500">{formatDate(review_date)}</span>
      </div>

      {/* Star Rating */}
      <div className="flex items-center gap-1 mb-2">
        {renderStars(rating)}
        <span className="ml-1 text-sm font-medium text-gray-700">
          {rating.toFixed(1)}
        </span>
      </div>

      {/* Review Comment */}
      <p className="text-gray-700 text-sm leading-relaxed mb-2">
        "{comment}"
      </p>

      {/* Footer with helpful count */}
      {helpful_count > 0 && (
        <div className="flex items-center gap-1 text-xs text-gray-500">
          <span>👍 {helpful_count} people found this helpful</span>
        </div>
      )}
    </div>
  );
};

export default ReviewCard;
