import{runStatus,reviewStatus}from '../../constants/enums';
const reportStatus={active:'有效',invalidated:'已失效'};
const supplementStatus={applied:'已应用',no_change:'无变更',quarantined:'含隔离'};
export function StatusBadge({status}:{status:string}){const names:Record<string,string>={...runStatus,...reviewStatus,...reportStatus,...supplementStatus};return <span className={'badge '+status}>{names[status]||status}</span>}
