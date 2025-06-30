import React from 'react';
import { useTranslation } from 'react-i18next';

/**
 * Displays a glTF digital human model using A-Frame.
 */
const AvatarViewer = () => {
  const { t } = useTranslation();
  const modelUrl =
    'https://raw.githubusercontent.com/mrdoob/three.js/master/examples/models/gltf/RobotExpressive/RobotExpressive.glb';

  return (
    <div className="bg-gray-800/60 backdrop-blur-lg rounded shadow p-4 h-80">
      <p className="mb-2 font-semibold">{t('avatar_viewer')}</p>
      <a-scene embedded vr-mode-ui="enabled: false">
        <a-assets>
          <a-asset-item id="avatar" src={modelUrl}></a-asset-item>
        </a-assets>
        <a-entity gltf-model="#avatar" position="0 -1 -3" rotation="0 180 0"></a-entity>
        <a-entity light="type: ambient; intensity: 0.5"></a-entity>
        <a-entity light="type: directional; intensity: 0.8" position="1 1 1"></a-entity>
        <a-sky color="#ECECEC"></a-sky>
      </a-scene>
    </div>
  );
};

export default AvatarViewer;
