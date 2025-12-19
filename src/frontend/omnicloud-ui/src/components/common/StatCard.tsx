interface StatCardProps {
  label: string;
  value: string | number;
  change?: string;
  changeType?: 'positive' | 'negative' | 'neutral';
}

function StatCard({ label, value, change, changeType = 'neutral' }: StatCardProps) {
  return (
    <div className="stat-card">
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      {change && <div className={`stat-change ${changeType}`}>{change}</div>}
    </div>
  );
}

export default StatCard;
