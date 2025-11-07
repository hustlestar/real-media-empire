/**
 * Avatar Provider Selector - Choose between HeyGen and VEED.io
 *
 * Allows users to switch between different avatar video generation providers
 */

import React, { useState } from 'react';
import { Sparkles, Image as ImageIcon } from 'lucide-react';
import AvatarStudio from './AvatarStudio';
import VeedTalkingAvatar from './VeedTalkingAvatar';

type Provider = 'heygen' | 'veed';

const PROVIDERS = {
  heygen: {
    name: 'HeyGen',
    icon: Sparkles,
    description: 'Professional AI avatars with full customization',
    features: [
      'Wide selection of avatars',
      'Custom voices and languages',
      'Background customization',
      'Advanced settings'
    ],
    color: 'blue'
  },
  veed: {
    name: 'VEED.io',
    icon: ImageIcon,
    description: 'Turn any photo into a talking avatar',
    features: [
      'Use your own photos',
      'Automatic lip-sync',
      'Fast generation',
      'Cost-effective'
    ],
    color: 'purple'
  }
};

export default function AvatarProviderSelector() {
  const [selectedProvider, setSelectedProvider] = useState<Provider>('heygen');

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold mb-2">Avatar Video Studio</h1>
        <p className="text-gray-600">
          Create AI-powered avatar videos for your content
        </p>
      </div>

      {/* Provider Selection */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">Choose Provider</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {(Object.keys(PROVIDERS) as Provider[]).map((providerKey) => {
            const provider = PROVIDERS[providerKey];
            const Icon = provider.icon;
            const isSelected = selectedProvider === providerKey;

            return (
              <button
                key={providerKey}
                onClick={() => setSelectedProvider(providerKey)}
                className={`p-6 border-2 rounded-lg text-left transition-all ${
                  isSelected
                    ? `border-${provider.color}-600 bg-${provider.color}-50 shadow-md`
                    : 'border-gray-200 hover:border-gray-300 hover:shadow'
                }`}
              >
                <div className="flex items-start gap-4">
                  <div
                    className={`p-3 rounded-lg ${
                      isSelected
                        ? `bg-${provider.color}-600 text-white`
                        : `bg-${provider.color}-100 text-${provider.color}-600`
                    }`}
                  >
                    <Icon className="w-6 h-6" />
                  </div>

                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-bold text-lg">{provider.name}</h3>
                      {isSelected && (
                        <span
                          className={`px-2 py-0.5 bg-${provider.color}-600 text-white text-xs rounded-full`}
                        >
                          Selected
                        </span>
                      )}
                    </div>

                    <p className="text-sm text-gray-600 mb-3">{provider.description}</p>

                    <ul className="space-y-1">
                      {provider.features.map((feature, idx) => (
                        <li key={idx} className="flex items-center gap-2 text-sm text-gray-700">
                          <div className={`w-1.5 h-1.5 rounded-full bg-${provider.color}-600`}></div>
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Provider Component */}
      <div>
        {selectedProvider === 'heygen' && <AvatarStudio />}
        {selectedProvider === 'veed' && <VeedTalkingAvatar />}
      </div>
    </div>
  );
}
