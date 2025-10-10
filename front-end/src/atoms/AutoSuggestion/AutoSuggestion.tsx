import { useEffect, useMemo, useRef, useState } from "react";
import type { FormEvent, InputHTMLAttributes } from "react";
import clsx from "clsx";
import { TextInput } from "../TextInput/TextInput";
import { Dropdown } from "../Dropdown/Dropdown";

export type SuggestionItem<T = unknown> = { label: string; value: T };

export type AutoSuggestionProps<T = unknown> = Omit<
  InputHTMLAttributes<HTMLInputElement>,
  "onChange" | "value"
> & {
  label?: string;
  className?: string;
  suggestionsGenerator: (search: string) => SuggestionItem<T>[];
  value?: SuggestionItem<T> | null; // controlled selected item
  onChange: (item: SuggestionItem<T> | null) => void; // fired when a suggestion is picked
};

export const AutoSuggestion = <T,>({
  label,
  className,
  suggestionsGenerator,
  value,
  onChange,
  onFocus,
  onInput,
  ...inputProps
}: AutoSuggestionProps<T>) => {
  const [search, setSearch] = useState("");
  const [open, setOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const suggestions = useMemo(
    () => suggestionsGenerator(search),
    [search, suggestionsGenerator]
  );

  useEffect(() => {
    // Open when there's any text; close only if suggestions list is empty
    if (search.length > 0) {
      setOpen(suggestions.length > 0);
    } else {
      setOpen(false);
    }
  }, [suggestions, search]);

  // Sync input text from controlled selected value when it changes (if provided)
  useEffect(() => {
    if (value && value.label !== search) {
      setSearch(value.label);
    }
    // If value becomes null, keep whatever the user typed
  }, [value]);

  const handlePick = (item: SuggestionItem<T>) => {
    setSearch(item.label);
    setOpen(false);
    onChange(item);
  };

  const handleInput: NonNullable<typeof onInput> = (
    e: FormEvent<HTMLInputElement>
  ) => {
    setSearch(e.currentTarget.value);
    if (typeof onInput === "function") onInput(e);
  };

  const handleFocus: NonNullable<typeof onFocus> = (e) => {
    setOpen(suggestions.length > 0 && search.length > 0);
    if (typeof onFocus === "function") onFocus(e);
  };

  return (
    <div className={clsx("mb-5", className)} ref={containerRef}>
      <TextInput
        label={label}
        ref={inputRef}
        {...inputProps}
        value={search}
        onInput={handleInput}
        onFocus={handleFocus}
      />
      <div className="relative">
        <Dropdown
          open={open}
          onClose={() => setOpen(false)}
          anchor={inputRef}
          className="mt-1"
        >
          <ul className="max-h-60 overflow-auto rounded-md bg-gray-700 border border-gray-600 text-white shadow-lg">
            {suggestions.map((s, idx) => (
              <li
                key={`${s.label}-${idx}`}
                className="px-3 py-2 cursor-pointer hover:bg-gray-600"
                onMouseDown={(e) => {
                  e.preventDefault();
                  handlePick(s);
                }}
              >
                {s.label}
              </li>
            ))}
          </ul>
        </Dropdown>
      </div>
    </div>
  );
};
