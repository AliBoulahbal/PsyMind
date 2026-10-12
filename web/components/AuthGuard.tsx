"use client";
import {useEffect,useState} from "react";
export default function AuthGuard({children}:{children:React.ReactNode}){
 const [ok,setOk]=useState(false);
 useEffect(()=>{if(!localStorage.getItem("psymind_access")) location.href="/login"; else setOk(true)},[]);
 if(!ok)return <div className="empty">Vérification de la session…</div>; return <>{children}</>
}
