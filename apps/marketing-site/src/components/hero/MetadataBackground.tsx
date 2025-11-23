"use client";

import React, { useRef, useState, useMemo, createRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial, Float, Text, Billboard } from '@react-three/drei';
import * as THREE from 'three';
import { useTheme } from 'next-themes';

// Generate random points for the background particles
function generatePoints(count: number, radius: number) {
  const points = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    const i3 = i * 3;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(2 * Math.random() - 1);
    const r = radius * Math.cbrt(Math.random());
    points[i3] = r * Math.sin(phi) * Math.cos(theta);
    points[i3 + 1] = r * Math.sin(phi) * Math.sin(theta);
    points[i3 + 2] = r * Math.cos(phi);
  }
  return points;
}

function Particles({ count = 2000, color = '#2a87c4' }: { count?: number; color?: string }) {
  const pointsRef = useRef<THREE.Points>(null!);
  const [positions] = useState(() => generatePoints(count, 3));

  useFrame((state) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.x = state.clock.getElapsedTime() * 0.05;
      pointsRef.current.rotation.y = state.clock.getElapsedTime() * 0.08;
    }
  });

  return (
    <Points ref={pointsRef} positions={positions} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color={color}
        size={0.05}
        sizeAttenuation={true}
        depthWrite={false}
        blending={THREE.AdditiveBlending}
        opacity={0.8}
      />
    </Points>
  );
}

// DynamicLine updates every frame to connect two objects by their world positions
function DynamicLine({
  startRef,
  endRef,
  color,
}: {
  startRef: React.RefObject<THREE.Object3D | null>;
  endRef: React.RefObject<THREE.Object3D | null>;
  color: string;
}) {
  const lineRef = useRef<THREE.Line>(null!); 

  const geometry = useMemo(() => {
    const geom = new THREE.BufferGeometry();
    geom.setAttribute('position', new THREE.BufferAttribute(new Float32Array(6), 3));
    return geom;
  }, []);

  const line = useMemo(() => {
    const material = new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.3 });
    return new THREE.Line(geometry, material);
  }, [geometry, color]);

  useFrame(() => {
    if (startRef.current && endRef.current && lineRef.current) {
      const startPos = new THREE.Vector3();
      const endPos = new THREE.Vector3();
      startRef.current.getWorldPosition(startPos);
      endRef.current.getWorldPosition(endPos);

      const positionAttribute = lineRef.current.geometry.getAttribute('position') as THREE.BufferAttribute;
      positionAttribute.setXYZ(0, startPos.x, startPos.y, startPos.z);
      positionAttribute.setXYZ(1, endPos.x, endPos.y, endPos.z);
      positionAttribute.needsUpdate = true;
    }
  });

  return <primitive object={line} ref={lineRef} />;
}

// UnicodeVariationSelectors displays animated Unicode symbols.
// Each group is given a ref from the parent.
function UnicodeVariationSelectors({ refs }: { refs: React.RefObject<THREE.Group | null>[] }) {
  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme === 'dark';

  const unicodeSymbols = [
    { symbol: "FE00", position: [1.5, 0, 0] as [number, number, number] },
    { symbol: "FE01", position: [-1.5, 0.5, 1] as [number, number, number] },
    { symbol: "FE02", position: [0, -1.5, -1] as [number, number, number] },
    { symbol: "FE03", position: [1.2, 1.2, 0.5] as [number, number, number] },
    { symbol: "FE04", position: [-1.2, -0.8, 0.8] as [number, number, number] },
    { symbol: "FE05", position: [0.8, -0.9, 1.2] as [number, number, number] },
  ];

  return (
    <group>
      {unicodeSymbols.map((item, index) => (
        <group key={index} position={item.position} ref={refs[index]}>
          <Float
            speed={1 + Math.random() * 0.5}
            rotationIntensity={0.3 + Math.random() * 0.5}
            floatIntensity={0.3 + Math.random() * 0.5}
          >
            <mesh>
              <octahedronGeometry args={[0.15, 0]} />
              <meshBasicMaterial
                color="#1b2f50"
                wireframe
                transparent
                opacity={0.3}
              />
            </mesh>
          </Float>
          <Billboard follow={true}>
            <Text
              color="#1b2f50"
              fontSize={0.2}
              anchorX="center"
              anchorY="middle"
            >
              {item.symbol}
            </Text>
          </Billboard>
        </group>
      ))}
    </group>
  );
}

