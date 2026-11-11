import{request,post}from './client';import type{Experiment}from '../types/entities';
export const experimentsApi={list:()=>request<Experiment[]>('/experiments'),create:(data:unknown)=>post<Experiment>('/experiments',data)};
