"use client";

import { useState } from "react";
import AssetSelector from "./components/AssetSelector";
import ZoneChart from "./components/ZoneChart";
import ZonesPanel from "./components/ZonesPanel";
import ZoneStats from "./components/ZoneStats";
import { ZoneData } from "./types";

const MOCK_ZONES: Record<string, ZoneData> = {
  BTC: {
    symbol: "BTCUSDT",
    current_price: 118000,
    zones: [
      { center_price: 109800, price_bottom: 108500, price_top: 111200, score: 96, zone_type: "critical", confluence_count: 5, timeframes: ["ciclo_completo", "1_ano", "6_meses", "3_meses", "1_mes"], description: "0.618 ciclo + 0.786 1ano + 1.0 6m + OB mensal + Topo Wyckoff" },
      { center_price: 102400, price_bottom: 101200, price_top: 103600, score: 91, zone_type: "critical", confluence_count: 4, timeframes: ["ciclo_completo", "1_ano", "6_meses", "3_meses"], description: "0.5 ciclo + 0.618 1ano + 0.786 6m + Cluster GMM 3σ" },
      { center_price: 95700, price_bottom: 94200, price_top: 97200, score: 88, zone_type: "high", confluence_count: 4, timeframes: ["ciclo_completo", "1_ano", "6_meses", "1_mes"], description: "0.382 ciclo + 0.5 1ano + Gann 90° + OB semanal" },
      { center_price: 89000, price_bottom: 87800, price_top: 90200, score: 85, zone_type: "high", confluence_count: 3, timeframes: ["1_ano", "6_meses", "3_meses"], description: "0.382 1ano + 0.618 6m + POC fase B Wyckoff" },
      { center_price: 81800, price_bottom: 80500, price_top: 83100, score: 78, zone_type: "medium", confluence_count: 3, timeframes: ["6_meses", "3_meses", "1_mes"], description: "0.5 6m + FVG H4 + KDE pico 78%" },
      { center_price: 74000, price_bottom: 72500, price_top: 75500, score: 94, zone_type: "critical", confluence_count: 5, timeframes: ["ciclo_completo", "1_ano", "6_meses", "3_meses", "semanal"], description: "0.0 ciclo + 0.0 1ano + 0.0 6m + Gann 180° + Spring Wyckoff" },
    ]
  },
  ETH: {
    symbol: "ETHUSDT",
    current_price: 3850,
    zones: [
      { center_price: 4100, price_bottom: 4020, price_top: 4180, score: 93, zone_type: "critical", confluence_count: 4, timeframes: ["ciclo_completo", "1_ano", "6_meses", "3_meses"], description: "1.0 ciclo + 1.0 1ano + 1.272 6m + OB diário" },
      { center_price: 3650, price_bottom: 3580, price_top: 3720, score: 87, zone_type: "high", confluence_count: 3, timeframes: ["1_ano", "6_meses", "3_meses"], description: "0.618 1ano + 0.786 6m + Cluster estatístico 2σ" },
      { center_price: 3220, price_bottom: 3150, price_top: 3290, score: 82, zone_type: "high", confluence_count: 3, timeframes: ["6_meses", "3_meses", "1_mes"], description: "0.5 6m + Gann 45° + Fase C Wyckoff" },
      { center_price: 2800, price_bottom: 2720, price_top: 2880, score: 95, zone_type: "critical", confluence_count: 5, timeframes: ["ciclo_completo", "1_ano", "6_meses", "3_meses", "semanal"], description: "0.0 ciclo + 0.0 1ano + 0.0 6m + Liquidity Pool + KDE 95%" },
    ]
  },
  SOL: {
    symbol: "SOLUSDT",
    current_price: 168,
    zones: [
      { center_price: 195, price_bottom: 188, price_top: 202, score: 89, zone_type: "high", confluence_count: 4, timeframes: ["ciclo_completo", "1_ano", "6_meses", "3_meses"], description: "1.0 ciclo + 1.272 1ano + OB semanal + Distribuição" },
      { center_price: 172, price_bottom: 166, price_top: 178, score: 76, zone_type: "medium", confluence_count: 3, timeframes: ["6_meses", "3_meses", "1_mes"], description: "0.786 6m + 1.0 3m + Cluster volume 68%" },
      { center_price: 148, price_bottom: 142, price_top: 154, score: 84, zone_type: "high", confluence_count: 3, timeframes: ["1_ano", "6_meses", "3_meses"], description: "0.618 1ano + Gann 90° + FVG H1" },
      { center_price: 120, price_bottom: 114, price_top: 126, score: 92, zone_type: "critical", confluence_count: 5, timeframes: ["ciclo_completo", "1_ano", "6_meses", "3_meses", "semanal"], description: "0.0 ciclo + 0.0 1ano + 0.0 6m + Liquidity Sweep + Spring" },
    ]
  }
};

export default function Home() {
  const [selectedAsset, setSelectedAsset] = useState<"BTC" | "ETH" | "SOL">("BTC");
  const [showOnlyCritical, setShowOnlyCritical] = useState(false);

  const data = MOCK_ZONES[selectedAsset];
  const filteredZones = showOnlyCritical 
    ? data.zones.filter(z => z.zone_type === "critical")
    : data.zones;

  return (
    <main className="max-w-7xl mx-auto px-4 py-6">
      {/* Header */}
      <header className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center text-white text-xl font-bold">
            ◈
          </div>
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">Oráculo de Zonas</h1>
            <p className="text-sm text-gray-500">Confluência multi-timeframe + Fibonacci</p>
          </div>
        </div>
      </header>

      {/* Asset Selector */}
      <AssetSelector 
        selected={selectedAsset} 
        onSelect={setSelectedAsset} 
      />

      {/* Filters */}
      <div className="flex gap-3 mb-6">
        <button
          onClick={() => setShowOnlyCritical(false)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            !showOnlyCritical 
              ? "bg-gray-900 text-white" 
              : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
          }`}
        >
          Todas as zonas
        </button>
        <button
          onClick={() => setShowOnlyCritical(true)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            showOnlyCritical 
              ? "bg-gray-900 text-white" 
              : "bg-white text-gray-600 border border-gray-200 hover:bg-gray-50"
          }`}
        >
          Apenas críticas (3+ confluências)
        </button>
      </div>

      {/* Stats */}
      <ZoneStats 
        symbol={data.symbol}
        currentPrice={data.current_price}
        totalZones={data.zones.length}
        criticalZones={data.zones.filter(z => z.zone_type === "critical").length}
      />

      {/* Chart + Zones */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
        <div className="lg:col-span-2">
          <ZoneChart 
            asset={selectedAsset}
            currentPrice={data.current_price}
            zones={filteredZones}
          />
        </div>
        <div className="lg:col-span-1">
          <ZonesPanel zones={filteredZones} />
        </div>
      </div>
    </main>
  );
}
