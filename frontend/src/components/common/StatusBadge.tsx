import{runStatus,reviewStatus}from '../../constants/enums';
export function StatusBadge({status}:{status:string}){const names:Record<string,string>={...runStatus,...reviewStatus};return <span className={'badge '+status}>{names[status]||status}</span>}
