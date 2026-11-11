import { useState } from 'react';
import type { Domain } from '../stores/domain';
import { domainStore } from '../stores/domain';
import { PageTitle } from '../components/common/PageTitle';
import { StatusBadge } from '../components/common/StatusBadge';
import { TrialSummary } from '../components/TrialSummary';
import { EmptyState } from '../components/common/EmptyState';

export function Reviews({ data, admin, act, busy }: { data: Domain; admin: boolean; act: (f: () => Promise<unknown>) => Promise<void>; busy: boolean }) {
  const [comment, setComment] = useState('站点分层口径已核对，建议结合包装成本进入下一轮验证。');
  if (!data.reviews.length) {
    return <>
      <PageTitle eyebrow="05 / RESEARCH REVIEW" title="让统计证据，接受业务复核。">源数据更新后，建立在旧分析上的复核自动失效、停止审批；请等待新版本数据的重算结果重新提交。</PageTitle>
      <EmptyState>在计算结果中填写业务解释，再提交研发复核。</EmptyState>
    </>;
  }
  return <>
    <PageTitle eyebrow="05 / RESEARCH REVIEW" title="让统计证据，接受业务复核。">源数据更新后，建立在旧分析上的复核自动失效、停止审批；请等待新版本数据的重算结果重新提交。</PageTitle>
    {data.reviews.map(review => {
      const run = data.runs.find(r => r.id === review.run_id);
      const invalid = review.status === 'invalidated';
      return <section className="sheet" key={review.id}>
        <div className="section-title">
          <h2>{data.experiments.find(e => e.id === run?.experiment_id)?.name || review.run_id}</h2>
          <StatusBadge status={review.status} />
        </div>
        {invalid && <div className="invalid-banner">
          <b>该复核依据的旧分析已失效，复核同步失效且不能继续审批。</b>
          {review.invalidated_reason}<br />
          失效时间：{new Date(review.invalidated_at).toLocaleString('zh-CN')} · 对应运行数据版本 v{run?.dataset_version}。
        </div>}
        {run && run.status === 'completed' && <TrialSummary run={run} />}
        {run && run.status !== 'completed' && (
          <p className="muted">关联运行状态：{run.status}（数据版本 v{run.dataset_version}），旧版统计依据仍可在计算结果页查看。</p>
        )}
        <p>{review.comment}</p>
        <p className="small">复核编号 {review.id} · {review.reviewer || '等待研发负责人'}</p>
        {admin && review.status === 'pending' && <>
          <label>复核意见<textarea value={comment} onChange={e => setComment(e.target.value)} minLength={5} /></label>
          <div className="actions">
            <button disabled={busy} onClick={() => act(() => domainStore.reviews.decide(review.id, 'approved', comment))}>通过复核</button>
            <button className="secondary" disabled={busy} onClick={() => act(() => domainStore.reviews.decide(review.id, 'rejected', comment))}>退回补充</button>
          </div>
        </>}
      </section>;
    })}
  </>;
}
