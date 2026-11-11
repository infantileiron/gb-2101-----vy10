import{request,post,download}from './client';import type{Report}from '../types/entities';
export const reportsApi={list:()=>request<Report[]>('/reports'),create:(run_id:string,review_id:string,title:string)=>post<Report>('/reports',{run_id,review_id,title}),download:(id:string)=>download('/reports/'+id+'/download',id+'.csv')};
