// /tools page: Lists all available tools
import Link from "next/link";
import { toolLinks } from "@/config/tools";

export default function ToolsPage() {
  return (
    <main className="max-w-2xl mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold mb-8">Encypher Tools</h1>
      <ul className="space-y-6">
        {toolLinks.map((tool) => (
          <li key={tool.href} className="border rounded-lg p-5 bg-card shadow-sm hover:shadow-md transition">
            <Link href={tool.href} className="text-xl font-semibold hover:underline text-primary">
              {tool.name}
            </Link>
            {tool.description ? (
              <p className="mt-1 text-muted-foreground">{tool.description}</p>
            ) : null}
          </li>
        ))}
      </ul>
    </main>
  );
}
