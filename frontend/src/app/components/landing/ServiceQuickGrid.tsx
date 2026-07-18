import { ChatIcon, DocCheckIcon, GuideBookIcon, SearchDocIcon, StarIcon, WalletIcon } from "./icons";

interface ServiceQuickGridProps {
  onGoCopilot: () => void;
  onComingSoon: (text: string) => void;
}

export default function ServiceQuickGrid({ onGoCopilot, onComingSoon }: ServiceQuickGridProps) {
  const items = [
    { icon: DocCheckIcon, label: "Đăng ký, quản lý hồ sơ trực tuyến", onClick: onGoCopilot },
    { icon: WalletIcon, label: "Thanh toán trực tuyến phí, lệ phí", onClick: () => onComingSoon("Thanh toán lệ phí trực tuyến an toàn, tích hợp ngân hàng quốc gia.") },
    { icon: SearchDocIcon, label: "Tra cứu hồ sơ đã nộp", onClick: () => onComingSoon("Nhập mã hồ sơ hành chính của bạn để theo dõi tiến độ giải quyết trực tiếp.") },
    { icon: StarIcon, label: "Đánh giá chất lượng dịch vụ công", onClick: () => onComingSoon("Ý kiến đóng góp của bạn giúp cải tiến thủ tục hành chính tốt hơn.") },
    { icon: ChatIcon, label: "Phản ánh, kiến nghị", onClick: () => onComingSoon("Gửi trực tiếp phản ánh, kiến nghị về vướng mắc thủ tục hành chính.") },
    { icon: GuideBookIcon, label: "Hướng dẫn sử dụng", onClick: () => onComingSoon("Tài liệu hướng dẫn sử dụng, video trực quan cho công dân.") },
  ];

  return (
    <section className="px-6 md:px-12 -mt-8 relative z-20 shrink-0">
      <div className="max-w-6xl mx-auto bg-white border border-border-slate rounded-2xl shadow-md p-6 md:p-8 grid grid-cols-2 md:grid-cols-6 gap-6 text-center">
        {items.map(({ icon: Icon, label, onClick }) => (
          <button
            key={label}
            onClick={onClick}
            className="flex flex-col items-center justify-center p-3 rounded-xl hover:bg-gov-cream hover-lift transition-all group"
          >
            <div className="w-12 h-12 rounded-full bg-gov-cream text-gov-red flex items-center justify-center mb-3 shadow-inner group-hover:scale-110 transition-transform">
              <Icon className="w-6 h-6" />
            </div>
            <span className="text-[11px] font-bold text-foreground/80 leading-snug">{label}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
