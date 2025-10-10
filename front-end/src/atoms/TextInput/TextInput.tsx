import { forwardRef, useEffect, useRef, useState } from "react";
import type {
  InputHTMLAttributes,
  FormEvent,
  ForwardRefExoticComponent,
  RefAttributes,
} from "react";
import clsx from "clsx";

export type TextInputProps = {
  label?: string;
  onClear?: () => void;
} & InputHTMLAttributes<HTMLInputElement>;

export const TextInput: ForwardRefExoticComponent<
  TextInputProps & RefAttributes<HTMLInputElement>
> = forwardRef<HTMLInputElement, TextInputProps>(
  (
    {
      label,
      id,
      name,
      type = "text",
      className,
      onClear,
      value,
      onInput,
      ...rest
    },
    ref
  ) => {
    const inputId = id ?? name;
    const innerRef = useRef<HTMLInputElement | null>(null);
    const [hasValue, setHasValue] = useState(
      Boolean(
        (rest as { value?: unknown; defaultValue?: unknown }).value ??
          (rest as { defaultValue?: unknown }).defaultValue
      )
    );

    const setRefs = (node: HTMLInputElement | null) => {
      innerRef.current = node;
      if (typeof ref === "function") {
        ref(node);
      } else if (ref) {
        (ref as { current: HTMLInputElement | null }).current = node;
      }
    };

    const handleInput = (e: FormEvent<HTMLInputElement>) => {
      const target = e.currentTarget;
      setHasValue(target.value.length > 0);
      if (typeof onInput === "function") onInput(e);
    };

    const handleClear = () => {
      if (onClear) {
        onClear();
      } else if (innerRef.current && value === undefined) {
        innerRef.current.value = "";
        innerRef.current.dispatchEvent(new Event("input", { bubbles: true }));
      }
      setHasValue(false);
      innerRef.current?.focus();
    };

    const controlledValue = value;
    useEffect(() => {
      setHasValue(
        typeof controlledValue === "string"
          ? controlledValue.length > 0
          : Boolean(controlledValue)
      );
    }, [controlledValue]);

    return (
      <div className="mb-5">
        {label ? (
          <label
            htmlFor={inputId}
            className="block mb-2 text-sm font-medium text-white"
          >
            {label}
          </label>
        ) : null}
        <div className="relative">
          <input
            id={inputId}
            name={name}
            ref={setRefs}
            type={type}
            onInput={handleInput}
            className={clsx(
              "bg-gray-700 border border-gray-600 text-white text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 placeholder-gray-400 pr-9",
              className
            )}
            value={value}
            {...rest}
          />
          {hasValue ? (
            <button
              type="button"
              aria-label="Clear input"
              onClick={handleClear}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-gray-400 hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500 rounded"
            >
              ×
            </button>
          ) : null}
        </div>
      </div>
    );
  }
);
