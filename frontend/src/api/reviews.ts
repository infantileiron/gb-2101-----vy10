import{request,post}from './client';import type{Review}from '../types/entities';
export const reviewsApi={list:()=>request<Review[]>('/reviews'),create:(run_id:string,comment:string)=>post<Review>('/reviews',{run_id,comment}),decide:(id:string,status:string,comment:string)=>request<Review>('/reviews/'+id,{method:'PATCH',body:JSON.stringify({status,comment})})};
