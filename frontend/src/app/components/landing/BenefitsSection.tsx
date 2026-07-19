import Image from "next/image";
import { ClockIcon, LeafIcon, PinIcon, ShieldIcon } from "./icons";
import hoaSenLeft from "@/image/hoa_sen_left.png";
import hoaSenRight from "@/image/hoa_sen_right.png";

const BENEFITS = [
  { icon: ClockIcon, label: "Tiết kiệm thời gian giải quyết hồ sơ" },
  { icon: PinIcon, label: "Mọi lúc, mọi nơi trên mọi thiết bị" },
  { icon: ShieldIcon, label: "An toàn, bảo mật thông tin" },
  { icon: LeafIcon, label: "Giảm chi phí đi lại, giấy tờ" },
];

export default function BenefitsSection() {
  return (
    <section className="bg-gov-cream border-y border-border-slate py-14 md:py-16 relative overflow-hidden shrink-0">
      <Image
        src={hoaSenLeft}
        alt=""
        className="hidden sm:block absolute z-0 bottom-0 left-0 w-32 md:w-48 h-auto object-contain pointer-events-none select-none"
      />
      <Image
        src={hoaSenRight}
        alt=""
        className="hidden sm:block absolute z-0 bottom-0 right-0 w-32 md:w-48 h-auto object-contain pointer-events-none select-none"
      />

      <div className="portal-container text-center relative z-10">
        <h3 className="text-2xl-plus font-sans font-semibold text-primary text-balance">Lợi ích khi sử dụng dịch vụ công trực tuyến</h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-8 max-w-4xl mx-auto font-sans">
          {BENEFITS.map(({ icon: Icon, label }) => (
            <div key={label} className="flex flex-col items-center p-4">
              <div className="w-14 h-14 rounded-full bg-white border border-border-slate text-gov-red flex items-center justify-center shadow-sm mb-4">
                <Icon className="w-7 h-7" />
              </div>
              <h4 className="text-sm font-bold text-foreground/80">{label}</h4>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
