import React, { useState, useRef, useEffect } from 'react';
import { GitBranch, Maximize2, Minimize2, ZoomIn, ZoomOut, Locate, Eye, Download, Trash2, Copy, Star } from 'lucide-react';

export interface AssetNode {
  id: string;
  type: 'original' | 'version' | 'variant' | 'refinement' | 'composite';
  title: string;
  thumbnailUrl?: string;
  metadata: {
    createdAt: Date;
    prompt?: string;
    changes?: string;
    status?: 'approved' | 'rejected' | 'pending' | 'archived';
  };
  parentId?: string;
  children?: AssetNode[];
  position?: { x: number; y: number };
}

export interface LineageData {
  rootNode: AssetNode;
  totalNodes: number;
  totalBranches: number;
  maxDepth: number;
}

interface LineageViewerProps {
  data?: LineageData;
  onNodeSelect?: (node: AssetNode) => void;
  onNodeView?: (node: AssetNode) => void;
  onNodeDownload?: (node: AssetNode) => void;
  onNodeDelete?: (nodeId: string) => void;
  onNodeDuplicate?: (node: AssetNode) => void;
  onNodeApprove?: (nodeId: string) => void;
}

const LineageViewer: React.FC<LineageViewerProps> = ({
  data,
  onNodeSelect,
  onNodeView,
  onNodeDownload,
  onNodeDelete,
  onNodeDuplicate,
  onNodeApprove
}) => {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [showMinimap, setShowMinimap] = useState(true);
  const [layoutMode, setLayoutMode] = useState<'tree' | 'radial' | 'timeline'>('tree');

  const canvasRef = useRef<HTMLDivElement>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  // Layout constants
  const NODE_WIDTH = 200;
  const NODE_HEIGHT = 120;
  const HORIZONTAL_SPACING = 80;
  const VERTICAL_SPACING = 60;

  // Calculate node positions based on layout mode
  const calculateNodePositions = (node: AssetNode, depth = 0, index = 0, parentPos?: { x: number; y: number }): AssetNode => {
    const nodeWithPosition = { ...node };

    if (layoutMode === 'tree') {
      // Tree layout: horizontal expansion
      const x = depth * (NODE_WIDTH + HORIZONTAL_SPACING) + 50;
      const y = index * (NODE_HEIGHT + VERTICAL_SPACING) + 50;
      nodeWithPosition.position = { x, y };

      if (node.children && node.children.length > 0) {
        let childIndex = 0;
        nodeWithPosition.children = node.children.map(child => {
          const positioned = calculateNodePositions(child, depth + 1, childIndex, nodeWithPosition.position);
          childIndex += countNodes(child);
          return positioned;
        });
      }
    } else if (layoutMode === 'radial') {
      // Radial layout: circular arrangement
      const radius = depth * 200 + 100;
      const angleStep = (2 * Math.PI) / Math.max(1, node.children?.length || 1);
      const angle = index * angleStep;

      if (depth === 0) {
        nodeWithPosition.position = { x: 500, y: 400 };
      } else if (parentPos) {
        nodeWithPosition.position = {
          x: parentPos.x + radius * Math.cos(angle),
          y: parentPos.y + radius * Math.sin(angle)
        };
      }

      if (node.children && node.children.length > 0) {
        nodeWithPosition.children = node.children.map((child, idx) =>
          calculateNodePositions(child, depth + 1, idx, nodeWithPosition.position)
        );
      }
    } else if (layoutMode === 'timeline') {
      // Timeline layout: chronological left-to-right
      const x = index * (NODE_WIDTH + HORIZONTAL_SPACING) + 50;
      const y = depth * (NODE_HEIGHT + VERTICAL_SPACING) + 50;
      nodeWithPosition.position = { x, y };

      if (node.children && node.children.length > 0) {
        nodeWithPosition.children = node.children.map((child, idx) =>
          calculateNodePositions(child, depth + 1, index + idx + 1, nodeWithPosition.position)
        );
      }
    }

    return nodeWithPosition;
  };

  // Count total nodes in subtree
  const countNodes = (node: AssetNode): number => {
    let count = 1;
    if (node.children) {
      count += node.children.reduce((sum, child) => sum + countNodes(child), 0);
    }
    return count;
  };

  // Get all nodes as flat array
  const getAllNodes = (node: AssetNode): AssetNode[] => {
    const nodes = [node];
    if (node.children) {
      node.children.forEach(child => {
        nodes.push(...getAllNodes(child));
      });
    }
    return nodes;
  };

  // Calculate layout
  const layoutData = data ? calculateNodePositions(data.rootNode) : null;
  const allNodes = layoutData ? getAllNodes(layoutData) : [];

  // Handle node selection
  const handleNodeClick = (node: AssetNode) => {
    setSelectedNodeId(node.id);
    onNodeSelect?.(node);
  };

  // Pan and zoom controls
  const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.button === 0 && e.target === canvasRef.current) {
      setIsPanning(true);
      setDragStart({ x: e.clientX - panOffset.x, y: e.clientY - panOffset.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (isPanning) {
      setPanOffset({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    }
  };

  const handleMouseUp = () => {
    setIsPanning(false);
  };

  const handleWheel = (e: React.WheelEvent<HTMLDivElement>) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    setZoomLevel(prev => Math.max(0.1, Math.min(3, prev * delta)));
  };

  // Zoom controls
  const handleZoomIn = () => setZoomLevel(prev => Math.min(3, prev * 1.2));
  const handleZoomOut = () => setZoomLevel(prev => Math.max(0.1, prev / 1.2));
  const handleResetView = () => {
    setZoomLevel(1);
    setPanOffset({ x: 0, y: 0 });
  };

  // Get node color based on type
  const getNodeColor = (type: AssetNode['type']): string => {
    switch (type) {
      case 'original': return 'border-blue-500 bg-blue-500/10';
      case 'version': return 'border-green-500 bg-green-500/10';
      case 'variant': return 'border-purple-500 bg-purple-500/10';
      case 'refinement': return 'border-yellow-500 bg-yellow-500/10';
      case 'composite': return 'border-pink-500 bg-pink-500/10';
      default: return 'border-gray-500 bg-gray-500/10';
    }
  };

  // Get status color
  const getStatusColor = (status?: string): string => {
    switch (status) {
      case 'approved': return 'bg-green-600';
      case 'rejected': return 'bg-red-600';
      case 'pending': return 'bg-yellow-600';
      case 'archived': return 'bg-gray-600';
      default: return 'bg-gray-700';
    }
  };

  // Render connection lines
  const renderConnections = () => {
    if (!layoutData) return null;

    const lines: JSX.Element[] = [];

    const addLines = (node: AssetNode) => {
      if (node.children && node.position) {
        node.children.forEach(child => {
          if (child.position) {
            const isSelected = selectedNodeId === node.id || selectedNodeId === child.id;
            const isHovered = hoveredNodeId === node.id || hoveredNodeId === child.id;

            lines.push(
              <line
                key={`${node.id}-${child.id}`}
                x1={node.position.x + NODE_WIDTH / 2}
                y1={node.position.y + NODE_HEIGHT}
                x2={child.position.x + NODE_WIDTH / 2}
                y2={child.position.y}
                stroke={isSelected ? '#a78bfa' : isHovered ? '#6b7280' : '#374151'}
                strokeWidth={isSelected ? 3 : 2}
                strokeDasharray={child.type === 'refinement' ? '5,5' : 'none'}
              />
            );
          }
          addLines(child);
        });
      }
    };

    addLines(layoutData);
    return lines;
  };

  // Render nodes
  const renderNodes = () => {
    return allNodes.map(node => {
      if (!node.position) return null;

      const isSelected = selectedNodeId === node.id;
      const isHovered = hoveredNodeId === node.id;

      return (
        <g
          key={node.id}
          transform={`translate(${node.position.x}, ${node.position.y})`}
          onMouseEnter={() => setHoveredNodeId(node.id)}
          onMouseLeave={() => setHoveredNodeId(null)}
        >
          {/* Node container */}
          <foreignObject width={NODE_WIDTH} height={NODE_HEIGHT}>
            <div
              onClick={() => handleNodeClick(node)}
              className={`w-full h-full p-3 rounded-lg border-2 cursor-pointer transition-all ${
                getNodeColor(node.type)
              } ${
                isSelected ? 'ring-2 ring-purple-500 scale-105' : ''
              } ${
                isHovered ? 'shadow-lg' : ''
              }`}
              style={{ backgroundColor: 'rgba(17, 24, 39, 0.95)' }}
            >
              {/* Thumbnail */}
              {node.thumbnailUrl ? (
                <div className="w-full h-16 mb-2 rounded overflow-hidden bg-gray-950">
                  <img
                    src={node.thumbnailUrl}
                    alt={node.title}
                    className="w-full h-full object-cover"
                  />
                </div>
              ) : (
                <div className="w-full h-16 mb-2 rounded bg-gray-950 flex items-center justify-center">
                  <GitBranch className="w-6 h-6 text-gray-600" />
                </div>
              )}

              {/* Info */}
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <h5 className="text-xs font-semibold text-white truncate flex-1">
                    {node.title}
                  </h5>
                  {node.metadata.status && (
                    <span className={`px-1.5 py-0.5 rounded text-xs text-white ${getStatusColor(node.metadata.status)}`}>
                      {node.metadata.status[0].toUpperCase()}
                    </span>
                  )}
                </div>

                <p className="text-xs text-gray-400 capitalize">{node.type}</p>

                {node.metadata.changes && (
                  <p className="text-xs text-blue-400 truncate">{node.metadata.changes}</p>
                )}
              </div>

              {/* Actions (on hover) */}
              {(isHovered || isSelected) && (
                <div className="absolute inset-x-0 bottom-0 p-2 bg-gray-900/95 rounded-b-lg flex items-center justify-center space-x-1">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onNodeView?.(node);
                    }}
                    className="p-1 bg-gray-800 hover:bg-gray-700 rounded transition"
                    title="View"
                  >
                    <Eye className="w-3 h-3 text-gray-400" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onNodeDownload?.(node);
                    }}
                    className="p-1 bg-gray-800 hover:bg-gray-700 rounded transition"
                    title="Download"
                  >
                    <Download className="w-3 h-3 text-gray-400" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      onNodeDuplicate?.(node);
                    }}
                    className="p-1 bg-gray-800 hover:bg-gray-700 rounded transition"
                    title="Duplicate"
                  >
                    <Copy className="w-3 h-3 text-gray-400" />
                  </button>
                  {node.metadata.status === 'pending' && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onNodeApprove?.(node.id);
                      }}
                      className="p-1 bg-green-600 hover:bg-green-500 rounded transition"
                      title="Approve"
                    >
                      <Star className="w-3 h-3 text-white" />
                    </button>
                  )}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (confirm('Delete this asset and all its descendants?')) {
                        onNodeDelete?.(node.id);
                      }
                    }}
                    className="p-1 bg-red-600 hover:bg-red-500 rounded transition"
                    title="Delete"
                  >
                    <Trash2 className="w-3 h-3 text-white" />
                  </button>
                </div>
              )}
            </div>
          </foreignObject>
        </g>
      );
    });
  };

  // Calculate SVG dimensions
  const svgWidth = Math.max(1000, ...allNodes.map(n => (n.position?.x || 0) + NODE_WIDTH + 100));
  const svgHeight = Math.max(800, ...allNodes.map(n => (n.position?.y || 0) + NODE_HEIGHT + 100));

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <GitBranch className="w-6 h-6 text-green-400" />
          <div>
            <h3 className="text-lg font-bold text-white">Asset Lineage</h3>
            <p className="text-sm text-gray-400">
              {data ? `${data.totalNodes} assets • ${data.totalBranches} branches • ${data.maxDepth} levels deep` : 'No data'}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {/* Layout Mode */}
          <div className="flex items-center bg-gray-900 rounded-lg p-1">
            <button
              onClick={() => setLayoutMode('tree')}
              className={`px-3 py-1.5 rounded text-sm transition ${
                layoutMode === 'tree'
                  ? 'bg-green-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Tree
            </button>
            <button
              onClick={() => setLayoutMode('timeline')}
              className={`px-3 py-1.5 rounded text-sm transition ${
                layoutMode === 'timeline'
                  ? 'bg-green-600 text-white'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              Timeline
            </button>
          </div>

          {/* Zoom Controls */}
          <div className="flex items-center bg-gray-900 rounded-lg p-1 space-x-1">
            <button
              onClick={handleZoomOut}
              className="p-2 hover:bg-gray-800 rounded transition"
              title="Zoom Out"
            >
              <ZoomOut className="w-4 h-4 text-gray-400" />
            </button>
            <span className="px-2 text-sm text-gray-400">{Math.round(zoomLevel * 100)}%</span>
            <button
              onClick={handleZoomIn}
              className="p-2 hover:bg-gray-800 rounded transition"
              title="Zoom In"
            >
              <ZoomIn className="w-4 h-4 text-gray-400" />
            </button>
            <button
              onClick={handleResetView}
              className="p-2 hover:bg-gray-800 rounded transition"
              title="Reset View"
            >
              <Locate className="w-4 h-4 text-gray-400" />
            </button>
          </div>

          {/* Minimap Toggle */}
          <button
            onClick={() => setShowMinimap(!showMinimap)}
            className={`px-3 py-2 rounded-lg transition ${
              showMinimap
                ? 'bg-green-600 text-white'
                : 'bg-gray-900 text-gray-400 hover:bg-gray-700'
            }`}
          >
            {showMinimap ? <Minimize2 className="w-4 h-4" /> : <Maximize2 className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Canvas */}
      <div
        ref={canvasRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        className="relative bg-gray-900 rounded-lg border border-gray-700 overflow-hidden cursor-grab active:cursor-grabbing"
        style={{ height: '600px' }}
      >
        {!data ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <GitBranch className="w-12 h-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-400 mb-2">No lineage data available</p>
              <p className="text-sm text-gray-500">Select an asset to view its family tree</p>
            </div>
          </div>
        ) : (
          <svg
            ref={svgRef}
            width="100%"
            height="100%"
            viewBox={`${-panOffset.x / zoomLevel} ${-panOffset.y / zoomLevel} ${1000 / zoomLevel} ${600 / zoomLevel}`}
            className="w-full h-full"
          >
            {/* Grid background */}
            <defs>
              <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#374151" strokeWidth="0.5" opacity="0.3" />
              </pattern>
            </defs>
            <rect width={svgWidth} height={svgHeight} fill="url(#grid)" />

            {/* Connection lines */}
            <g>{renderConnections()}</g>

            {/* Nodes */}
            <g>{renderNodes()}</g>
          </svg>
        )}

        {/* Minimap */}
        {showMinimap && data && (
          <div className="absolute bottom-4 right-4 w-48 h-32 bg-gray-950/90 border border-gray-700 rounded-lg overflow-hidden">
            <svg
              width="100%"
              height="100%"
              viewBox={`0 0 ${svgWidth} ${svgHeight}`}
              className="w-full h-full"
            >
              {/* Minimap connections */}
              <g opacity="0.5">{renderConnections()}</g>

              {/* Minimap nodes (simplified) */}
              {allNodes.map(node => {
                if (!node.position) return null;
                return (
                  <rect
                    key={node.id}
                    x={node.position.x}
                    y={node.position.y}
                    width={NODE_WIDTH}
                    height={NODE_HEIGHT}
                    fill={selectedNodeId === node.id ? '#a78bfa' : '#4b5563'}
                    stroke="#6b7280"
                    strokeWidth="2"
                    rx="4"
                  />
                );
              })}

              {/* Viewport indicator */}
              <rect
                x={-panOffset.x / zoomLevel}
                y={-panOffset.y / zoomLevel}
                width={1000 / zoomLevel}
                height={600 / zoomLevel}
                fill="none"
                stroke="#a78bfa"
                strokeWidth="3"
              />
            </svg>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className="mt-4 bg-gray-900 rounded-lg p-4 border border-gray-700">
        <h4 className="text-sm font-semibold text-white mb-3">Legend</h4>
        <div className="grid grid-cols-5 gap-4">
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded border-2 border-blue-500 bg-blue-500/20"></div>
            <span className="text-xs text-gray-400">Original</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded border-2 border-green-500 bg-green-500/20"></div>
            <span className="text-xs text-gray-400">Version</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded border-2 border-purple-500 bg-purple-500/20"></div>
            <span className="text-xs text-gray-400">Variant</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded border-2 border-yellow-500 bg-yellow-500/20"></div>
            <span className="text-xs text-gray-400">Refinement</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-4 h-4 rounded border-2 border-pink-500 bg-pink-500/20"></div>
            <span className="text-xs text-gray-400">Composite</span>
          </div>
        </div>
      </div>

      {/* Tips */}
      <div className="mt-4 bg-green-600/10 border border-green-600/30 rounded-lg p-3">
        <p className="text-xs text-green-400">
          <strong>💡 Pro Tip:</strong> Click and drag to pan, scroll to zoom. Click nodes to select and view actions.
          Hover over nodes to see quick actions. Dashed lines indicate refinement relationships.
        </p>
      </div>
    </div>
  );
};

export default LineageViewer;
