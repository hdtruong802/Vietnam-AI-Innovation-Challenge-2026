import { ClockIcon, LeafIcon, PinIcon, ShieldIcon } from "./icons";

const BENEFITS = [
  { icon: ClockIcon, label: "Tiết kiệm thời gian giải quyết hồ sơ" },
  { icon: PinIcon, label: "Mọi lúc, mọi nơi trên mọi thiết bị" },
  { icon: ShieldIcon, label: "An toàn, bảo mật thông tin" },
  { icon: LeafIcon, label: "Giảm chi phí đi lại, giấy tờ" },
];

export default function BenefitsSection() {
  return (
    <section className="bg-gov-cream border-y border-border-slate py-12 px-6 md:px-12 relative overflow-hidden shrink-0">
      <div className="max-w-6xl mx-auto text-center relative z-10">
        <h3 className="text-xl font-serif font-extrabold text-primary">Lợi ích khi sử dụng dịch vụ công trực tuyến</h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mt-8 font-sans">
          {BENEFITS.map(({ icon: Icon, label }) => (
            <div key={label} className="flex flex-col items-center p-4">
              <div className="w-14 h-14 rounded-full bg-white border border-border-slate text-gov-red flex items-center justify-center shadow-sm mb-4">
                <Icon className="w-7 h-7" />
              </div>
              <h4 className="text-xs font-bold text-foreground/80">{label}</h4>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
