import React from 'react'; 
const GraphView = ({ graph }) => {
  if (!graph || !graph.nodes) return null;
  return (
    <div className="h-96 border rounded">
      <ForceGraph2D graphData={graph} />
    </div>
  );
};

export default GraphView;
