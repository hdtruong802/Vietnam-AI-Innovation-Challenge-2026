"use client";

import { FormEvent, useId, useState } from "react";

interface LoginDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onDemoLogin: () => void;
}

export default function LoginDialog({ isOpen, onClose, onDemoLogin }: LoginDialogProps) {
  const titleId = useId();
  const [message, setMessage] = useState("");

  if (!isOpen) return null;

  function handleAccountSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setMessage("Đăng nhập bằng tài khoản chưa được mở trong bản demo này. Hãy chọn “Vào demo ngay”.");
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/55 p-4" role="presentation">
      <div role="dialog" aria-modal="true" aria-labelledby={titleId} className="w-full max-w-md rounded-xl border border-border-slate bg-white p-6 shadow-xl">
        <div className="flex items-start justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wide text-gov-red">Bản demo</p>
            <h2 id={titleId} className="mt-1 text-xl font-bold text-primary">Đăng nhập VNGov</h2>
          </div>
          <button type="button" onClick={onClose} className="rounded p-1 text-foreground/70 hover:bg-neutral-bg" aria-label="Đóng đăng nhập">×</button>
        </div>
        <p className="mt-3 text-sm leading-6 text-foreground/70">Bạn có thể trải nghiệm Copilot ngay mà không cần tạo hay cung cấp tài khoản.</p>
        <button type="button" onClick={onDemoLogin} className="mt-5 w-full rounded-lg bg-gov-red px-4 py-2.5 text-sm font-bold text-white transition-colors hover:bg-gov-red-hover">
          Vào demo ngay
        </button>
        <div className="my-5 flex items-center gap-3 text-xs text-foreground/50"><span className="h-px flex-1 bg-border-slate" />Hoặc đăng nhập tài khoản<span className="h-px flex-1 bg-border-slate" /></div>
        <form className="space-y-4" onSubmit={handleAccountSubmit}>
          <label className="block text-sm font-semibold text-foreground" htmlFor="auth-username">
            Tên đăng nhập
            <input id="auth-username" autoComplete="username" className="mt-1.5 w-full rounded-lg border border-border-slate px-3 py-2.5 text-sm outline-none focus:border-gov-red focus:ring-2 focus:ring-gov-red/20" />
          </label>
          <label className="block text-sm font-semibold text-foreground" htmlFor="auth-password">
            Mật khẩu
            <input id="auth-password" type="password" autoComplete="current-password" className="mt-1.5 w-full rounded-lg border border-border-slate px-3 py-2.5 text-sm outline-none focus:border-gov-red focus:ring-2 focus:ring-gov-red/20" />
          </label>
          {message && <p role="status" className="text-sm font-medium text-foreground/70">{message}</p>}
          <button type="submit" className="w-full rounded-lg border border-border-slate px-4 py-2.5 text-sm font-bold text-primary transition-colors hover:bg-neutral-bg">Đăng nhập tài khoản</button>
        </form>
      </div>
    </div>
  );
}
