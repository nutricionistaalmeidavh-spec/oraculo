"use client";

import { useEffect, useRef } from "react";
import { Zone } from "../types";

interface ZoneChartProps {
  asset: string;
  currentPrice: number;
  zones: Zone[];
}

export default function ZoneChart({ asset, currentPrice, zones }: ZoneChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Setup canvas
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    const w = rect.width;
    const h = rect.height;
    const pad = { top: 20, right: 80, bottom: 30, left: 20 };
    const cw = w - pad.left - pad.right;
    const ch = h - pad.top - pad.bottom;

    // Clear
    ctx.clearRect(0, 0, w, h);

    // Determine price range
    const allPrices = zones.flatMap(z => [z.price_bottom, z.price_top, z.center_price]);
    allPrices.push(currentPrice);
    const minP = Math.min(...allPrices) * 0.98;
    const maxP = Math.max(...allPrices) * 1.02;
    const range = maxP - minP;

    const priceToY = (p: number) => pad.top + ch - ((p - minP) / range) * ch;

    // Grid lines
    ctx.strokeStyle = "#e5e7eb";
    ctx.lineWidth = 0.5;
    ctx.setLineDash([3, 3]);
    for (let i = 0; i <= 5; i++) {
      const y = pad.top + (ch / 5) * i;
      const price = maxP - (range / 5) * i;
      ctx.beginPath();
      ctx.moveTo(pad.left, y);
      ctx.lineTo(w - pad.right, y);
      ctx.stroke();

      ctx.fillStyle = "#9ca3af";
      ctx.font = "11px sans-serif";
      ctx.textAlign = "left";
      ctx.fillText(`$${(price / 1000).toFixed(1)}k`, w - pad.right + 6, y + 4);
    }
    ctx.setLineDash([]);

    // Draw zones
    zones.forEach((zone) => {
      const yTop = priceToY(zone.price_top);
      const yBot = priceToY(zone.price_bottom);
      const height = Math.max(yBot - yTop, 3);

      let color = "rgba(59, 130, 246, 0.15)";
      let borderColor = "#3b82f6";

      if (zone.zone_type === "critical") {
        color = "rgba(239, 68, 68, 0.18)";
        borderColor = "#ef4444";
      } else if (zone.zone_type === "high") {
        color = "rgba(245, 158, 11, 0.15)";
        borderColor = "#f59e0b";
      }

      // Zone fill
      ctx.fillStyle = color;
      ctx.fillRect(pad.left, yTop, cw, height);

      // Zone borders
      ctx.strokeStyle = borderColor;
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(pad.left, yTop);
      ctx.lineTo(w - pad.right, yTop);
      ctx.stroke();

      ctx.beginPath();
      ctx.moveTo(pad.left, yBot);
      ctx.lineTo(w - pad.right, yBot);
      ctx.stroke();

      // Confluence dots
      const colors = ["#3b82f6", "#ef4444", "#10b981", "#8b5cf6", "#6b7280", "#f59e0b"];
      zone.timeframes.forEach((tf, i) => {
        const dotX = pad.left + 25 + i * 16;
        const dotY = yTop + height / 2;
        ctx.fillStyle = colors[i % colors.length];
        ctx.beginPath();
        ctx.arc(dotX, dotY, 4, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = "white";
        ctx.lineWidth = 1.5;
        ctx.stroke();
      });

      // Score label
      ctx.fillStyle = borderColor;
      ctx.font = "bold 11px sans-serif";
      ctx.textAlign = "right";
      ctx.fillText(`${zone.score}`, w - pad.right - 8, yTop + height / 2 + 4);
    });

    // Current price line
    const curY = priceToY(currentPrice);
    ctx.strokeStyle = "#10b981";
    ctx.lineWidth = 1.5;
    ctx.setLineDash([5, 3]);
    ctx.beginPath();
    ctx.moveTo(pad.left, curY);
    ctx.lineTo(w - pad.right, curY);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = "#10b981";
    ctx.font = "bold 11px sans-serif";
    ctx.textAlign = "left";
    ctx.fillText(`$${(currentPrice / 1000).toFixed(1)}k`, w - pad.right + 6, curY + 4);

    // Simulated price path
    ctx.strokeStyle = "rgba(0,0,0,0.6)";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    const n = 100;
    for (let i = 0; i <= n; i++) {
      const x = pad.left + (cw / n) * i;
      const t = i / n;
      const trend = minP + range * (0.3 + 0.4 * Math.sin(t * 4) + 0.3 * t);
      const noise = (Math.random() - 0.5) * range * 0.03;
      const y = priceToY(trend + noise);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.stroke();

  }, [asset, currentPrice, zones]);

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100 flex justify-between items-center">
        <div>
          <h3 className="text-sm font-semibold text-gray-900">Mapa de Zonas</h3>
          <p className="text-xs text-gray-400 mt-0.5">Confluência de Fibonacci em múltiplos horizontes</p>
        </div>
        <div className="flex gap-4 text-xs text-gray-500">
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-blue-500"></span>Ciclo</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-red-500"></span>1 Ano</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-green-500"></span>6M</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-purple-500"></span>3M</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-gray-500"></span>1M</span>
          <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-sm bg-amber-500"></span>Sem</span>
        </div>
      </div>
      <canvas 
        ref={canvasRef} 
        className="w-full h-[360px]"
        style={{ width: "100%", height: "360px" }}
      />
    </div>
  );
}
