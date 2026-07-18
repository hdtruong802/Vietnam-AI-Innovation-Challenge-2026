import Image from "next/image";
import footerBg from "@/image/9c4df88a-96fa-45ff-9d88-467468014bdf.jpg";
import quocHuy from "@/image/quoc-huy-viet-nam.png";

interface LandingFooterProps {
  onComingSoon: (text: string) => void;
}

export default function LandingFooter({ onComingSoon }: LandingFooterProps) {
  return (
    <footer className="relative text-white/90 py-12 px-6 md:px-12 shrink-0 border-t border-white/10 overflow-hidden font-sans">
      <Image src={footerBg} alt="" fill className="object-cover object-center -z-20" />
      <div className="absolute inset-0 bg-gov-red/85 -z-10" />

      <div className="max-w-6xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 relative z-10 text-xs">
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            <Image src={quocHuy} alt="Quốc huy Việt Nam" className="w-10 h-10 shrink-0" />
            <div>
              <h4 className="font-serif font-extrabold text-sm text-white">CỔNG DỊCH VỤ CÔNG QUỐC GIA</h4>
              <p className="text-[9px] uppercase font-bold text-gov-gold tracking-wider">Kết nối, cung cấp thông tin và dịch vụ công mọi lúc, mọi nơi</p>
            </div>
          </div>
          <div className="space-y-2 text-white/70 font-medium">
            <p>024 1234 5678</p>
            <p>hotro@dvcqg.gov.vn</p>
            <p>https://dvcqg.gov.vn</p>
          </div>
        </div>

        <div className="space-y-3 font-medium">
          <h4 className="text-xs uppercase font-extrabold text-gov-gold">Về chúng tôi</h4>
          <ul className="space-y-2 text-white/70">
            <li><button className="hover:text-white transition-colors" onClick={() => onComingSoon("Giới thiệu về Ban Quản trị Cổng Dịch vụ công Quốc gia.")}>Giới thiệu</button></li>
            <li><button className="hover:text-white transition-colors" onClick={() => onComingSoon("Danh mục văn bản pháp luật quy định hành chính.")}>Văn bản pháp luật</button></li>
            <li><button className="hover:text-white transition-colors" onClick={() => onComingSoon("Câu hỏi thường gặp của người dân.")}>Câu hỏi thường gặp</button></li>
            <li><button className="hover:text-white transition-colors" onClick={() => onComingSoon("Bản đồ trang thông tin.")}>Sitemap</button></li>
          </ul>
        </div>

        <div className="space-y-3 font-medium">
          <h4 className="text-xs uppercase font-extrabold text-gov-gold">Hỗ trợ</h4>
          <ul className="space-y-2 text-white/70">
            <li><button className="hover:text-white transition-colors" onClick={() => onComingSoon("Tài liệu hướng dẫn kê khai trực tuyến.")}>Hướng dẫn sử dụng</button></li>
            <li><button className="hover:text-white transition-colors" onClick={() => onComingSoon("Tổng đài đường dây nóng 1900 1234.")}>Tổng đài hỗ trợ</button></li>
            <li><button className="hover:text-white transition-colors" onClick={() => onComingSoon("Gửi phản hồi, kiến nghị hành chính.")}>Phản ánh, kiến nghị</button></li>
          </ul>
        </div>

        <div className="space-y-3">
          <h4 className="text-xs uppercase font-extrabold text-gov-gold">Kết nối với chúng tôi</h4>
          <div className="flex items-center gap-3">
            <button aria-label="Facebook" className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 transition-all text-sm">f</button>
            <button aria-label="Zalo" className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 transition-all text-sm">Z</button>
            <button aria-label="YouTube" className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 transition-all text-sm">▶</button>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto mt-8 pt-6 border-t border-white/10 text-center text-[10px] text-white/50 relative z-10 flex flex-col sm:flex-row justify-between items-center gap-3">
        <p>© 2024 Cổng Dịch vụ công Quốc gia. All rights reserved.</p>
        <div className="flex gap-4">
          <button className="hover:text-white transition-colors" onClick={() => onComingSoon("Chính sách bảo mật thông tin quốc gia.")}>Chính sách bảo mật</button>
          <button className="hover:text-white transition-colors" onClick={() => onComingSoon("Điều khoản sử dụng dịch vụ công trực tuyến.")}>Điều khoản sử dụng</button>
        </div>
      </div>
    </footer>
  );
}
