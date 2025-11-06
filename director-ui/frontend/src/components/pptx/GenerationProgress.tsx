import React from 'react';
import { Loader, CheckCircle } from 'lucide-react';

interface GenerationProgressProps {
  progress: number;
  stage: string;
}

const stages = [
  { name: 'Initializing', min: 0, max: 10 },
  { name: 'Fetching content', min: 10, max: 30 },
  { name: 'Generating outline', min: 30, max: 50 },
  { name: 'Creating slides', min: 50, max: 80 },
  { name: 'Formatting', min: 80, max: 95 },
  { name: 'Finalizing', min: 95, max: 100 }
];

const GenerationProgress: React.FC<GenerationProgressProps> = ({ progress, stage }) => {
  const currentStageIndex = stages.findIndex(s => progress >= s.min && progress < s.max);
  const currentStage = stages[currentStageIndex] || stages[stages.length - 1];

  return (
    <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-blue-500 border-opacity-30">
      <div className="text-center mb-6">
        <div className="w-16 h-16 bg-blue-500 bg-opacity-20 rounded-full flex items-center justify-center mx-auto mb-4">
          <Loader className="w-8 h-8 text-blue-400 animate-spin" />
        </div>

        <h3 className="text-xl font-bold mb-2">Generating Presentation</h3>
        <p className="text-sm text-gray-400">{stage || currentStage.name}</p>
      </div>

      {/* Progress Bar */}
      <div className="mb-6">
        <div className="w-full h-3 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
        <div className="text-center text-sm font-semibold text-blue-300 mt-2">
          {progress}%
        </div>
      </div>

      {/* Stage Indicators */}
      <div className="space-y-2">
        {stages.map((stg, idx) => {
          const isCompleted = progress > stg.max;
          const isCurrent = progress >= stg.min && progress < stg.max;
          const isPending = progress < stg.min;

          return (
            <div
              key={idx}
              className={`flex items-center space-x-3 p-2 rounded transition ${
                isCurrent ? 'bg-blue-900 bg-opacity-20' : ''
              }`}
            >
              <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                isCompleted ? 'bg-green-500 bg-opacity-30' :
                isCurrent ? 'bg-blue-500 bg-opacity-30' :
                'bg-gray-700'
              }`}>
                {isCompleted ? (
                  <CheckCircle className="w-4 h-4 text-green-400" />
                ) : (
                  <span className={`text-xs ${
                    isCurrent ? 'text-blue-300' : 'text-gray-500'
                  }`}>
                    {idx + 1}
                  </span>
                )}
              </div>

              <span className={`text-sm ${
                isCompleted ? 'text-green-300 line-through' :
                isCurrent ? 'text-blue-300 font-semibold' :
                'text-gray-500'
              }`}>
                {stg.name}
              </span>

              {isCurrent && (
                <div className="ml-auto">
                  <div className="w-5 h-5 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Estimated Time */}
      <div className="mt-6 text-center text-xs text-gray-400">
        <div>Estimated time: 30-60 seconds</div>
        <div className="mt-1">Please don't close this window</div>
      </div>
    </div>
  );
};

export default GenerationProgress;
