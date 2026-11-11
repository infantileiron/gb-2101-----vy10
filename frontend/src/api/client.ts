export async function request<T>(path:string,options:RequestInit={}):Promise<T>{
 const token=localStorage.getItem('fresh-token');
 const response=await fetch('/api'+path,{...options,headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{}),...options.headers}});
 if(!response.ok){const body=await response.json().catch(()=>({detail:'网络暂时不可用'}));throw new Error(typeof body.detail==='string'?body.detail:JSON.stringify(body.detail));}
 return response.json();
}
export const post=<T>(path:string,body:unknown)=>request<T>(path,{method:'POST',body:JSON.stringify(body)});
export async function download(path:string,filename:string){
 const r=await fetch('/api'+path,{headers:{Authorization:'Bearer '+localStorage.getItem('fresh-token')}});
 if(!r.ok)throw new Error('下载失败，请检查复核状态');
 const url=URL.createObjectURL(await r.blob());const a=document.createElement('a');a.href=url;a.download=filename;a.click();URL.revokeObjectURL(url);
}
