export const routes=[{key:'overview',label:'实验总览',index:'01'},{key:'datasets',label:'数据批次',index:'02'},{key:'design',label:'试验设计',index:'03'},{key:'results',label:'计算结果',index:'04'},{key:'reviews',label:'研发复核',index:'05'},{key:'reports',label:'成果归档',index:'06'}]as const;
export type Route=typeof routes[number]['key'];
