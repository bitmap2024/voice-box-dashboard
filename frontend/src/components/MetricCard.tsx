import type { Kpi } from '../types';

export function MetricCard({ item }: { item: Kpi }) {
  return (
    <div className="metric-card">
      <span>{item.label}</span>
      <strong>
        {item.value}
        <small>{item.unit}</small>
      </strong>
      <em>{item.trend}</em>
    </div>
  );
}
