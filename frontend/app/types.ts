export interface Zone {
  center_price: number;
  price_bottom: number;
  price_top: number;
  score: number;
  zone_type: "critical" | "high" | "medium" | "observation";
  confluence_count: number;
  timeframes: string[];
  description: string;
}

export interface ZoneData {
  symbol: string;
  current_price: number;
  zones: Zone[];
}
