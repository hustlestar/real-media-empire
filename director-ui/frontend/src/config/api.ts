/**
 * API configuration
 *
 * This file centralizes API configuration to make it easy to change
 * the backend URL for different environments.
 */

// Get API base URL from environment variable or use default
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export { API_BASE_URL };

// Helper function to construct API URLs
export function apiUrl(path: string): string {
  // Ensure path starts with /
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
}
