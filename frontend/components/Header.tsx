import Link from "next/link";
const Header = () => (
  <header className="w-full flex items-center justify-between py-4 px-6 border-b border-border bg-background/80 backdrop-blur-md">
    <div className="flex items-center gap-3">
      <Link href="/"> <span className="text-2xl font-bold tracking-tight">OrchestrateAI</span> </Link>
      <span className="text-sm text-muted-foreground font-medium hidden sm:inline">Multi-Agent Research Agency</span>
    </div>
    <div>{/* Dark mode toggle placeholder */}</div>
  </header>
);

export default Header; 