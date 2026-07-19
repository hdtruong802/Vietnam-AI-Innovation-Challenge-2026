import type { ComponentType } from "react";
import {
  ArrowRightIcon,
  BirthCertIcon,
  HomeIcon,
  LicenseIcon,
  BriefcaseIcon,
  TaxIcon,
  HeartShieldIcon,
  DocCheckIcon,
  GuideBookIcon,
} from "./icons";

interface Procedure {
  id?: string;
  title: string;
  description: string;
  icon: ComponentType<{ className?: string }>;
  onClick: () => void;
}

interface NewsItem {
  title: string;
  date: string;
  onClick: () => void;
}

interface FeaturedServicesAndNewsProps {
  onSelectProcedure: (procedureId: string) => void;
  onGoCopilot: () => void;
  onComingSoon: (text: string) => void;
}

export default function FeaturedServicesAndNews({ onSelectProcedure, onGoCopilot, onComingSoon }: FeaturedServicesAndNewsProps) {
  const procedures: Procedure[] = [
    {
      title: "Đăng ký khai sinh",
      description: "Thủ tục đăng ký khai sinh trực tuyến cho công dân",
      icon: BirthCertIcon,
      onClick: () => onSelectProcedure("dang-ky-khai-sinh"),
    },
    {
      title: "Đăng ký thường trú",
      description: "Thủ tục đăng ký thường trú trực tuyến",
      icon: HomeIcon,
      onClick: () => onSelectProcedure("dang-ky-thuong-tru"),
    },
    {
      title: "Cấp đổi giấy phép lái xe",
      description: "Thủ tục cấp đổi giấy phép lái xe trực tuyến",
      icon: LicenseIcon,
      onClick: () => onComingSoon("Thủ tục cấp đổi Giấy phép lái xe quốc gia đang được cập nhật luồng AI tiền kiểm."),
    },
    {
      title: "Đăng ký kinh doanh",
      description: "Thủ tục đăng ký thành lập doanh nghiệp",
      icon: BriefcaseIcon,
      onClick: () => onSelectProcedure("dang-ky-ho-kinh-doanh"),
    },
    {
      title: "Nộp thuế điện tử",
      description: "Nộp thuế trực tuyến mọi lúc, mọi nơi",
      icon: TaxIcon,
      onClick: () => onComingSoon("Hệ thống nộp thuế điện tử liên kết trực tiếp với Tổng cục Thuế."),
    },
    {
      title: "Bảo hiểm xã hội",
      description: "Tra cứu và nộp hồ sơ bảo hiểm xã hội",
      icon: HeartShieldIcon,
      onClick: () => onComingSoon("Tra cứu thông tin và quá trình đóng Bảo hiểm xã hội trực tuyến."),
    },
  ];

  const handleRowKeyDown = (e: React.KeyboardEvent, onClick: () => void) => {
    if (e.key === "Enter" || e.key === " ") {
      e.preventDefault();
      onClick();
    }
  };

  const news: NewsItem[] = [
    {
      title: "Nghị định mới về quản lý, cung cấp dịch vụ công trực tuyến",
      date: "15/05/2024",
      onClick: () => onComingSoon("Chi tiết Nghị định số 42/2024/NĐ-CP hướng dẫn thi hành Dịch vụ công trực tuyến."),
    },
    {
      title: "Hướng dẫn nộp hồ sơ trực tuyến trên Cổng dịch vụ công Quốc gia",
      date: "10/05/2024",
      onClick: () => onComingSoon("Tài liệu số hướng dẫn công dân nộp hồ sơ, quét căn cước và xác thực."),
    },
    {
      title: "Cập nhật tính năng thanh toán trực tuyến trên Cổng DVCQG",
      date: "08/05/2024",
      onClick: () => onComingSoon("Nâng cấp hạ tầng thanh toán, liên kết mã QR động với các ngân hàng lớn."),
    },
    {
      title: "Tích hợp định danh điện tử với Cổng Dịch vụ công Quốc gia",
      date: "05/05/2024",
      onClick: () => onComingSoon("Đăng nhập an toàn và bảo mật cao thông qua ứng dụng định danh VNeID."),
    },
  ];

  return (
    <section className="py-12 shrink-0">
      <div className="portal-container grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Featured Services (~64% width) */}
        <div className="lg:col-span-2 bg-[var(--portal-surface)] border border-[var(--portal-border)] rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-5">
            <span className="w-9 h-9 rounded-full bg-[#fff2dc] text-gov-red flex items-center justify-center shrink-0">
              <DocCheckIcon className="w-[18px] h-[18px]" />
            </span>
            <h3 className="text-[26px] font-sans font-semibold text-primary">Dịch vụ công nổi bật</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 md:gap-x-6 divide-y divide-border-slate md:divide-y-0 font-sans">
            {procedures.map((proc) => {
              const Icon = proc.icon;
              return (
                <div
                  key={proc.title}
                  onClick={proc.onClick}
                  role="button"
                  tabIndex={0}
                  onKeyDown={(e) => handleRowKeyDown(e, proc.onClick)}
                  className="flex items-center gap-3 py-3.5 px-2 -mx-2 rounded-lg cursor-pointer transition-colors duration-150 group hover:bg-[#fff8ee] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gov-red/40"
                >
                  <span className="w-9 h-9 rounded-full bg-[#fff2dc] text-gov-red flex items-center justify-center shrink-0">
                    <Icon className="w-[18px] h-[18px]" />
                  </span>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-[15px] font-semibold text-gov-red">{proc.title}</h4>
                    <p className="text-base text-[var(--portal-muted)] font-medium mt-0.5">{proc.description}</p>
                  </div>
                  <ArrowRightIcon className="w-4 h-4 text-[var(--portal-muted)] group-hover:text-gov-red transition-colors shrink-0" />
                </div>
              );
            })}
          </div>

          <div className="pt-4 mt-2 border-t border-border-slate text-center">
            <button
              onClick={onGoCopilot}
              className="px-6 py-2.5 bg-gov-red text-white text-sm font-bold rounded-lg hover:bg-gov-red-hover transition-all font-sans focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gov-red/50 focus-visible:ring-offset-2"
            >
              Xem tất cả dịch vụ công
            </button>
          </div>
        </div>

        {/* Right Column: Latest Updates (~36% width) */}
        <div className="bg-[var(--portal-surface)] border border-[var(--portal-border)] rounded-2xl p-6">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center gap-2">
              <span className="w-9 h-9 rounded-full bg-[#fff2dc] text-gov-red flex items-center justify-center shrink-0">
                <GuideBookIcon className="w-[18px] h-[18px]" />
              </span>
              <h3 className="text-[26px] font-sans font-semibold text-primary">Cập nhật mới nhất</h3>
            </div>
            <button onClick={() => onComingSoon("Kho văn bản tin tức đang được đồng bộ.")} className="text-sm font-bold text-gov-red hover:underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gov-red/40 rounded-sm">Xem tất cả</button>
          </div>

          <div className="divide-y divide-border-slate font-sans">
            {news.map((item) => (
              <div
                key={item.title}
                className="py-3.5 first:pt-0 cursor-pointer hover:text-gov-red transition-colors group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gov-red/40 rounded-lg"
                onClick={item.onClick}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => handleRowKeyDown(e, item.onClick)}
              >
                <div className="flex items-start justify-between gap-2">
                  <h4 className="text-base font-semibold text-foreground leading-snug group-hover:text-gov-red">{item.title}</h4>
                  <ArrowRightIcon className="w-4 h-4 text-[var(--portal-muted)] group-hover:text-gov-red transition-colors shrink-0 mt-0.5" />
                </div>
                <span className="text-sm text-[var(--portal-muted)] block mt-1 font-medium">{item.date}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
