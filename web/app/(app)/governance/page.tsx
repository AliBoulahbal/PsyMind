"use client";
import {useEffect,useState} from "react";import {api} from "@/lib/api";
export default function Governance(){
 const [models,setModels]=useState<any[]>([]),[flags,setFlags]=useState<any[]>([]),[knowledge,setKnowledge]=useState<any[]>([]),[err,setErr]=useState("");
 const load=()=>{api<any[]>("/governance/models").then(setModels).catch(e=>setErr(e.message));api<any[]>("/governance/flags").then(setFlags);api<any[]>("/governance/knowledge").then(setKnowledge)};useEffect(load,[]);
 async function flag(key:string,enabled:boolean){await api(`/governance/flags/${key}`,{method:"PUT",body:JSON.stringify({enabled,config:{}})});load()}
 return <><div className="eyebrow">AI Governance Center</div><h1 className="title">Gouvernance & modèles</h1><p className="muted">Promotion contrôlée des modèles, feature flags et connaissances institutionnelles.</p>{err&&<p className="error">{err}</p>}
 <div className="grid grid2" style={{marginTop:18}}>
 <div className="card"><h3>Model Registry</h3>{models.map(x=><div key={x.id} style={{padding:"10px 0",borderBottom:"1px solid #eee"}}><b>{x.name}</b><div className="muted">{x.provider} · {x.model_ref}</div><span className={x.status==="approved"?"badge":"badge warn"}>{x.status}</span></div>)}{!models.length&&<div className="empty">Aucun modèle enregistré.</div>}</div>
 <div className="card"><h3>Feature Flags</h3>{["ai_assistant","agents","risk_module","shadow_ai"].map(k=>{const x=flags.find(f=>f.key===k);return <div key={k} className="toolbar"><span>{k}</span><button className={x?.enabled?"btn primary":"btn secondary"} onClick={()=>flag(k,!x?.enabled)}>{x?.enabled?"Activé":"Désactivé"}</button></div>})}</div>
 <div className="card"><h3>Knowledge Base</h3>{knowledge.map(x=><p key={x.id}><b>{x.title}</b> · v{x.version} <span className="badge">{x.status}</span></p>)}{!knowledge.length&&<div className="empty">Aucune source institutionnelle versionnée.</div>}</div>
 <div className="card"><h3>Safety Gates</h3><p>✓ RLS/FORCE RLS</p><p>✓ Prompt-injection baseline</p><p>✓ Grounding/citations</p><p>✓ HITL actions critiques</p><p>✓ AI disaster mode</p><p className="muted">PII Vault et audit externe doivent être configurés en production.</p></div>
 </div></>
}
