export const number=(x:number|undefined,d=2)=>x===undefined?'—':x.toFixed(d);
export const date=(x:string)=>new Date(x).toLocaleString('zh-CN',{month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit'});
