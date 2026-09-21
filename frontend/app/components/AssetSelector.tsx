"use client";

interface AssetSelectorProps {
  selected: "BTC" | "ETH" | "SOL";
  onSelect: (asset: "BTC" | "ETH" | "SOL") => void;
}

export default function AssetSelector({ selected, onSelect }: AssetSelectorProps) {
  const assets = [
    { key: "BTC" as const, label: "BTC/USDT", price: "$118,000" },
    { key: "ETH" as const, label: "ETH/USDT", price: "$3,850" },
    { key: "SOL" as const, label: "SOL/USDT", price: "$168" },
  ];

  return (
    <div className="flex gap-3 mb-6">
      {assets.map((asset) => (
        <button
          key={asset.key}
          onClick={() => onSelect(asset.key)}
          className={`flex-1 max-w-[180px] px-4 py-3 rounded-xl border text-left transition-all ${
            selected === asset.key
              ? "bg-gray-900 text-white border-gray-900 shadow-lg"
              : "bg-white text-gray-700 border-gray-200 hover:border-gray-300 hover:bg-gray-50"
          }`}
        >
          <div className="text-sm font-semibold">{asset.label}</div>
          <div className={`text-xs mt-1 ${selected === asset.key ? "text-gray-300" : "text-gray-400"}`}>
            {asset.price}
          </div>
        </button>
      ))}
    </div>
  );
}
