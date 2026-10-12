"use client";
import { useState } from "react";
import { login } from "@/lib/api";
import { BrainCircuit, ShieldCheck } from "lucide-react";

export default function Login() {
  const [tenant, setTenant] = useState("demo-center");
  const [email, setEmail] = useState("admin@psymind.local");
  const [password, setPassword] = useState("ChangeMe123!");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError("");
    
    try {
      await login(tenant, email, password);
      location.href = "/dashboard";
    } catch (e: any) {
      console.error("Login exception:", e);
      
      // Safely parse the error to prevent [object Object] rendering
      let errorMsg = "Une erreur d'authentification s'est produite.";
      
      if (e?.message) {
        if (typeof e.message === "string" && e.message !== "[object Object]") {
          errorMsg = e.message;
        } else if (typeof e.message === "object") {
          errorMsg = e.message.detail || JSON.stringify(e.message);
        } else if (e.message === "[object Object]") {
          errorMsg = "Identifiants incorrects ou accès refusé.";
        }
      } else if (typeof e === "string") {
        errorMsg = e;
      }
      
      setError(errorMsg);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login">
      <section className="loginhero">
        <BrainCircuit size={48} />
        <h1 style={{ fontSize: 48, marginBottom: 8 }}>PsyMind</h1>
        <p style={{ fontSize: 20, maxWidth: 600, color: "#cbd7f7" }}>
          Dossier clinique, RAG documentaire et aide IA supervisée dans une plateforme multi-tenant sécurisée.
        </p>
        <p>
          <ShieldCheck size={18} /> Les décisions cliniques critiques restent humaines.
        </p>
      </section>
      
      <section className="loginpanel">
        <form className="loginbox form" onSubmit={submit}>
          <div className="eyebrow">Espace clinique</div>
          <h1>Connexion</h1>
          <p className="muted">Accédez à votre centre PsyMind.</p>
          
          <label>
            Centre
            <input className="input" value={tenant} onChange={e => setTenant(e.target.value)} />
          </label>
          
          <label>
            Email
            <input className="input" type="email" value={email} onChange={e => setEmail(e.target.value)} />
          </label>
          
          <label>
            Mot de passe
            <input className="input" type="password" value={password} onChange={e => setPassword(e.target.value)} />
          </label>
          
          {error && <div className="error">{error}</div>}
          
          <button className="btn primary" disabled={busy}>
            {busy ? "Connexion…" : "Se connecter"}
          </button>
          
          <div className="notice">
            Les identifiants préremplis sont exclusivement ceux de la démo locale synthétique.
          </div>
        </form>
      </section>
    </div>
  );
}