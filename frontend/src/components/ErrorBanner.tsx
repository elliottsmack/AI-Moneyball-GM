import { AlertCircle } from "lucide-react";

export default function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="flex items-center gap-3 bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-400">
      <AlertCircle size={18} className="flex-shrink-0" />
      <p className="text-sm">{message}</p>
    </div>
  );
}
