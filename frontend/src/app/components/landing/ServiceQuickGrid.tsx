import { AiBadge, ChatIcon, DocCheckIcon, GuideBookIcon, SearchDocIcon, StarIcon, WalletIcon } from "./icons";

interface ServiceQuickGridProps {
  onGoCopilot: () => void;
  onComingSoon: (text: string) => void;
}

export default function ServiceQuickGrid({ onGoCopilot, onComingSoon }: ServiceQuickGridProps) {
  const items = [
    { icon: DocCheckIcon, label: "Đăng ký, quản lý hồ sơ\ntrực tuyến", onClick: onGoCopilot, showAiBadge: true },
    { icon: WalletIcon, label: "Thanh toán trực tuyến\nphí, lệ phí", onClick: () => onComingSoon("Thanh toán lệ phí trực tuyến an toàn, tích hợp ngân hàng quốc gia.") },
    { icon: SearchDocIcon, label: "Tra cứu hồ sơ đã nộp", onClick: () => onComingSoon("Nhập mã hồ sơ hành chính của bạn để theo dõi tiến độ giải quyết trực tiếp.") },
    { icon: StarIcon, label: "Đánh giá chất lượng\ndịch vụ công", onClick: () => onComingSoon("Ý kiến đóng góp của bạn giúp cải tiến thủ tục hành chính tốt hơn.") },
    { icon: ChatIcon, label: "Phản ánh, kiến nghị", onClick: () => onComingSoon("Gửi trực tiếp phản ánh, kiến nghị về vướng mắc thủ tục hành chính.") },
    { icon: GuideBookIcon, label: "Hướng dẫn sử dụng", onClick: () => onComingSoon("Tài liệu hướng dẫn sử dụng, video trực quan cho công dân.") },
  ];

  return (
    <section className="-mt-[18px] relative z-20 shrink-0">
      <div className="portal-container bg-[#fffdf9] border border-border-slate rounded-2xl shadow-xl p-6 md:p-8 grid grid-cols-2 md:grid-cols-6 gap-6 md:gap-0 md:divide-x md:divide-border-slate/60 text-center">
        {items.map(({ icon: Icon, label, onClick, showAiBadge }) => (
          <button
            key={label}
            onClick={onClick}
            className="flex flex-col items-center justify-start p-3 rounded-xl hover:bg-gov-cream transition-all group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gov-red/40"
          >
            <div className="relative w-[52px] h-[52px] rounded-full bg-[#fff2dc] text-gov-red flex items-center justify-center mb-3 shadow-inner group-hover:scale-110 transition-transform">
              <Icon className="w-6 h-6" />
              {showAiBadge && <AiBadge className="absolute -top-1 -right-1" />}
            </div>
            <span className="text-sm font-bold text-foreground/80 leading-snug whitespace-pre-line">{label}</span>
          </button>
        ))}
      </div>
    </section>
  );
}
