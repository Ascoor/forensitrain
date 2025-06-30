import React, { useRef, useEffect } from 'react'
import ForceGraph2D from 'react-force-graph-2d'

// Simple color mapping by node type
const COLORS = {
  phone: '#2563eb',
  email: '#16a34a',
  social: '#f59e0b',
  breach: '#dc2626',
  default: '#6b7280'
}

/**
 * GraphView renders a force-directed graph using react-force-graph.
 * Nodes can represent phones, emails, social profiles and breaches.
 * Pass in an object with `nodes` and `links` arrays like:
 * {
 *   nodes: [{ id, type, label }],
 *   links: [{ source, target }]
 * }
 */
const GraphView = ({ graph, loading = false, error = null }) => {
  const fgRef = useRef()

  // Zoom to fit whenever the graph data changes
  useEffect(() => {
    if (graph && fgRef.current) {
      fgRef.current.zoomToFit(400)
    }
  }, [graph])

  if (loading) {
    return (
      <div className="flex justify-center my-4">
        <div className="h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (error) {
    return <p className="text-red-600">{error}</p>
  }

  if (!graph || !graph.nodes || graph.nodes.length === 0) {
    return <p className="text-sm italic">No graph data available.</p>
  }

  // Color nodes by type
  const nodeColor = (node) => COLORS[node.type] || COLORS.default

  return (
    <div className="h-96 border rounded">
      <ForceGraph2D
        ref={fgRef}
        graphData={graph}
        nodeLabel={(node) => node.label || node.id}
        nodeColor={nodeColor}
        linkColor={() => '#9ca3af'}
        linkDirectionalParticles={1}
        linkDirectionalParticleWidth={1}
      />
    </div>
  )
}

export default GraphView
