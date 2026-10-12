"use client";
import Link from "next/link"; import {usePathname} from "next/navigation";
import {LayoutDashboard,Users,Brain,ClipboardCheck,ShieldCheck,Activity,LogOut,Stethoscope,Pill} from "lucide-react";
import {logout} from "@/lib/api";
const nav=[
 ["/dashboard","Dashboard",LayoutDashboard],["/patients","Patients",Users],["/catalogs","Référentiels",Pill],
 ["/assistant","Assistant IA",Brain],["/approvals","Validations HITL",ClipboardCheck],
 ["/governance","Gouvernance IA",ShieldCheck],["/audit","Audit",ShieldCheck],["/usage","Usage IA",Activity]
] as const;
export default function AppShell({children}:{children:React.ReactNode}){
 const path=usePathname();
 return <div className="app"><aside className="sidebar">
  <div className="brand"><div className="brandmark"><Stethoscope size={20}/></div><span>PsyMind</span></div>
  <nav className="nav">{nav.map(([href,label,I])=><Link className={path.startsWith(href)?"active":""} href={href} key={href}><I size={19}/><span className="label">{label}</span></Link>)}</nav>
 </aside><main className="main"><header className="topbar"><div><b>PsyMind Clinical</b><div className="muted" style={{fontSize:12}}>Human-supervised clinical support</div></div><button className="btn secondary" onClick={logout}><LogOut size={15}/> Déconnexion</button></header><div className="content">{children}</div></main></div>
}
