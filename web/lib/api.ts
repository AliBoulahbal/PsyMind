const BASE=process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";
export type Patient={id:string;file_number:string;display_name:string;birth_date?:string;sex?:string;status:string;created_at?:string};
export function token(){return typeof window==="undefined"?null:localStorage.getItem("psymind_access")}
export async function api<T=any>(path:string,options:RequestInit={}):Promise<T>{
 const headers=new Headers(options.headers||{}); headers.set("Content-Type","application/json");
 const t=token(); if(t) headers.set("Authorization",`Bearer ${t}`);
 const r=await fetch(`${BASE}${path}`,{...options,headers,cache:"no-store"});
 if(r.status===401 && typeof window!=="undefined"){localStorage.removeItem("psymind_access");window.location.href="/login";throw new Error("Session expirée")}
 if(!r.ok){let m=`Erreur ${r.status}`;try{const j=await r.json();m=j.detail||m}catch{}throw new Error(m)}
 return r.json();
}
export async function login(tenant_slug:string,email:string,password:string){
 const data=await api<{access_token:string;refresh_token:string}>("/auth/login",{method:"POST",body:JSON.stringify({tenant_slug,email,password})});
 localStorage.setItem("psymind_access",data.access_token);localStorage.setItem("psymind_refresh",data.refresh_token);return data;
}
export function logout(){localStorage.removeItem("psymind_access");localStorage.removeItem("psymind_refresh");location.href="/login"}
