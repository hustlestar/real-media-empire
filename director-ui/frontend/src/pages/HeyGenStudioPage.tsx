/**
 * HeyGen Studio Page
 *
 * Main page wrapper for the HeyGen Avatar Studio component.
 * Provides the full-screen interface for AI avatar video generation.
 */

import React from 'react';
import AvatarStudio from '../components/heygen/AvatarStudio';

export default function HeyGenStudioPage() {
  return (
    <div className="h-full">
      <AvatarStudio />
    </div>
  );
}
