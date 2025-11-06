import React from 'react';
import { DollarSign, TrendingUp, AlertCircle, CheckCircle } from 'lucide-react';

interface CostEstimatorProps {
  estimatedCost: number;
  budgetLimit: number | null;
  numSlides: number;
  model: string;
}

const CostEstimator: React.FC<CostEstimatorProps> = ({
  estimatedCost,
  budgetLimit,
  numSlides,
  model
}) => {
  const withinBudget = budgetLimit === null || estimatedCost <= budgetLimit;
  const costPerSlide = estimatedCost / numSlides;

  return (
    <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-green-500 border-opacity-30">
      <div className="flex items-center space-x-2 mb-4">
        <DollarSign className="w-5 h-5 text-green-400" />
        <h3 className="font-bold">Cost Estimate</h3>
      </div>

      {/* Total Cost */}
      <div className="bg-gray-900 bg-opacity-50 rounded-lg p-4 mb-4">
        <div className="text-xs text-gray-400 mb-1">Estimated Total Cost</div>
        <div className="text-3xl font-bold text-green-300">
          ${estimatedCost.toFixed(4)}
        </div>
      </div>

      {/* Breakdown */}
      <div className="space-y-3 mb-4">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Per Slide</span>
          <span className="font-semibold">${costPerSlide.toFixed(4)}</span>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Model</span>
          <span className="font-semibold">{model}</span>
        </div>

        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Total Slides</span>
          <span className="font-semibold">{numSlides}</span>
        </div>

        {budgetLimit !== null && (
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-400">Budget Limit</span>
            <span className="font-semibold">${budgetLimit.toFixed(2)}</span>
          </div>
        )}
      </div>

      {/* Budget Status */}
      {budgetLimit !== null && (
        <div className={`rounded-lg p-3 ${
          withinBudget
            ? 'bg-green-900 bg-opacity-20 border border-green-600 border-opacity-30'
            : 'bg-red-900 bg-opacity-20 border border-red-600 border-opacity-30'
        }`}>
          <div className="flex items-center space-x-2">
            {withinBudget ? (
              <>
                <CheckCircle className="w-4 h-4 text-green-400" />
                <span className="text-sm text-green-300 font-semibold">Within Budget</span>
              </>
            ) : (
              <>
                <AlertCircle className="w-4 h-4 text-red-400" />
                <span className="text-sm text-red-300 font-semibold">Over Budget</span>
              </>
            )}
          </div>
          {!withinBudget && (
            <div className="text-xs text-red-300 mt-1">
              Reduce slides or switch to a cheaper model
            </div>
          )}
        </div>
      )}

      {/* Savings Tip */}
      {model !== 'gpt-3.5-turbo' && (
        <div className="mt-4 bg-blue-900 bg-opacity-20 border border-blue-600 border-opacity-30 rounded p-3">
          <div className="flex items-start space-x-2 text-xs text-blue-200">
            <TrendingUp className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <div>
              <div className="font-semibold mb-1">Save Money</div>
              <div className="text-blue-300 opacity-80">
                Switch to GPT-3.5 Turbo to reduce cost by ~50%
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CostEstimator;
