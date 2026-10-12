"use client";
export default function Modal({title,children,onClose}:{title:string;children:React.ReactNode;onClose:()=>void}){
 return <div className="modalback" onMouseDown={onClose}><div className="modal" onMouseDown={e=>e.stopPropagation()}><div style={{display:"flex",justifyContent:"space-between",alignItems:"center"}}><h2>{title}</h2><button className="btn secondary" onClick={onClose}>Fermer</button></div>{children}</div></div>
}
