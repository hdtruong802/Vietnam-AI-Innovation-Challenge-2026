"use client";

export interface IconProps {
  className?: string;
  stroke?: string;
}

const base = {
  viewBox: "0 0 24 24",
  fill: "none" as const,
  strokeWidth: 1.75,
  strokeLinecap: "round" as const,
  strokeLinejoin: "round" as const,
  "aria-hidden": true as const,
};

export function CheckCircleIcon({ className = "w-4 h-4", stroke = "currentColor" }: IconProps) {
  return (
    <svg {...base} className={className} stroke={stroke}>
      <circle cx="12" cy="12" r="9" />
      <path d="m8.5 12.5 2.5 2.5 4.5-5" />
    </svg>
  );
}

export function SpinnerIcon({ className = "w-4 h-4 animate-vg-spin", stroke = "currentColor" }: IconProps) {
  return (
    <svg {...base} className={className} stroke={stroke}>
      <path d="M12 3a9 9 0 1 0 9 9" />
    </svg>
  );
}

export function AlertTriangleIcon({ className = "w-4 h-4", stroke = "currentColor" }: IconProps) {
  return (
    <svg {...base} className={className} stroke={stroke}>
      <path d="M12 9v4M12 17h.01" />
      <path d="M10.3 3.86 1.82 18a1.5 1.5 0 0 0 1.3 2.25h17.76a1.5 1.5 0 0 0 1.3-2.25L13.7 3.86a1.5 1.5 0 0 0-2.6 0Z" />
    </svg>
  );
}

export function AlertCircleIcon({ className = "w-4 h-4", stroke = "currentColor" }: IconProps) {
  return (
    <svg {...base} className={className} stroke={stroke}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 8v4.5M12 16h.01" />
    </svg>
  );
}

export function InfoCircleIcon({ className = "w-4 h-4", stroke = "currentColor" }: IconProps) {
  return (
    <svg {...base} className={className} stroke={stroke}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 11v5M12 8h.01" />
    </svg>
  );
}

export function HelpCircleIcon({ className = "w-4 h-4", stroke = "currentColor" }: IconProps) {
  return (
    <svg {...base} className={className} stroke={stroke}>
      <circle cx="12" cy="12" r="9" />
      <path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.29c-.7.32-1 .82-1 1.46V14" />
      <path d="M12 17h.01" />
    </svg>
  );
}

export function ThumbsUpIcon({ className = "w-4 h-4", stroke = "currentColor" }: IconProps) {
  return (
    <svg {...base} className={className} stroke={stroke}>
      <path d="M7 11v9H4a1 1 0 0 1-1-1v-7a1 1 0 0 1 1-1Z" />
      <path d="M7 11l3.5-7a2 2 0 0 1 2 2v3h5.4a2 2 0 0 1 2 2.4l-1.2 6A2 2 0 0 1 16.8 20H7" />
    </svg>
  );
}

export function ThumbsDownIcon({ className = "w-4 h-4", stroke = "currentColor" }: IconProps) {
  return (
    <svg {...base} className={className} stroke={stroke}>
      <path d="M17 13V4h3a1 1 0 0 1 1 1v7a1 1 0 0 1-1 1Z" />
      <path d="M17 13l-3.5 7a2 2 0 0 1-2-2v-3H6.1a2 2 0 0 1-2-2.4l1.2-6A2 2 0 0 1 7.2 4H17" />
    </svg>
  );
}

export function FlaskIcon({ className = "w-4 h-4", stroke = "currentColor" }: IconProps) {
  return (
    <svg {...base} className={className} stroke={stroke}>
      <path d="M9 3h6M10 3v6l-5.2 8.5A1.5 1.5 0 0 0 6.1 20h11.8a1.5 1.5 0 0 0 1.3-2.5L14 9V3" />
      <path d="M7.5 15h9" />
    </svg>
  );
}

export function ShieldIcon({ className = "w-4 h-4", stroke = "currentColor" }: IconProps) {
  return (
    <svg {...base} className={className} stroke={stroke}>
      <path d="M12 3 5 6v5c0 4.5 3 8 7 9 4-1 7-4.5 7-9V6l-7-3Z" />
    </svg>
  );
}

export function DocIcon({ className = "w-8 h-8", stroke = "currentColor" }: IconProps) {
  return (
    <svg {...base} className={className} stroke={stroke} strokeWidth={1.5}>
      <path d="M7 3h7l4 4v14H7Z" />
      <path d="M14 3v4h4" />
      <path d="M9.5 12.5h5M9.5 15.5h5" />
    </svg>
  );
}

export function ChecklistIcon({ className = "w-8 h-8", stroke = "currentColor" }: IconProps) {
  return (
    <svg {...base} className={className} stroke={stroke} strokeWidth={1.5}>
      <rect x="4" y="3" width="16" height="18" rx="1.5" />
      <path d="m8.5 11 1.5 1.5L13 9M8.5 16h7" />
    </svg>
  );
}

export function ChevronRightIcon({ className = "w-4 h-4", stroke = "currentColor" }: IconProps) {
  return (
    <svg {...base} className={className} stroke={stroke} strokeWidth={2}>
      <path d="m9 6 6 6-6 6" />
    </svg>
  );
}

export function BirthIcon({ className = "w-5 h-5", stroke = "var(--vg-accent)" }: IconProps) {
  return (
    <svg {...base} className={className} stroke={stroke}>
      <circle cx="12" cy="8" r="3.25" />
      <path d="M6.5 20c0-3.5 2.5-6 5.5-6s5.5 2.5 5.5 6" />
    </svg>
  );
}

export function ResidenceIcon({ className = "w-5 h-5", stroke = "var(--vg-accent)" }: IconProps) {
  return (
    <svg {...base} className={className} stroke={stroke}>
      <path d="M4 11.5 12 5l8 6.5" />
      <path d="M6 10.5V19a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1v-8.5" />
      <path d="M10 20v-5h4v5" />
    </svg>
  );
}

export function BusinessIcon({ className = "w-5 h-5", stroke = "var(--vg-accent)" }: IconProps) {
  return (
    <svg {...base} className={className} stroke={stroke}>
      <rect x="3.5" y="8" width="17" height="11" rx="1.5" />
      <path d="M8.5 8V6a1.5 1.5 0 0 1 1.5-1.5h4A1.5 1.5 0 0 1 15.5 6v2" />
      <path d="M3.5 12.5h17" />
    </svg>
  );
}

export function WarningOctagonIcon({ className = "w-4 h-4", stroke = "currentColor" }: IconProps) {
  return (
    <svg {...base} className={className} stroke={stroke} strokeWidth={2}>
      <circle cx="12" cy="12" r="9" />
      <path d="M12 8v5M12 16h.01" />
    </svg>
  );
}

export function SparkleIcon({ className = "w-4 h-4", stroke = "currentColor" }: IconProps) {
  return (
    <svg {...base} className={className} stroke={stroke} strokeWidth={1.5}>
      <path d="M12 3l1.8 4.9L19 9.7l-4.4 3.2L16 18l-4-2.9L8 18l1.4-5.1L5 9.7l5.2-.8L12 3Z" />
    </svg>
  );
}
