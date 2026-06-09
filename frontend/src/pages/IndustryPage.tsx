import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { api } from '../api';
import { PageHeader } from '../components/PageHeader';
import { useAsyncData } from '../components/useAsyncData';
import type { AppContext } from '../App';

type Benchmark = {
  industry: string;
  sample_factory_count: number;
  metrics: { metric: string; factory_value: number; industry_median: number; top25: number; conclusion: string }[];
  hot_roles: { name: string; value: number }[];
};

type Recommendation = { id: string; title: string; content: string; severity: string };

export function IndustryPage({ context }: { context: AppContext }) {
  const benchmark = useAsyncData(() => api<Benchmark>('/api/industry/benchmarks', { token: context.token }), [context.token]);
  const recs = useAsyncData(() => api<Recommendation[]>('/api/industry/recommendations', { token: context.token }), [context.token]);

  return (
    <>
      <PageHeader title="行业分析" description="基于匿名聚合数据，为同类型 AI 玩具工厂提供同行对比和优化建议。" />
      <div className="grid two">
        <div className="panel">
          <div className="panel-title">行业热门角色类型</div>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={benchmark.data?.hot_roles || []}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#0f766e" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="panel">
          <div className="panel-title">匿名样本说明</div>
          <p>行业：{benchmark.data?.industry || '-'}</p>
          <p>样本工厂数：{benchmark.data?.sample_factory_count || 0}</p>
          <p className="muted">这里只展示匿名、聚合、分桶后的指标，不展示任何具体工厂、SN、Prompt 或对话内容。</p>
        </div>
      </div>
      <div className="panel">
        <div className="panel-title">本工厂 vs 行业基准</div>
        <table>
          <thead>
            <tr><th>指标</th><th>本工厂</th><th>行业中位数</th><th>行业前 25%</th><th>结论</th></tr>
          </thead>
          <tbody>
            {(benchmark.data?.metrics || []).map((item) => (
              <tr key={item.metric}>
                <td>{item.metric}</td>
                <td>{item.factory_value}</td>
                <td>{item.industry_median}</td>
                <td>{item.top25}</td>
                <td>{item.conclusion}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="panel">
        <div className="panel-title">优化建议</div>
        <div className="stack">
          {(recs.data || []).map((item) => (
            <div className="suggestion" key={item.id}>
              <strong>{item.title}</strong>
              <p>{item.content}</p>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}
