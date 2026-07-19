interface IconProps {
  className?: string;
}

export const DocCheckIcon = ({ className = "w-6 h-6" }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M7 3h7l4 4v13a1 1 0 01-1 1H7a1 1 0 01-1-1V4a1 1 0 011-1z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
    <path d="M14 3v4h4" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
    <path d="M8.5 13.5l2 2 4-4.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export const WalletIcon = ({ className = "w-6 h-6" }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="3" y="6" width="18" height="13" rx="2" stroke="currentColor" strokeWidth="1.6" />
    <path d="M3 10h18" stroke="currentColor" strokeWidth="1.6" />
    <path d="M16 14.5h2.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
  </svg>
);

export const SearchDocIcon = ({ className = "w-6 h-6" }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M6 3h8l4 4v14a1 1 0 01-1 1H6a1 1 0 01-1-1V4a1 1 0 011-1z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
    <circle cx="11" cy="13.5" r="3" stroke="currentColor" strokeWidth="1.6" />
    <path d="M13.3 15.8L15.5 18" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
  </svg>
);

export const StarIcon = ({ className = "w-6 h-6" }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 2.5l2.9 6 6.6.8-4.8 4.6 1.2 6.6L12 17l-5.9 3.5 1.2-6.6-4.8-4.6 6.6-.8L12 2.5z" />
  </svg>
);

export const ChatIcon = ({ className = "w-6 h-6" }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M4 5h16v11H8l-4 4V5z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
    <circle cx="8.5" cy="10.5" r="1" fill="currentColor" />
    <circle cx="12" cy="10.5" r="1" fill="currentColor" />
    <circle cx="15.5" cy="10.5" r="1" fill="currentColor" />
  </svg>
);

export const GuideBookIcon = ({ className = "w-6 h-6" }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 6.5C10.3 5.2 8 4.5 5 4.5V17c3 0 5.3.7 7 2 1.7-1.3 4-2 7-2V4.5c-3 0-5.3.7-7 2z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
    <path d="M12 6.5V19" stroke="currentColor" strokeWidth="1.6" />
  </svg>
);

export const ArrowRightIcon = ({ className = "w-4 h-4" }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M9 5l7 7-7 7" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export const ClockIcon = ({ className = "w-7 h-7" }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="12" cy="12" r="8.5" stroke="currentColor" strokeWidth="1.6" />
    <path d="M12 7.5V12l3 2" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export const PinIcon = ({ className = "w-7 h-7" }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 21s7-6.2 7-11.5a7 7 0 10-14 0C5 14.8 12 21 12 21z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
    <circle cx="12" cy="9.5" r="2.4" stroke="currentColor" strokeWidth="1.6" />
  </svg>
);

export const ShieldIcon = ({ className = "w-7 h-7" }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 3l7 3v5.5c0 5-3 8.2-7 9.5-4-1.3-7-4.5-7-9.5V6l7-3z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
    <path d="M9 12l2 2 4-4.3" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export const LeafIcon = ({ className = "w-7 h-7" }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M5 19c0-8 4-13.5 14-13.5C19 15 13.5 19 5 19z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
    <path d="M6 18C9 13 12 10 17 6.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
  </svg>
);

export const PhoneIcon = ({ className = "w-4 h-4" }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M6.5 3.5h3l1.5 4-2 1.3a11 11 0 005.7 5.7l1.3-2 4 1.5v3a1.5 1.5 0 01-1.6 1.5A15.5 15.5 0 015 6.1a1.5 1.5 0 011.5-1.6z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
  </svg>
);

export const MailIcon = ({ className = "w-4 h-4" }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="3.5" y="5.5" width="17" height="13" rx="1.5" stroke="currentColor" strokeWidth="1.6" />
    <path d="M4.5 7l7.5 6 7.5-6" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export const GlobeIcon = ({ className = "w-4 h-4" }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="12" cy="12" r="8.5" stroke="currentColor" strokeWidth="1.6" />
    <path d="M3.5 12h17M12 3.5c2.3 2.3 3.5 5.3 3.5 8.5s-1.2 6.2-3.5 8.5c-2.3-2.3-3.5-5.3-3.5-8.5S9.7 5.8 12 3.5z" stroke="currentColor" strokeWidth="1.6" />
  </svg>
);

export const BirthCertIcon = ({ className = "w-5 h-5" }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="9" cy="7" r="2.5" stroke="currentColor" strokeWidth="1.6" />
    <path d="M4.5 16c0-2.5 2-4 4.5-4s4.5 1.5 4.5 4" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
    <path d="M14 4.5h5.5v15H14" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
  </svg>
);

export const HomeIcon = ({ className = "w-5 h-5" }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M4 11.5L12 4l8 7.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    <path d="M6 10v9.5h12V10" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
    <path d="M10 19.5V14h4v5.5" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
  </svg>
);

export const LicenseIcon = ({ className = "w-5 h-5" }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="3" y="6" width="18" height="12" rx="2" stroke="currentColor" strokeWidth="1.6" />
    <circle cx="8.5" cy="12" r="2" stroke="currentColor" strokeWidth="1.6" />
    <path d="M13.5 10h5M13.5 14h3.5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
  </svg>
);

export const BriefcaseIcon = ({ className = "w-5 h-5" }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="3" y="8" width="18" height="11" rx="2" stroke="currentColor" strokeWidth="1.6" />
    <path d="M8.5 8V6a1.5 1.5 0 011.5-1.5h4A1.5 1.5 0 0115.5 6v2" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
    <path d="M3 13h18" stroke="currentColor" strokeWidth="1.6" />
  </svg>
);

export const TaxIcon = ({ className = "w-5 h-5" }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="12" cy="12" r="8.5" stroke="currentColor" strokeWidth="1.6" />
    <path d="M9 15l6-6M9.5 10.5h.01M14.5 15.5h.01" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
  </svg>
);

export const HeartShieldIcon = ({ className = "w-5 h-5" }: IconProps) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path d="M12 3l7 3v5.5c0 5-3 8.2-7 9.5-4-1.3-7-4.5-7-9.5V6l7-3z" stroke="currentColor" strokeWidth="1.6" strokeLinejoin="round" />
    <path d="M12 15.5s-2.8-1.7-2.8-3.7a1.6 1.6 0 012.8-1 1.6 1.6 0 012.8 1c0 2-2.8 3.7-2.8 3.7z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
  </svg>
);

export const AiBadge = ({ className = "" }: IconProps) => (
  <span
    className={`inline-flex items-center justify-center px-1 h-4 min-w-[18px] rounded-full bg-gov-gold text-[#3d2a00] text-[9px] font-extrabold leading-none tracking-tight ring-2 ring-white shadow-sm pointer-events-none select-none ${className}`}
  >
    AI
  </span>
);
