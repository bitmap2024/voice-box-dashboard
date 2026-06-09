import { useEffect, useState } from 'react';
import { ArrowLeft, Timer } from 'lucide-react';
import { api } from '../api';
import { PageHeader } from '../components/PageHeader';
import { StatusBadge } from '../components/StatusBadge';
import type { AppContext } from '../App';
import type { Conversation, ConversationTurn } from '../types';

type TraceResponse = { turn: ConversationTurn; trace: Record<string, number> };

export function ConversationDetailPage({ context, id }: { context: AppContext; id: string }) {
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTurnId, setActiveTurnId] = useState<string | null>(null);
  const [trace, setTrace] = useState<TraceResponse | null>(null);

  useEffect(() => {
    setLoading(true);
    api<Conversation>(`/api/conversations/${id}`, { token: context.token })
      .then(async (detail) => {
        setConversation(detail);
        const firstTurn = detail.turns?.[0];
        if (firstTurn) {
          setActiveTurnId(firstTurn.id);
          setTrace(await api<TraceResponse>(`/api/conversation-turns/${firstTurn.id}/trace`, { token: context.token }));
        } else {
          setActiveTurnId(null);
          setTrace(null);
        }
      })
      .finally(() => setLoading(false));
  }, [id, context.token]);

  async function selectTurn(turnId: string) {
    setActiveTurnId(turnId);
    setTrace(await api<TraceResponse>(`/api/conversation-turns/${turnId}/trace`, { token: context.token }));
  }

  if (loading || !conversation) {
    return <div className="panel">加载会话详情...</div>;
  }

  const activeTurn = conversation.turns?.find((t) => t.id === activeTurnId);

  return (
    <>
      <PageHeader
        title="会话详细分析"
        description={`${conversation.bound_user?.nickname || conversation.anonymous_user_label || '-'} · ${conversation.device_sn} · ${conversation.started_at?.slice(0, 16).replace('T', ' ')}`}
        action={
          <button
            className="ghost-button"
            onClick={() => {
              const endUserId = conversation.bound_user?.id;
              if (endUserId) {
                context.navigate({ page: 'user-chat-history', endUserId });
              } else {
                context.navigate({ page: 'user-ops' });
              }
            }}
          >
            <ArrowLeft size={16} />返回
          </button>
        }
      />

      <div className="transcript-summary">
        <div><span>用户分层</span><strong>{conversation.user_segment || '-'}</strong></div>
        <div><span>总轮数</span><strong>{conversation.total_turns}</strong></div>
        <div><span>会话总延迟</span><strong>{conversation.total_latency_ms} ms</strong></div>
      </div>

      <div className="panel elevated full-page-table" style={{ marginTop: '1rem' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th>轮次</th>
              <th>用户 ASR</th>
              <th>AI 回复</th>
              <th>意图</th>
              <th>E2E 延迟</th>
              <th>标记</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {(conversation.turns || []).map((turn, index) => (
              <tr key={turn.id} className={activeTurnId === turn.id ? 'row-active' : ''}>
                <td>第 {index + 1} 轮</td>
                <td>{turn.user_asr_text}</td>
                <td>{turn.ai_reply_text}</td>
                <td>{turn.intent || '-'}</td>
                <td>
                  <Timer size={14} style={{ display: 'inline', marginRight: 4 }} />
                  {turn.e2e_first_response_ms ?? turn.latency_total_ms} ms
                </td>
                <td>
                  {turn.fallback_hit && <StatusBadge value="medium" />}
                  {turn.safety_hit && <StatusBadge value="high" />}
                  {!turn.success && <StatusBadge value="open" />}
                </td>
                <td>
                  <button className="link-button" onClick={() => selectTurn(turn.id)}>链路</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {trace && (
        <div className="panel elevated" style={{ marginTop: '1rem' }}>
          <div className="panel-title">链路 Trace · {trace.turn.trace_id}</div>
          <div className="trace-row">
            {Object.entries(trace.trace).map(([key, value]) => (
              <div className="trace-step" key={key}>
                <span>{key}</span>
                <strong>{value} ms</strong>
              </div>
            ))}
          </div>

          {trace.turn.llm_context && (
            <div style={{ marginTop: '1rem' }}>
              <div className="panel-title">LLM Context</div>
              <pre className="context-block">{trace.turn.llm_context}</pre>
            </div>
          )}

          <div className="conversation-bubble" style={{ marginTop: '1rem' }}>
            <strong>用户：</strong>{trace.turn.user_asr_text}
            <br />
            <strong>AI：</strong>{trace.turn.ai_reply_text}
          </div>
        </div>
      )}

      {!trace && activeTurn && (
        <div className="panel elevated" style={{ marginTop: '1rem' }}>
          <div className="conversation-bubble">
            <strong>用户：</strong>{activeTurn.user_asr_text}
            <br />
            <strong>AI：</strong>{activeTurn.ai_reply_text}
          </div>
        </div>
      )}
    </>
  );
}
