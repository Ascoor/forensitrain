import React from 'react';

const images = [
  { src: 'https://via.placeholder.com/80', confidence: 92 },
  { src: 'https://via.placeholder.com/80', confidence: 75 },
  { src: 'https://via.placeholder.com/80', confidence: 60 },
];

const ImageGrid = () => (
  <div className="bg-gray-800/60 backdrop-blur-lg rounded shadow p-4 h-64 overflow-auto">
    <p className="mb-2 font-semibold">Image Analysis</p>
    <div className="grid grid-cols-3 gap-2">
      {images.map((img, idx) => (
        <div key={idx} className="relative">
          <img src={img.src} alt="thumb" className="rounded" />
          <span className="absolute bottom-1 right-1 text-xs bg-black/60 px-1 rounded">
            {img.confidence}%
          </span>
        </div>
      ))}
    </div>
  </div>
);

export default ImageGrid;
