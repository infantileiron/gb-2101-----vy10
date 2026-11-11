import {post,request} from './client';import type{User}from '../types/entities';
export const login=(email:string,password:string)=>post<{access_token:string;user:User}>('/auth/login',{email,password});
export const me=()=>request<User>('/auth/me');
