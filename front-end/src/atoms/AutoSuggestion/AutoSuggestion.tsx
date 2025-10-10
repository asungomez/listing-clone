import { useEffect, useRef, useState } from "react";
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
  suggestionsGenerator: (
    search: string
  ) => SuggestionItem<T>[] | Promise<SuggestionItem<T>[]>;
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
  const [suppressOpen, setSuppressOpen] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const [suggestions, setSuggestions] = useState<SuggestionItem<T>[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      const result = suggestionsGenerator(search);
      if (result instanceof Promise) {
        setLoading(true);
        try {
          const data = await result;
          if (!cancelled) setSuggestions(data);
        } finally {
          if (!cancelled) setLoading(false);
        }
      } else {
        setSuggestions(result);
      }
    };
    if (search.length > 0) run();
    else {
      setSuggestions([]);
      setLoading(false);
    }
    return () => {
      cancelled = true;
    };
  }, [search, suggestionsGenerator]);

  useEffect(() => {
    if (suppressOpen) {
      setOpen(false);
      return;
    }
    if (search.length > 0) {
      setOpen(true); // show dropdown even if no results, to display empty state
    } else {
      setOpen(false);
    }
  }, [search, suppressOpen]);

  // Sync input text from controlled selected value when it changes (if provided)
  useEffect(() => {
    if (value && value.label !== search) {
      setSearch(value.label);
      setSuppressOpen(true);
    }
    // If value becomes null, keep whatever the user typed
  }, [value]);

  const handlePick = (item: SuggestionItem<T>) => {
    setSearch(item.label);
    setOpen(false);
    setSuppressOpen(true);
    onChange(item);
  };

  const handleInput: NonNullable<typeof onInput> = (
    e: FormEvent<HTMLInputElement>
  ) => {
    setSearch(e.currentTarget.value);
    setSuppressOpen(false);
    if (typeof onInput === "function") onInput(e);
  };

  const handleFocus: NonNullable<typeof onFocus> = (e) => {
    if (!suppressOpen) {
      setOpen(suggestions.length > 0 && search.length > 0);
    }
    if (typeof onFocus === "function") onFocus(e);
  };

  const handleClear = () => {
    setSearch("");
    setOpen(false);
    setSuppressOpen(false);
    if (value) onChange(null);
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
        onClear={handleClear}
        loading={loading}
      />
      <div className="relative">
        <Dropdown
          open={open}
          onClose={() => setOpen(false)}
          anchor={inputRef}
          className="mt-1"
        >
          <ul className="max-h-60 overflow-auto rounded-md bg-gray-700 border border-gray-600 text-white shadow-lg">
            {suggestions.length > 0 ? (
              suggestions.map((s, idx) => (
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
              ))
            ) : (
              <li className="px-3 py-2 text-gray-400 select-none">
                No results
              </li>
            )}
          </ul>
        </Dropdown>
      </div>
    </div>
  );
};
