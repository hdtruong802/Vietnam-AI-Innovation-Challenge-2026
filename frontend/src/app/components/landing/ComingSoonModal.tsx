interface ComingSoonModalProps {
  show: boolean;
  text: string;
  onClose: () => void;
}

export default function ComingSoonModal({ show, text, onClose }: ComingSoonModalProps) {
  if (!show) return null;

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 font-sans animate-fade-in">
      <div className="bg-white border border-border-slate rounded-2xl p-6 max-w-sm w-full shadow-2xl relative overflow-hidden animate-scale-up">
        <div className="absolute top-0 left-0 w-full h-[4px] bg-gov-red" />
        <h4 className="text-base font-serif font-extrabold text-primary mb-4">Thông báo từ Cổng DVCQG</h4>
        <p className="text-sm text-foreground/75 leading-relaxed font-medium">{text}</p>
        <div className="mt-6 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gov-red text-white text-sm font-bold rounded-lg hover:bg-gov-red-hover transition-all shadow-sm"
          >
            Đã hiểu
          </button>
        </div>
      </div>
    </div>
  );
}
