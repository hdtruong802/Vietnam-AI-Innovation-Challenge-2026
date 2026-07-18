import { ArrowRightIcon } from "./icons";

interface Procedure {
  id?: string;
  title: string;
  description: string;
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
      onClick: () => onSelectProcedure("dang-ky-khai-sinh"),
    },
    {
      title: "Đăng ký thường trú",
      description: "Thủ tục đăng ký thường trú trực tuyến",
      onClick: () => onSelectProcedure("dang-ky-thuong-tru"),
    },
    {
      title: "Cấp đổi giấy phép lái xe",
      description: "Thủ tục cấp đổi giấy phép lái xe trực tuyến",
      onClick: () => onComingSoon("Thủ tục cấp đổi Giấy phép lái xe quốc gia đang được cập nhật luồng AI tiền kiểm."),
    },
    {
      title: "Đăng ký kinh doanh",
      description: "Thủ tục đăng ký thành lập doanh nghiệp",
      onClick: () => onSelectProcedure("dang-ky-ho-kinh-doanh"),
    },
    {
      title: "Nộp thuế điện tử",
      description: "Nộp thuế trực tuyến mọi lúc, mọi nơi",
      onClick: () => onComingSoon("Hệ thống nộp thuế điện tử liên kết trực tiếp với Tổng cục Thuế."),
    },
    {
      title: "Bảo hiểm xã hội",
      description: "Tra cứu và nộp hồ sơ bảo hiểm xã hội",
      onClick: () => onComingSoon("Tra cứu thông tin và quá trình đóng Bảo hiểm xã hội trực tuyến."),
    },
  ];

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
    <section className="px-6 md:px-12 py-12 shrink-0">
      <div className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Featured Services (2/3 width) */}
        <div className="lg:col-span-2 space-y-6">
          <div className="flex items-center gap-2 border-b border-border-slate pb-3">
            <h3 className="text-lg font-serif font-extrabold text-primary">Dịch vụ công nổi bật</h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-sans">
            {procedures.map((proc) => (
              <div
                key={proc.title}
                onClick={proc.onClick}
                className="flex items-center justify-between p-4 bg-white border border-border-slate rounded-xl hover:border-gov-red hover:shadow-md hover-lift cursor-pointer transition-all duration-200 group"
              >
                <div>
                  <h4 className="text-xs font-bold text-gov-red">{proc.title}</h4>
                  <p className="text-[10px] text-foreground/50 font-medium mt-0.5">{proc.description}</p>
                </div>
                <ArrowRightIcon className="w-4 h-4 text-foreground/40 group-hover:text-gov-red transition-colors shrink-0" />
              </div>
            ))}
          </div>

          <div className="pt-2 text-center">
            <button
              onClick={onGoCopilot}
              className="px-6 py-2.5 bg-gov-red text-white text-xs font-bold rounded-lg hover:bg-gov-red-hover transition-all font-sans"
            >
              Xem tất cả dịch vụ công
            </button>
          </div>
        </div>

        {/* Right Column: Latest Updates (1/3 width) */}
        <div className="space-y-6">
          <div className="flex items-center justify-between border-b border-border-slate pb-3">
            <h3 className="text-lg font-serif font-extrabold text-primary">Cập nhật mới nhất</h3>
            <button onClick={() => onComingSoon("Kho văn bản tin tức đang được đồng bộ.")} className="text-xs font-bold text-gov-red hover:underline">Xem tất cả</button>
          </div>

          <div className="space-y-4 divide-y divide-border-slate font-sans">
            {news.map((item) => (
              <div key={item.title} className="pt-3.5 first:pt-1.5 cursor-pointer hover:text-gov-red transition-colors group" onClick={item.onClick}>
                <div className="flex items-start justify-between gap-2">
                  <h4 className="text-xs font-bold text-foreground leading-snug group-hover:text-gov-red">{item.title}</h4>
                  <ArrowRightIcon className="w-4 h-4 text-foreground/40 group-hover:text-gov-red transition-colors shrink-0 mt-0.5" />
                </div>
                <span className="text-[10px] text-foreground/50 block mt-1 font-medium">{item.date}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
