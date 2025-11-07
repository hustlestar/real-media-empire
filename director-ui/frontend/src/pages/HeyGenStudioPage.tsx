/**
 * Avatar Studio Page (HeyGen & VEED.io)
 *
 * Main page wrapper for AI avatar video generation.
 * Supports both HeyGen (professional avatars) and VEED.io (photo-to-talking-avatar).
 */

import React from 'react';
import AvatarProviderSelector from '../components/heygen/AvatarProviderSelector';

export default function HeyGenStudioPage() {
  return (
    <div className="h-full">
      <AvatarProviderSelector />
    </div>
  );
}
