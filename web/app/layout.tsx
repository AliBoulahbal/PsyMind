import "./globals.css";
export const metadata={title:"PsyMind V2",description:"Clinical SaaS"};
export default function RootLayout({children}:{children:React.ReactNode}){
 return <html lang="fr"><body>{children}</body></html>
}
