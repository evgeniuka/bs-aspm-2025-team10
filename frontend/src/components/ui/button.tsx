import { ButtonHTMLAttributes } from "react";
import { clsx } from "clsx";

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "danger" | "ghost";
  size?: "sm" | "md";
};

export function Button({ className, size = "md", variant = "primary", ...props }: ButtonProps) {
  return (
    <button
      className={clsx(
        "inline-flex items-center justify-center gap-2 rounded-md font-semibold transition disabled:cursor-not-allowed disabled:opacity-50",
        size === "md" && "min-h-10 px-4 py-2 text-sm",
        size === "sm" && "min-h-8 px-3 py-1.5 text-xs",
        variant === "primary" && "bg-brand text-white shadow-[0_1px_2px_rgba(36,84,214,0.35),0_10px_20px_rgba(36,84,214,0.14)] hover:bg-blue-700",
        variant === "secondary" && "border border-line bg-white/90 text-ink shadow-sm hover:bg-panel",
        variant === "danger" && "bg-danger text-white shadow-sm hover:bg-red-800",
        variant === "ghost" && "text-muted hover:bg-panel hover:text-ink",
        className
      )}
      {...props}
    />
  );
}
