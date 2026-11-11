import{request,post}from './client';import type{Dataset}from '../types/entities';
export const datasetsApi={list:()=>request<Dataset[]>('/datasets'),detail:(id:string)=>request<Dataset>('/datasets/'+id),create:(data:unknown)=>post<Dataset>('/datasets',data)};
