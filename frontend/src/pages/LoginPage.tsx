import { useState } from 'react';
import { post } from '../api';
import type { User } from '../types';

export function LoginPage({ onLogin }: { onLogin: (token: string, user: User) => void }) {
  const [account, setAccount] = useState('factory-a@voicebox.ai');
  const [password, setPassword] = useState('123456');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    setError('');
    try {
      const result = await post<{ token: string; user: User }>('/api/auth/login', { account, password });
      onLogin(result.token, result.user);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-screen">
      <form className="login-card" onSubmit={submit}>
        <div className="brand-mark large">VB</div>
        <h1>AI 语音硬件 ToB SaaS 控制台</h1>
        <p>管理工厂租户、ESP32 设备、AI 角色 Prompt、对话链路和行业洞察。</p>
        <label>
          账号
          <input value={account} onChange={(event) => setAccount(event.target.value)} />
        </label>
        <label>
          密码
          <input type="password" value={password} onChange={(event) => setPassword(event.target.value)} />
        </label>
        {error && <div className="form-error">{error}</div>}
        <button className="primary-button" disabled={loading}>{loading ? '登录中...' : '登录'}</button>
        <div className="login-hints">
          <span>平台：admin@voicebox.ai</span>
          <span>工厂：factory-a@voicebox.ai</span>
          <span>工程：engineer@voicebox.ai</span>
        </div>
      </form>
    </div>
  );
}
