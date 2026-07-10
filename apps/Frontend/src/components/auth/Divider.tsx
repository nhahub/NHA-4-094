import { cn } from "@/lib/utils";

interface DividerProps {
  text?: string;
  className?: string;
}

export function Divider({ text = "or", className }: DividerProps) {
  return (
    <div
      className={cn("relative flex items-center py-1", className)}
      role="separator"
      aria-label={text}
    >
      <div className="flex-1 border-t border-[#666565]/20" />
      <span className="mx-4 text-xs font-medium uppercase tracking-wider text-muted-foreground/50">
        {text}
      </span>
      <div className="flex-1 border-t border-[#666565]/20" />
    </div>
  );
}
