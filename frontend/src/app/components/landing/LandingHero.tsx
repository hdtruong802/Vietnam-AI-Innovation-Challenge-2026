import Image from "next/image";
import trongDong from "@/image/trong_dong.png";
import hoaSen from "@/image/hoa_sen.png";

interface LandingHeroProps {
  searchQuery: string;
  onSearchQueryChange: (value: string) => void;
  onSearchSubmit: (e: React.FormEvent) => void;
}

export default function LandingHero({ searchQuery, onSearchQueryChange, onSearchSubmit }: LandingHeroProps) {
  return (
    <section className="relative min-h-[430px] md:min-h-[460px] flex items-center py-12 md:py-16 overflow-hidden shrink-0 bg-gradient-to-r from-[#263417] via-[#3e4b1d] to-[#af7610]">
      <Image
        src={trongDong}
        alt=""
        className="absolute z-0 right-[-6%] md:right-[2%] top-1/2 -translate-y-1/2 w-[440px] md:w-[620px] h-auto object-contain opacity-90 pointer-events-none select-none"
        priority
      />

      {/* Directional contrast overlay: darkens the text side, leaves the drum side clear */}
      <div className="absolute inset-0 z-10 bg-gradient-to-r from-black/25 via-black/5 to-transparent pointer-events-none" />

      <Image
        src={hoaSen}
        alt=""
        className="absolute z-20 bottom-0 left-0 w-full h-[110px] md:h-[150px] object-cover object-bottom pointer-events-none select-none"
      />

      <div className="portal-container relative z-30">
        <div className="max-w-[620px] text-left">
          <h1 className="text-3xl md:text-5xl font-sans font-bold text-white leading-[1.18] tracking-tight drop-shadow-md">
            Kết nối, cung cấp thông tin và dịch vụ công mọi lúc, mọi nơi
          </h1>
          <p className="text-xs md:text-sm text-white/90 mt-4 max-w-xl leading-relaxed font-medium">
            Cổng Dịch vụ công Quốc gia là cầu nối giữa cơ quan nhà nước và người dân, doanh nghiệp trên môi trường số.
          </p>

          {/* Search Bar */}
          <form onSubmit={onSearchSubmit} className="mt-8 max-w-xl flex gap-2 p-1.5 bg-white rounded-xl shadow-lg border border-border-slate/50">
            <input
              id="landing-search-input"
              aria-label="Tìm kiếm dịch vụ công"
              type="text"
              value={searchQuery}
              onChange={(e) => onSearchQueryChange(e.target.value)}
              placeholder="Bạn cần tìm dịch vụ công nào?"
              className="flex-1 px-4 py-3 bg-transparent text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-gov-red/40 rounded-lg text-foreground placeholder-foreground/50 font-medium"
            />
            <button
              type="submit"
              aria-label="Tìm kiếm"
              className="px-4 py-3 aspect-square bg-gov-red text-white rounded-lg hover:bg-gov-red-hover transition-all flex items-center justify-center gap-2 text-xs font-bold focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70"
            >
              <svg viewBox="0 0 20 20" fill="none" className="w-4 h-4" xmlns="http://www.w3.org/2000/svg">
                <circle cx="9" cy="9" r="6.5" stroke="currentColor" strokeWidth="1.8" />
                <path d="M14 14L18 18" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
              </svg>
            </button>
          </form>
        </div>
      </div>
    </section>
  );
}
