import type{Domain}from '../stores/domain';import{PageTitle}from '../components/common/PageTitle';import{StatusBadge}from '../components/common/StatusBadge';import{TrialSummary}from '../components/TrialSummary';import{RunChart}from '../components/RunChart';import{EmptyState}from '../components/common/EmptyState';
export function Overview({data}:{data:Domain}){
  const valid=data.runs.filter(r=>r.status==='completed');
  const run=valid.sort((a,b)=>b.dataset_version-a.dataset_version)[0];
  const invalidCount=data.runs.filter(r=>r.status==='invalidated').length;
  return <><PageTitle eyebrow="RESEARCH NOTEBOOK / 2026.11" title="保鲜包装，先验证再决定。">青禾鲜品成都研发组 · 鲜切叶菜封膜 B 随机对照试验</PageTitle>
  <div className="overview-grid"><div><div className="section-title"><h2>当前研究 · 封膜 B</h2><span className="stamp">站点分层 / A-B · 数据 v{run?.dataset_version??'—'}</span></div>
  {run?<><TrialSummary run={run}/><RunChart result={run.result}/></>:<EmptyState>先在试验设计页创建并运行一个分析。</EmptyState>}
  {invalidCount>0&&<p className="quarantine-note">{invalidCount} 个历史运行因源数据补报已失效，旧版依据仍可在“计算结果”页追溯；请以当前数据版本的重算结果为准。</p>}
  </div><aside className="field-note"><p className="eyebrow">FIELD CONTEXT</p><h2>保持新鲜，<br/>也保持审慎。</h2><p>3 个冷链站点的环境不同。分析在站点内置换组标签，避免站点差异淹没包装本身的效果。</p><dl><dt>观测批次</dt><dd>{data.datasets.reduce((n,d)=>n+d.row_count,0)} 批</dd><dt>待研发复核</dt><dd>{data.reviews.filter(r=>r.status==='pending').length} 份</dd><dt>已归档成果</dt><dd>{data.reports.filter(r=>r.status!=='invalidated').length} 份</dd></dl><p className="small">统计显著性是证据的一部分。采购决策仍需结合成本、运输损耗与适用范围。</p></aside></div></>}
