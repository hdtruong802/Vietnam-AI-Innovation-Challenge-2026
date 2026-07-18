"use client";

import type { ChecklistResponse, Finding, FormFieldValue } from "../procedureCase.types";
import FormFieldRenderer from "./FormFieldRenderer";

interface DynamicFormRendererProps {
  checklist: ChecklistResponse;
  formDraft: Record<string, FormFieldValue>;
  findings: Finding[];
  onChange: (key: string, value: FormFieldValue) => void;
  onFocusField: (key: string) => void;
  onBlurField: () => void;
}

// Conditional field visibility is not implemented: ChecklistResponse.form_schema
// properties only carry {type, title, minLength?, format?} — there is no
// depends_on/visible_if key on the backend model to key visibility off of
// (only ChecklistItem.condition exists, and only for document items, with
// no defined shape). Every schema property is rendered unconditionally.
export default function DynamicFormRenderer({
  checklist,
  formDraft,
  findings,
  onChange,
  onFocusField,
  onBlurField,
}: DynamicFormRendererProps) {
  const properties = checklist.form_schema?.properties ?? {};
  const required = checklist.form_schema?.required ?? [];

  return (
    <div className="space-y-3.5 max-h-[280px] overflow-y-auto pr-1">
      {Object.entries(properties).map(([key, property]) => (
        <FormFieldRenderer
          key={key}
          fieldKey={key}
          property={property}
          isRequired={required.includes(key)}
          value={formDraft[key] ?? null}
          finding={findings.find((f) => f.field_id === key)}
          onChange={onChange}
          onFocus={onFocusField}
          onBlur={onBlurField}
        />
      ))}
    </div>
  );
}
