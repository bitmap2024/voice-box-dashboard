export function StatusBadge({ value }: { value: string }) {
  const label: Record<string, string> = {
    active: '启用',
    trial: '试用',
    online: '在线',
    offline: '离线',
    warning: '异常',
    open: '未处理',
    resolved: '已处理',
    published: '已发布',
    draft: '草稿',
    archived: '历史',
    high: '高',
    medium: '中',
    low: '低',
  };

  return <span className={`status ${value}`}>{label[value] || value}</span>;
}
