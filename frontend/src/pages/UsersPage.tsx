import { useState } from 'react';
import { Plus } from 'lucide-react';
import { api, post } from '../api';
import { PageHeader } from '../components/PageHeader';
import { StatusBadge } from '../components/StatusBadge';
import { useAsyncData } from '../components/useAsyncData';
import type { AppContext } from '../App';
import type { Role, User } from '../types';

export function UsersPage({ context }: { context: AppContext }) {
  const users = useAsyncData(() => api<User[]>('/api/admin-users', { token: context.token }), [context.token]);
  const roles = useAsyncData(() => api<Role[]>('/api/roles', { token: context.token }), [context.token]);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('operator');

  async function createUser() {
    if (!name || !email) return;
    const row = await post<User>('/api/admin-users', { name, email, role_code: role }, context.token);
    users.setData([...(users.data || []), row]);
    setName('');
    setEmail('');
  }

  return (
    <>
      <PageHeader title="后台用户管理" description="只管理工厂后台账号，不建立消费者用户体系。" />
      <div className="toolbar">
        <input placeholder="姓名" value={name} onChange={(event) => setName(event.target.value)} />
        <input placeholder="邮箱" value={email} onChange={(event) => setEmail(event.target.value)} />
        <select value={role} onChange={(event) => setRole(event.target.value)}>
          {(roles.data || []).filter((item) => item.code !== 'super_admin').map((item) => <option key={item.code} value={item.code}>{item.name}</option>)}
        </select>
        <button className="primary-button compact" onClick={createUser}><Plus size={16} />新增账号</button>
      </div>
      <div className="panel">
        <table>
          <thead>
            <tr><th>姓名</th><th>邮箱</th><th>手机</th><th>角色</th><th>状态</th><th>最近登录</th></tr>
          </thead>
          <tbody>
            {(users.data || []).map((item) => (
              <tr key={item.id}>
                <td>{item.name}</td>
                <td>{item.email}</td>
                <td>{item.phone || '-'}</td>
                <td>{item.role.name}</td>
                <td><StatusBadge value={item.status} /></td>
                <td>{item.last_login_at?.slice(0, 16) || '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
