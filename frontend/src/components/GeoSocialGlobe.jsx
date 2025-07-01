import React from 'react'
import { Canvas } from '@react-three/fiber'
import { OrbitControls, Stars } from '@react-three/drei'
import * as THREE from 'three'

function Markers({ data }) {
  const radius = 2
  const points = data.locations.map((loc) => {
    const phi = (90 - loc.lat) * (Math.PI / 180)
    const theta = (loc.lon + 180) * (Math.PI / 180)
    return new THREE.Vector3(
      -radius * Math.sin(phi) * Math.cos(theta),
      radius * Math.cos(phi),
      radius * Math.sin(phi) * Math.sin(theta)
    )
  })

  return (
    <group>
      {points.map((pos, idx) => (
        <mesh key={idx} position={pos}>
          <sphereGeometry args={[0.05, 8, 8]} />
          <meshStandardMaterial color="red" />
        </mesh>
      ))}
    </group>
  )
}

const GeoSocialGlobe = ({ data }) => (
  <Canvas className="h-96 w-full rounded">
    <ambientLight intensity={0.5} />
    <pointLight position={[10, 10, 10]} />
    <mesh>
      <sphereGeometry args={[2, 32, 32]} />
      <meshBasicMaterial wireframe color="white" />
    </mesh>
    <Markers data={data} />
    <OrbitControls />
    <Stars />
  </Canvas>
)

export default GeoSocialGlobe