// MetadataObjects displays metadata text objects.
// Each group is given a ref from the parent.
function MetadataObjects({ refs }: { refs: React.RefObject<THREE.Group | null>[] }) {
  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme === 'dark';

  const metadataObjects = [
    { text: 'model_id: gpt4o', position: [2, 0.5, -1] as [number, number, number] },
    { text: 'timestamp: 1679529600', position: [-2, -0.5, -1.5] as [number, number, number] },
    { text: 'model_id: claude-3-opus', position: [0, 1.8, 0.5] as [number, number, number] },
    { text: 'timestamp: 1711342092', position: [1.5, -1.2, 0.8] as [number, number, number] },
    { text: 'model_id: gemini-2.5-pro', position: [-1.8, 1.2, -0.7] as [number, number, number] },
    { text: 'verified: true', position: [1.2, 1.5, -1.2] as [number, number, number] },
    { text: 'source: openai', position: [-1.2, -1.5, 0.5] as [number, number, number] },
    { text: 'signature: a1b2c3d4', position: [0.8, -1.8, -0.5] as [number, number, number] },
    { text: 'version: 2.0.0', position: [-0.5, 1.0, 1.5] as [number, number, number] },
    { text: 'created_by: Encypher', position: [1.8, 0.2, 1.0] as [number, number, number] },
  ];

  return (
    <group>
      {metadataObjects.map((item, index) => (
        <group key={index} position={item.position} ref={refs[index]}>
          <Float
            speed={0.5 + Math.random() * 0.3}
            rotationIntensity={0.2 + Math.random() * 0.3}
            floatIntensity={0.2 + Math.random() * 0.3}
          >
            <group />
          </Float>
          <Billboard follow={true}>
            <Text
              color="#1b2f50"
              fontSize={0.15}
              maxWidth={2}
              anchorX="center"
              anchorY="middle"
              fillOpacity={0.7}
            >
              {item.text}
            </Text>
          </Billboard>
        </group>
      ))}
    </group>
  );
}

// EncypherHub is the central hub. We use forwardRef so the parent can get its mesh reference.
const EncypherHub = React.forwardRef<THREE.Mesh>((props, ref) => {
  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme === 'dark';

  useFrame((state) => {
    if (ref && typeof ref !== 'function' && ref.current) {
      ref.current.rotation.x = state.clock.getElapsedTime() * 0.2;
      ref.current.rotation.y = state.clock.getElapsedTime() * 0.3;
    }
  });

  return (
    <mesh ref={ref as React.Ref<THREE.Mesh>} position={[0, 0, 0]}>
      <dodecahedronGeometry args={[0.3, 0]} />
      <meshBasicMaterial
        color="#1b2f50"
        wireframe
        transparent
        opacity={0.7}
      />
    </mesh>
  );
});

EncypherHub.displayName = 'EncypherHub';

// ConnectionLines renders a DynamicLine for every text object connecting it to the hub.
function ConnectionLines({
  unicodeRefs,
  metadataRefs,
  hubRef,
  color,
}: {
  unicodeRefs: React.RefObject<THREE.Group | null>[];
  metadataRefs: React.RefObject<THREE.Group | null>[];
  hubRef: React.RefObject<THREE.Mesh | null>;
  color: string;
}) {
  return (
    <group>
      {unicodeRefs.map((ref, index) => (
        <DynamicLine key={`unicode-${index}`} startRef={ref} endRef={hubRef} color={color} />
      ))}
      {metadataRefs.map((ref, index) => (
        <DynamicLine key={`metadata-${index}`} startRef={ref} endRef={hubRef} color={color} />
      ))}
    </group>
  );
}

// Main Scene: create refs for each text object and the hub,
// and rotate the parent groups for additional animation.
function Scene() {
  const { resolvedTheme } = useTheme();
  const isDark = resolvedTheme === 'dark';
  const lineColor = '#1b2f50';

  // Create refs for Unicode symbols (6 items)
  const unicodeRefs = useMemo(
    () => Array.from({ length: 6 }, () => createRef<THREE.Group>()),
    []
  );
  // Create refs for Metadata objects (10 items)
  const metadataRefs = useMemo(
    () => Array.from({ length: 10 }, () => createRef<THREE.Group>()),
    []
  );
  // Ref for the central hub
  const hubRef = useRef<THREE.Mesh>(null!);

  // Group refs for additional rotation animation
  const symbolsGroupRef = useRef<THREE.Group>(null!);
  const metadataGroupRef = useRef<THREE.Group>(null!);

  useFrame((state) => {
    if (symbolsGroupRef.current) {
      symbolsGroupRef.current.rotation.y = state.clock.getElapsedTime() * 0.1;
    }
    if (metadataGroupRef.current) {
      metadataGroupRef.current.rotation.y = state.clock.getElapsedTime() * 0.05;
    }
  });

  return (
    <>
      <Particles color="#1b2f50" />
      <group ref={symbolsGroupRef}>
        <UnicodeVariationSelectors refs={unicodeRefs} />
      </group>
      <group ref={metadataGroupRef}>
        <MetadataObjects refs={metadataRefs} />
      </group>
      <ConnectionLines unicodeRefs={unicodeRefs} metadataRefs={metadataRefs} hubRef={hubRef} color={lineColor} />
      <EncypherHub ref={hubRef} />
    </>
  );
}

export default function MetadataBackground() {
  const { resolvedTheme } = useTheme();

  return (
    <div className="absolute inset-0 bg-background opacity-20">
      <Canvas key={resolvedTheme} camera={{ position: [0, 0, 5], fov: 50 }}>
        <ambientLight intensity={0.3} />
        <Scene />
      </Canvas>
    </div>
  );
}
