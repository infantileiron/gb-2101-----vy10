import{request,post}from './client';import type{Run}from '../types/entities';
export const runsApi={list:()=>request<Run[]>('/runs'),create:(experiment_id:string)=>post<Run>('/runs',{experiment_id})};
