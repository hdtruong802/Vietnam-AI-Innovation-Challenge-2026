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
    <section className="relative min-h-[490px] md:min-h-[520px] flex items-center py-12 md:py-16 overflow-hidden shrink-0 bg-gradient-to-r from-[#263417] via-[#3e4b1d] to-[#af7610]">
      {/* Bronze drum: wrapper handles position/scale/static tilt, inner Image handles glow + the only-transform spin */}
      <div
        className="absolute z-0 pointer-events-none select-none
                   left-[86%] top-[6%] w-[300px]
                   md:left-[78%] md:top-[40%] md:w-[760px]
                   lg:left-[74%] lg:top-[42%] lg:w-[960px]
                   -translate-x-1/2 -translate-y-1/2 rotate-[-10deg]"
      >
        <Image
          src={trongDong}
          alt=""
          className="w-full h-auto object-contain pointer-events-none select-none
                     opacity-[0.5] md:opacity-[0.72] lg:opacity-[0.8]
                     brightness-[1.15] saturate-[1.3]
                     drop-shadow-[0_0_40px_rgba(216,148,47,0.45)]
                     animate-drum-spin"
          priority
        />
      </div>

      {/* Directional contrast overlay: darkens the text side, leaves the drum side clear */}
      <div className="absolute inset-0 z-10 bg-gradient-to-r from-black/30 from-0% via-black/10 via-45% to-transparent to-70% pointer-events-none" />

      <div className="absolute z-20 bottom-0 left-0 w-full h-auto pointer-events-none select-none">
        {/* Sharp lotus: masked out on the left so it no longer fights with the heading text */}
        <Image
          src={hoaSen}
          alt=""
          className="w-full h-auto object-contain object-bottom"
          style={{
            opacity: 0.70,
            maskImage:
              "linear-gradient(to right, transparent 0%, rgba(0,0,0,0.45) 28%, black 55%)",
            WebkitMaskImage:
              "linear-gradient(to right, transparent 0%, rgba(0,0,0,0.45) 28%, black 55%)",
          }}
        />
        {/* Soft, receded lotus layer over the left/text-overlapping area, fading into the sharp layer */}
        <Image
          src={hoaSen}
          alt=""
          className="absolute inset-0 w-full h-auto object-contain object-bottom"
          style={{
            filter: "blur(clamp(6px, 1.1vw, 14px)) saturate(0.9) brightness(0.95)",
            opacity: 0.12,
            transform: "scale(1.03)",
            maskImage: "linear-gradient(to right, black 0%, black 30%, transparent 58%)",
            WebkitMaskImage: "linear-gradient(to right, black 0%, black 30%, transparent 58%)",
          }}
        />
      </div>

      <div className="portal-container relative z-30">
        <div className="max-w-[620px] text-left">
          <h1 className="text-3xl md:text-5xl font-sans font-bold text-white leading-[1.18] tracking-tight drop-shadow-md">
            Kết nối, cung cấp<br />
            thông tin và dịch vụ công<br />
            mọi lúc, mọi nơi
          </h1>
          <p className="text-sm md:text-base text-white/90 mt-4 max-w-xl leading-relaxed font-medium">
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
              className="flex-1 px-4 py-3 bg-transparent text-base focus:outline-none focus-visible:ring-2 focus-visible:ring-gov-red/40 rounded-lg text-foreground placeholder:text-[var(--portal-muted)] font-medium"
            />
            <button
              type="submit"
              aria-label="Tìm kiếm"
              className="px-4 py-3 aspect-square bg-gov-red text-white rounded-lg hover:bg-gov-red-hover transition-all flex items-center justify-center gap-2 text-sm font-bold focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-white/70"
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
