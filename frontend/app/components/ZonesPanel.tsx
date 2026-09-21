"use client";

import { Zone } from "../types";

interface ZonesPanelProps {
  zones: Zone[];
}

export default function ZonesPanel({ zones }: ZonesPanelProps) {
  const getBadgeClass = (type: string) => {
    switch (type) {
      case "critical": return "bg-red-50 text-red-700 border-red-200";
      case "high": return "bg-amber-50 text-amber-700 border-amber-200";
      case "medium": return "bg-blue-50 text-blue-700 border-blue-200";
      default: return "bg-gray-50 text-gray-600 border-gray-200";
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return "text-red-600";
    if (score >= 80) return "text-amber-600";
    if (score >= 70) return "text-blue-600";
    return "text-gray-500";
  };

  const getBarColor = (score: number) => {
    if (score >= 90) return "bg-red-500";
    if (score >= 80) return "bg-amber-500";
    if (score >= 70) return "bg-blue-500";
    return "bg-gray-400";
  };

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-100">
        <h3 className="text-sm font-semibold text-gray-900">Zonas Detectadas</h3>
        <p className="text-xs text-gray-400 mt-0.5">Ordenadas por score de confluência</p>
      </div>
      <div className="divide-y divide-gray-100 max-h-[500px] overflow-y-auto">
        {zones.map((zone, idx) => (
          <div key={idx} className="px-4 py-3 hover:bg-gray-50 transition-colors">
            <div className="flex items-start justify-between gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className={`text-lg font-bold tabular-nums ${getScoreColor(zone.score)}`}>
                    {zone.score}
                  </span>
                  <span className={`text-xs px-2 py-0.5 rounded-md border font-medium ${getBadgeClass(zone.zone_type)}`}>
                    {zone.zone_type === "critical" ? "Crítica" : 
                     zone.zone_type === "high" ? "Alta" : 
                     zone.zone_type === "medium" ? "Média" : "Observação"}
                  </span>
                </div>
                <div className="text-sm font-medium text-gray-900 mt-1">
                  ${zone.center_price.toLocaleString()}
                </div>
                <div className="text-xs text-gray-500 mt-0.5">
                  Range: ${zone.price_bottom.toLocaleString()} – ${zone.price_top.toLocaleString()}
                </div>
                <div className="text-xs text-gray-400 mt-1 line-clamp-2">
                  {zone.description}
                </div>
                <div className="flex flex-wrap gap-1 mt-2">
                  {zone.timeframes.map((tf) => (
                    <span key={tf} className="text-[10px] px-1.5 py-0.5 bg-gray-100 text-gray-500 rounded">
                      {tf.replace("_", " ")}
                    </span>
                  ))}
                </div>
                <div className="mt-2">
                  <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full transition-all ${getBarColor(zone.score)}`}
                      style={{ width: `${zone.score}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
