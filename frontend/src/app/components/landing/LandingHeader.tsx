import Image from "next/image";
import vngovSymbol from "@/image/VNGov_symbol.svg";
import portalLogo from "@/image/logo-cong-dich-vu-cong-quoc-gia.png";

interface LandingHeaderProps {
  onGoCopilot: () => void;
  onComingSoon: (text: string) => void;
  onLogin: () => void;
  isAuthenticated: boolean;
  onLogout: () => void;
}

export default function LandingHeader({
  onGoCopilot,
  onComingSoon,
  onLogin,
  isAuthenticated,
  onLogout,
}: LandingHeaderProps) {
  return (
    <header className="w-full bg-white border-b border-border-slate shadow-sm shrink-0 relative overflow-hidden">
      <div className="absolute top-0 left-0 w-full h-[3px] bg-gradient-to-r from-gov-gold via-gov-red to-gov-gold" />
      <div className="w-full bg-amber-50 border-b border-amber-200 text-center text-[11px] md:text-xs font-medium text-amber-800 px-4 py-1">
        Sản phẩm thử nghiệm tại VAIC 2026 – không phải cổng dịch vụ công chính thức.
      </div>
      <div className="max-w-[1440px] mx-auto flex items-center justify-between gap-6 px-6 md:px-12 py-5">
        <div className="flex items-center gap-3 relative z-10">
          <Image src={vngovSymbol} alt="Biểu tượng VNGov" className="w-11 h-11 md:w-12 md:h-12 shrink-0 object-contain" priority unoptimized />
          <Image
            src={portalLogo}
            alt="Cổng dịch vụ công Quốc gia"
            className="h-8 md:h-9 w-auto hidden sm:block"
            priority
          />
        </div>

        <nav className="hidden lg:flex items-center gap-6 text-sm font-bold text-foreground/75">
          <button className="text-gov-red hover:text-gov-red-hover border-b border-gov-red pb-1">Trang chủ</button>
          <button className="hover:text-gov-red pb-1 transition-colors" onClick={() => onComingSoon("Giới thiệu hệ thống dịch vụ công đang được cập nhật.")}>Giới thiệu</button>
          <button className="hover:text-gov-red pb-1 transition-colors" onClick={onGoCopilot}>Dịch vụ công</button>
          <button className="hover:text-gov-red pb-1 transition-colors" onClick={() => onComingSoon("Chức năng tra cứu hồ sơ điện tử đang liên kết với cơ sở dữ liệu quốc gia.")}>Tra cứu hồ sơ</button>
          <button className="hover:text-gov-red pb-1 transition-colors" onClick={() => onComingSoon("Cổng thanh toán điện tử phí & lệ phí hành chính đang được bảo trì định kỳ.")}>Thanh toán</button>
          <button className="hover:text-gov-red pb-1 transition-colors" onClick={() => onComingSoon("Tổng đài hỗ trợ 1900 1234 phục vụ 24/7.")}>Hỗ trợ</button>
        </nav>

        <div className="flex items-center gap-3">
          {isAuthenticated ? (
            <>
              <button onClick={onGoCopilot} className="px-4 py-2 bg-gov-red text-white text-sm font-bold rounded-lg hover:bg-gov-red-hover transition-all shadow-sm">Vào Copilot</button>
              <button onClick={onLogout} className="px-3 py-2 text-sm font-bold text-foreground/70 hover:text-gov-red">Đăng xuất</button>
            </>
          ) : (
            <button
              onClick={onLogin}
              className="px-4 py-2 bg-gov-red text-white text-sm font-bold rounded-lg hover:bg-gov-red-hover transition-all shadow-sm"
            >
              Đăng nhập
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
