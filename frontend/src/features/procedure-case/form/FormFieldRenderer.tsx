"use client";

import type { Finding, FormFieldValue, FormSchemaProperty } from "../procedureCase.types";
import { AlertTriangleIcon, InfoCircleIcon } from "../icons";

interface FormFieldRendererProps {
  fieldKey: string;
  property: FormSchemaProperty;
  isRequired: boolean;
  value: FormFieldValue;
  finding?: Finding;
  onChange: (key: string, value: FormFieldValue) => void;
  onFocus: (key: string) => void;
  onBlur: () => void;
}

export default function FormFieldRenderer({
  fieldKey,
  property,
  isRequired,
  value,
  finding,
  onChange,
  onFocus,
  onBlur,
}: FormFieldRendererProps) {
  const inputId = `input-${fieldKey}`;
  const errorId = `${inputId}-error`;
  const hasError = finding?.severity === "error";
  const commonProps = {
    id: inputId,
    onFocus: () => onFocus(fieldKey),
    onBlur,
    "aria-required": isRequired,
    "aria-invalid": hasError,
    "aria-describedby": finding ? errorId : undefined,
    className: `px-3 py-2 border rounded-lg text-xs transition-all focus:outline-none focus:border-[var(--vg-accent)] focus-visible:ring-2 focus-visible:ring-[var(--vg-accent)] ${
      hasError ? "border-[var(--vg-error)] bg-[var(--vg-error-soft)]" : "border-[var(--vg-border)] bg-[var(--vg-surface)] text-[var(--vg-text)]"
    }`,
  };

  let control: React.ReactNode;
  if (property.type === "boolean") {
    control = (
      <input
        {...commonProps}
        type="checkbox"
        checked={value === true}
        onChange={(e) => onChange(fieldKey, e.target.checked)}
        className="w-4 h-4"
      />
    );
  } else if (property.type === "integer" || property.type === "number") {
    control = (
      <input
        {...commonProps}
        type="number"
        value={value === null || value === undefined ? "" : String(value)}
        onChange={(e) => onChange(fieldKey, e.target.value === "" ? null : Number(e.target.value))}
      />
    );
  } else if (property.format === "date") {
    control = (
      <input
        {...commonProps}
        type="date"
        value={typeof value === "string" ? value : ""}
        onChange={(e) => onChange(fieldKey, e.target.value)}
      />
    );
  } else {
    control = (
      <input
        {...commonProps}
        type="text"
        minLength={property.minLength}
        value={typeof value === "string" ? value : ""}
        onChange={(e) => onChange(fieldKey, e.target.value)}
      />
    );
  }

  return (
    <div className="flex flex-col text-left">
      <label htmlFor={inputId} className="text-[11px] font-bold text-[var(--vg-text)] mb-1">
        {property.title} {isRequired && <span className="text-[var(--vg-error)]">*</span>}
      </label>
      {control}
      {finding && (
        <span
          id={errorId}
          className={`inline-flex items-center gap-1 text-[10px] font-bold mt-0.5 ${hasError ? "text-[var(--vg-error)]" : "text-[var(--vg-warning)]"}`}
        >
          {hasError ? <AlertTriangleIcon className="w-3 h-3 shrink-0" /> : <InfoCircleIcon className="w-3 h-3 shrink-0" />}
          {finding.message}
        </span>
      )}
    </div>
  );
}
