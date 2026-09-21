"use client";

interface ZoneStatsProps {
  symbol: string;
  currentPrice: number;
  totalZones: number;
  criticalZones: number;
}

export default function ZoneStats({ symbol, currentPrice, totalZones, criticalZones }: ZoneStatsProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="text-xs text-gray-500 uppercase tracking-wide">Ativo</div>
        <div className="text-lg font-semibold text-gray-900 mt-1">{symbol}</div>
      </div>
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="text-xs text-gray-500 uppercase tracking-wide">Preço Atual</div>
        <div className="text-lg font-semibold text-green-600 mt-1">
          ${currentPrice.toLocaleString()}
        </div>
      </div>
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="text-xs text-gray-500 uppercase tracking-wide">Zonas Detectadas</div>
        <div className="text-lg font-semibold text-gray-900 mt-1">{totalZones}</div>
      </div>
      <div className="bg-white rounded-xl border border-gray-200 p-4">
        <div className="text-xs text-gray-500 uppercase tracking-wide">Zonas Críticas</div>
        <div className="text-lg font-semibold text-red-600 mt-1">{criticalZones}</div>
      </div>
    </div>
  );
}
