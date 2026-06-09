import { Activity, Gauge, TimerReset } from 'lucide-react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { api } from '../api';
import { PageHeader } from '../components/PageHeader';
import { StatusBadge } from '../components/StatusBadge';
import { useAsyncData } from '../components/useAsyncData';
import type { AppContext } from '../App';

type LatencyData = {
  summary: { label: string; value: number; unit: string; status: string }[];
  breakdown: { stage: string; avg: number; p95: number }[];
  slow_traces: { trace_id: string; device_sn: string; character_name: string; e2e_first_response_ms: number; asr_ms: number; llm_ttft_ms: number; tts_first_audio_ms: number; created_at: string }[];
};

const stageName: Record<string, string> = {
  vad_ms: 'VAD',
  upload_ms: '上传',
  asr_ms: 'ASR',
  llm_ttft_ms: 'LLM 首 token',
  llm_total_ms: 'LLM 总耗时',
  tts_first_audio_ms: 'TTS 首包',
  playback_start_ms: '播放启动',
  e2e_first_response_ms: 'E2E 首句',
};

export function LatencyPage({ context }: { context: AppContext }) {
  const suffix = context.factoryQuery ? `?${context.factoryQuery}` : '';
  const { data, loading } = useAsyncData(() => api<LatencyData>(`/api/observability/latency${suffix}`, { token: context.token }), [context.token, context.factoryQuery]);
  const breakdown = (data?.breakdown || []).map((item) => ({ ...item, stageLabel: stageName[item.stage] || item.stage }));

  return (
    <>
      <PageHeader title="链路观测" description="拆解 VAD、上传、ASR、LLM、TTS 到设备播放的首句延迟，定位体验瓶颈。" />
      {loading ? <div className="panel">加载链路指标...</div> : (
        <>
          <div className="insight-strip">
            <div className="insight-main">
              <Activity size={28} />
              <div>
                <span>当前链路健康度</span>
                <strong>需要关注 LLM TTFT 与弱网上传</strong>
              </div>
            </div>
            <div className="insight-copy">P95 投诉通常来自尾部链路，而不是平均延迟。这里优先展示最慢 trace 和各阶段 P95。</div>
          </div>

          <div className="quality-grid">
            {(data?.summary || []).map((item) => (
              <div className="quality-card" key={item.label}>
                <div className="quality-icon"><Gauge size={18} /></div>
                <span>{item.label}</span>
                <strong>{item.value}<small>{item.unit}</small></strong>
                <StatusBadge value={item.status === 'normal' ? 'low' : 'medium'} />
              </div>
            ))}
          </div>

          <div className="grid two">
            <div className="panel elevated">
              <div className="panel-title"><TimerReset size={18} />阶段耗时 Avg / P95</div>
              <ResponsiveContainer width="100%" height={320}>
                <BarChart data={breakdown}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="stageLabel" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="avg" fill="#2563eb" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="p95" fill="#f59e0b" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="panel elevated">
              <div className="panel-title">最慢 Trace 排行</div>
              <table className="data-table">
                <thead>
                  <tr><th>Trace</th><th>设备</th><th>角色</th><th>E2E</th><th>LLM TTFT</th></tr>
                </thead>
                <tbody>
                  {(data?.slow_traces || []).map((item) => (
                    <tr key={item.trace_id}>
                      <td>{item.trace_id}</td>
                      <td>{item.device_sn}</td>
                      <td>{item.character_name}</td>
                      <td><strong>{item.e2e_first_response_ms} ms</strong></td>
                      <td>{item.llm_ttft_ms} ms</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </>
  );
}
