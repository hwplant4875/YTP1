import React from 'react';
import { AbsoluteFill, spring, useCurrentFrame, useVideoConfig } from 'remotion';
export const Smoke: React.FC = () => {
  const f = useCurrentFrame(); const { fps } = useVideoConfig();
  const s = spring({ frame: f, fps, config: { damping: 10 } });
  return <AbsoluteFill style={{ background: '#1A2329', alignItems: 'center', justifyContent: 'center' }}>
    <div style={{ transform: `scale(${s})`, color: '#FFC83D', fontSize: 160, fontFamily: 'sans-serif', fontWeight: 900 }}>REMOTION OK</div>
  </AbsoluteFill>;
};
