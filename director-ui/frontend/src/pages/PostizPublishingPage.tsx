/**
 * Postiz Publishing Page
 *
 * Main page wrapper for the multi-platform social media publishing hub.
 */

import React from 'react';
import PublishingHub from '../components/publishing/PublishingHub';

export default function PostizPublishingPage() {
  return (
    <div className="h-full">
      <PublishingHub />
    </div>
  );
}
