"use client";
import {useState} from "react";import {token} from "@/lib/api";
const BASE=process.env.NEXT_PUBLIC_API_URL||"http://localhost:8000/api/v1";
export default function DocumentUpload({patientId,onDone}:{patientId:string;onDone:()=>void}){
 const [file,setFile]=useState<File|null>(null),[busy,setBusy]=useState(false),[msg,setMsg]=useState("");
 async function upload(e:React.FormEvent){e.preventDefault();if(!file)return;setBusy(true);setMsg("");
  const fd=new FormData();fd.append("file",file);fd.append("title",file.name);
  const r=await fetch(`${BASE}/documents/patients/${patientId}/upload`,{method:"POST",headers:{Authorization:`Bearer ${token()}`},body:fd});
  const data=await r.json();setBusy(false);if(!r.ok){setMsg(typeof data.detail==="string"?data.detail:JSON.stringify(data.detail));return}
  setMsg(`${data.chunks} fragments indexés.`);setFile(null);onDone();
 }
 return <form className="form" onSubmit={upload}><label>PDF, DOCX ou TXT<input className="input" type="file" accept=".pdf,.docx,.txt" onChange={e=>setFile(e.target.files?.[0]||null)}/></label><button className="btn primary" disabled={!file||busy}>{busy?"Extraction & indexation…":"Importer et indexer"}</button>{msg&&<div className="notice">{msg}</div>}</form>
}
