import { useState } from 'react';
import { MessageCircle, Search, ShieldCheck, Timer } from 'lucide-react';
import { api, post } from '../api';
import { PageHeader } from '../components/PageHeader';
import { StatusBadge } from '../components/StatusBadge';
import { useAsyncData } from '../components/useAsyncData';
import type { AppContext } from '../App';
import type { Conversation, ConversationTurn } from '../types';

type TraceResponse = { turn: ConversationTurn; trace: Record<string, number> };

export function ConversationsPage({ context }: { context: AppContext }) {
  const suffix = context.factoryQuery ? `?${context.factoryQuery}` : '';
  const conversations = useAsyncData(() => api<Conversation[]>(`/api/conversations${suffix}`, { token: context.token }), [context.token, context.factoryQuery]);
  const badcases = useAsyncData(() => api<ConversationTurn[]>(`/api/badcases${suffix}`, { token: context.token }), [context.token, context.factoryQuery]);
  const [trace, setTrace] = useState<TraceResponse | null>(null);
  const [selected, setSelected] = useState<Conversation | null>(null);
  const [keyword, setKeyword] = useState('');
  const showFactory = context.user.role_code === 'super_admin' && !context.selectedFactoryId;

  const filteredConversations = (conversations.data || []).filter((item) => {
    const text = `${item.factory_name || ''} ${item.device_sn} ${item.character_name} ${item.bound_user?.nickname || ''} ${item.anonymous_user_label} ${item.anonymous_session_id}`.toLowerCase();
    return text.includes(keyword.toLowerCase());
  });

  async function openTrace(conversationId: string) {
    const detail = await api<Conversation>('/api/conversations/' + conversationId, { token: context.token });
    setSelected(detail);
    if (detail.turns?.[0]) {
      setTrace(await api<TraceResponse>(`/api/conversation-turns/${detail.turns[0].id}/trace`, { token: context.token }));
    }
  }

  return (
    <>
      <PageHeader title="对话运营" description="查看设备绑定用户的聊天记录，每条回复附带 E2E 首句延迟。平台管理员可跨工厂查看全部数据。" />

      <div className="conversation-layout">
        <div className="panel elevated conversation-list">
          <div className="panel-title"><MessageCircle size={18} />用户会话记录</div>
          <div className="searchbox full">
            <Search size={16} />
            <input placeholder="搜索工厂 / SN / 绑定用户 / 会话" value={keyword} onChange={(event) => setKeyword(event.target.value)} />
          </div>
          <div className="session-list">
            {filteredConversations.map((item) => (
              <button key={item.id} className={selected?.id === item.id ? 'session-card active' : 'session-card'} onClick={() => openTrace(item.id)}>
                <div>
                  <strong>{item.bound_user?.nickname || item.anonymous_user_label || item.anonymous_session_id}</strong>
                  <span>{showFactory && item.factory_name ? `${item.factory_name} · ` : ''}{item.device_sn} · {item.character_name}</span>
                </div>
                <div className="session-meta">
                  <span>{item.total_turns} 轮</span>
                  <StatusBadge value={item.success ? 'resolved' : 'open'} />
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="panel elevated transcript-panel">
          <div className="panel-title"><ShieldCheck size={18} />聊天记录详情</div>
          {!selected ? (
            <div className="empty-state">选择左侧会话后查看完整聊天记录。</div>
          ) : (
            <>
              <div className="transcript-summary">
                <div><span>绑定用户</span><strong>{selected.bound_user?.nickname || selected.anonymous_user_label || '-'}</strong></div>
                <div><span>用户分层</span><strong>{selected.user_segment}</strong></div>
                <div><span>设备 SN</span><strong>{selected.device_sn}</strong></div>
                {showFactory && <div><span>工厂</span><strong>{selected.factory_name || '-'}</strong></div>}
                <div><span>总延迟</span><strong>{selected.total_latency_ms} ms</strong></div>
              </div>
              <div className="chat-thread">
                {(selected.turns || []).map((turn) => (
                  <div className="turn-block" key={turn.id}>
                    <div className="chat-line user">
                      <span>用户 ASR</span>
                      <p>{turn.user_asr_text}</p>
                    </div>
                    <div className="chat-line ai">
                      <span>AI 回复</span>
                      <p>{turn.ai_reply_text}</p>
                    </div>
                    <div className="turn-meta">
                      <span><Timer size={14} />E2E {turn.e2e_first_response_ms ?? turn.latency_total_ms} ms</span>
                      <span>意图：{turn.intent}</span>
                      {turn.fallback_hit && <StatusBadge value="medium" />}
                      {turn.safety_hit && <StatusBadge value="high" />}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </div>

      <div className="panel elevated">
        <div className="panel-title">全部对话记录</div>
        {conversations.loading ? '加载对话...' : (
          <table className="data-table">
            <thead>
              <tr>
                <th>时间</th>
                {showFactory && <th>工厂</th>}
                <th>绑定用户</th>
                <th>设备 SN</th>
                <th>角色</th>
                <th>轮数</th>
                <th>总延迟</th>
                <th>状态</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {filteredConversations.map((item) => (
                <tr key={item.id}>
                  <td>{item.started_at.slice(5, 16)}</td>
                  {showFactory && <td>{item.factory_name}</td>}
                  <td>{item.bound_user?.nickname || item.anonymous_user_label}</td>
                  <td>{item.device_sn}</td>
                  <td>{item.character_name}</td>
                  <td>{item.total_turns}</td>
                  <td>{item.total_latency_ms} ms</td>
                  <td><StatusBadge value={item.success ? 'resolved' : 'open'} /></td>
                  <td><button className="link-button" onClick={() => openTrace(item.id)}>查看详情</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      {trace && (
        <div className="panel elevated">
          <div className="panel-title">链路耗时 Trace · {trace.turn.trace_id}</div>
          <div className="trace-row">
            {Object.entries(trace.trace).map(([key, value]) => (
              <div className="trace-step" key={key}><span>{key}</span><strong>{value} ms</strong></div>
            ))}
          </div>
        </div>
      )}
      <div className="panel elevated">
        <div className="panel-title">Badcase 分析</div>
        <table className="data-table">
          <thead>
            <tr><th>类型</th><th>设备</th><th>角色</th><th>用户文本</th><th>E2E 延迟</th><th>错误码</th><th></th></tr>
          </thead>
          <tbody>
            {(badcases.data || []).map((item) => (
              <tr key={item.id}>
                <td>{item.badcase_type}</td>
                <td>{item.device_sn}</td>
                <td>{item.character_name}</td>
                <td>{item.user_asr_text}</td>
                <td>{item.e2e_first_response_ms ?? item.latency_total_ms} ms</td>
                <td>{item.error_code || '-'}</td>
                <td><button className="link-button" onClick={() => post(`/api/badcases/${item.id}/mark`, { status: 'reviewed' }, context.token)}>标记已看</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
