import React from 'react';
import { FileText, ChevronRight } from 'lucide-react';

interface OutlinePreviewProps {
  outline: {
    title: string;
    slides: Array<{
      title: string;
      bullets: string[];
    }>;
  };
}

const OutlinePreview: React.FC<OutlinePreviewProps> = ({ outline }) => {
  return (
    <div className="bg-black bg-opacity-40 backdrop-blur-md rounded-xl p-6 border border-blue-500 border-opacity-30">
      <div className="flex items-center space-x-2 mb-4">
        <FileText className="w-5 h-5 text-blue-400" />
        <h3 className="font-bold">Presentation Outline</h3>
      </div>

      {/* Title */}
      <div className="bg-blue-900 bg-opacity-20 rounded-lg p-4 mb-4">
        <div className="text-lg font-bold text-blue-200">{outline.title}</div>
        <div className="text-xs text-gray-400 mt-1">{outline.slides.length} slides</div>
      </div>

      {/* Slides */}
      <div className="space-y-3 max-h-[600px] overflow-y-auto custom-scrollbar">
        {outline.slides.map((slide, idx) => (
          <div
            key={idx}
            className="bg-gray-900 bg-opacity-50 rounded-lg p-4 hover:bg-gray-800 transition"
          >
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-blue-600 bg-opacity-30 rounded flex items-center justify-center flex-shrink-0 font-bold text-sm">
                {idx + 1}
              </div>

              <div className="flex-1">
                <div className="font-semibold text-sm mb-2">{slide.title}</div>
                <ul className="space-y-1">
                  {slide.bullets.map((bullet, bidx) => (
                    <li key={bidx} className="text-xs text-gray-400 flex items-start space-x-2">
                      <ChevronRight className="w-3 h-3 mt-0.5 flex-shrink-0 text-blue-400" />
                      <span>{bullet}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Actions */}
      <div className="mt-4 pt-4 border-t border-gray-700">
        <button className="w-full py-2 bg-blue-600 hover:bg-blue-500 rounded-lg transition text-sm">
          Looks Good - Generate Presentation
        </button>
      </div>
    </div>
  );
};

export default OutlinePreview;
