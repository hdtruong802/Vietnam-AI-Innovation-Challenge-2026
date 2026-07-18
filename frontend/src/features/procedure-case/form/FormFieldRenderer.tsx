"use client";

import type { Finding, FormFieldValue, FormSchemaProperty } from "../procedureCase.types";

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
    className: `px-3 py-2 border rounded-lg text-xs transition-all focus:outline-none focus:border-accent focus-visible:ring-2 focus-visible:ring-accent ${
      hasError ? "border-error bg-error-bg/10" : "border-border-slate bg-card-bg text-foreground"
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
      <label htmlFor={inputId} className="text-[11px] font-bold text-primary mb-1">
        {property.title} {isRequired && <span className="text-error">*</span>}
      </label>
      {control}
      {finding && (
        <span
          id={errorId}
          className={`text-[10px] font-bold mt-0.5 ${hasError ? "text-error" : "text-warning"}`}
        >
          {hasError ? "⚠️" : "ℹ️"} {finding.message}
        </span>
      )}
    </div>
  );
}
