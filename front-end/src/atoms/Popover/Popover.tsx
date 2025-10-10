import {
  FC,
  ReactNode,
  RefObject,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
  forwardRef,
  useCallback,
  Children,
  isValidElement,
} from "react";
import type { ForwardRefExoticComponent, RefAttributes } from "react";
import { clsx } from "clsx";
import { createPortal } from "react-dom";

type PopoverSide = "top" | "right" | "bottom" | "left";

type PopoverProps = {
  anchor: RefObject<HTMLElement | null> | HTMLElement | null;
  open: boolean;
  position?: PopoverSide;
  className?: string;
  children: ReactNode;
  showArrow?: boolean;
};

type PopoverComponent = ForwardRefExoticComponent<
  PopoverProps & RefAttributes<HTMLDivElement>
> & {
  Title: FC<{ children: ReactNode }>;
};

const ARROW_SIZE_PX = 10; // visual size of the diamond (width/height)
const OFFSET_PX = 8; // gap between anchor and popover panel
const SCREEN_MARGIN_PX = 8; // min distance to viewport edges

const clamp = (value: number, min: number, max: number) =>
  Math.min(Math.max(value, min), max);

const getAnchorElement = (
  anchor: RefObject<HTMLElement | null> | HTMLElement | null
): HTMLElement | null => {
  if (!anchor) return null;
  if ("current" in (anchor as RefObject<HTMLElement | null>)) {
    return (anchor as RefObject<HTMLElement | null>).current;
  }
  return anchor as HTMLElement;
};

const chooseSide = (
  preferred: PopoverSide | undefined,
  anchorRect: DOMRect,
  panelW: number,
  panelH: number,
  vw: number,
  vh: number
): PopoverSide => {
  if (preferred) return preferred;

  const spaces: Record<PopoverSide, number> = {
    top: anchorRect.top,
    bottom: vh - anchorRect.bottom,
    left: anchorRect.left,
    right: vw - anchorRect.right,
  };

  // Heuristic: pick the side with most available space; ensure it can roughly fit
  const entries = (Object.entries(spaces) as [PopoverSide, number][]).sort(
    (a, b) => b[1] - a[1]
  );
  for (const [side] of entries) {
    if (side === "top" || side === "bottom") {
      if (panelH + OFFSET_PX + ARROW_SIZE_PX <= spaces[side]) return side;
    } else {
      if (panelW + OFFSET_PX + ARROW_SIZE_PX <= spaces[side]) return side;
    }
  }
  // fallback to the largest space anyway
  return entries[0][0];
};

const PopoverTitle: FC<{ children: ReactNode }> = ({ children }) => {
  return (
    <div
      data-popover-title
      className="px-3 py-2 bg-gray-700 border-b border-gray-600 rounded-t-lg"
    >
      <h3 className="font-semibold text-white">{children}</h3>
    </div>
  );
};
PopoverTitle.displayName = "PopoverTitle";

const ARROW_POSITIONING_CLASSES: Record<PopoverSide, string> = {
  top: "bottom-[-5px]",
  bottom: "top-[-5px]",
  left: "right-[-5px]",
  right: "left-[-5px]",
};

const ARROW_BORDER_POSITIONING_CLASSES: Record<PopoverSide, string> = {
  top: "border-b border-r",
  bottom: "border-t border-l",
  left: "border-r border-t",
  right: "border-l border-b",
};

const PopoverImpl = forwardRef<HTMLDivElement, PopoverProps>(
  ({ anchor, open, position, className, children, showArrow = true }, ref) => {
    const internalPanelRef = useRef<HTMLDivElement | null>(null);
    const [coords, setCoords] = useState<{
      top: number;
      left: number;
      side: PopoverSide;
      arrowOffset?: { left?: number; top?: number };
    } | null>(null);

    // No parsing of children: simply render them. Use <Popover.Title> for a header.

    const recalc = useCallback(() => {
      if (!open) return;
      const anchorEl = getAnchorElement(anchor);
      const panelEl = internalPanelRef.current;
      if (!anchorEl || !panelEl) return;

      const rect = anchorEl.getBoundingClientRect();
      // Temporarily make sure we can measure real size
      const vw = window.innerWidth;
      const vh = window.innerHeight;

      const panelW = panelEl.offsetWidth;
      const panelH = panelEl.offsetHeight;

      const effectiveArrow = showArrow ? ARROW_SIZE_PX : 0;
      const side = chooseSide(position, rect, panelW, panelH, vw, vh);

      let top = 0;
      let left = 0;
      let arrowOffset: { left?: number; top?: number } | undefined = undefined;

      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      if (side === "top" || side === "bottom") {
        const desiredLeft = centerX - panelW / 2;
        left = clamp(
          desiredLeft,
          SCREEN_MARGIN_PX,
          vw - SCREEN_MARGIN_PX - panelW
        );
        if (side === "top") {
          top = rect.top - panelH - OFFSET_PX - effectiveArrow / 2;
        } else {
          top = rect.bottom + OFFSET_PX + effectiveArrow / 2;
        }
        top = clamp(top, SCREEN_MARGIN_PX, vh - SCREEN_MARGIN_PX - panelH);

        if (showArrow) {
          const arrowLeft = clamp(
            centerX - left - ARROW_SIZE_PX / 2,
            8,
            panelW - 8
          );
          arrowOffset = { left: arrowLeft };
        }
      } else {
        const desiredTop = centerY - panelH / 2;
        top = clamp(
          desiredTop,
          SCREEN_MARGIN_PX,
          vh - SCREEN_MARGIN_PX - panelH
        );
        if (side === "left") {
          left = rect.left - panelW - OFFSET_PX - effectiveArrow / 2;
        } else {
          left = rect.right + OFFSET_PX + effectiveArrow / 2;
        }
        left = clamp(left, SCREEN_MARGIN_PX, vw - SCREEN_MARGIN_PX - panelW);

        if (showArrow) {
          const arrowTop = clamp(
            centerY - top - ARROW_SIZE_PX / 2,
            8,
            panelH - 8
          );
          arrowOffset = { top: arrowTop };
        }
      }

      setCoords({ top, left, side, arrowOffset });
    }, [open, anchor, position, showArrow]);

    useLayoutEffect(() => {
      if (!open) return;
      recalc();
    }, [open, recalc]);

    useEffect(() => {
      if (!open) return;
      const handle = () => recalc();
      window.addEventListener("resize", handle);
      window.addEventListener("scroll", handle, true);
      const anchorEl = getAnchorElement(anchor);
      const panelEl = internalPanelRef.current;
      let ro: ResizeObserver | undefined;
      if ("ResizeObserver" in window) {
        ro = new ResizeObserver(handle);
        anchorEl && ro.observe(anchorEl);
        panelEl && ro.observe(panelEl);
      }
      return () => {
        window.removeEventListener("resize", handle);
        window.removeEventListener("scroll", handle, true);
        ro?.disconnect();
      };
    }, [open, recalc]);

    if (!open) return null;

    const side = coords?.side ?? position ?? "bottom";
    const arrowPosClass = ARROW_POSITIONING_CLASSES[side];

    // Detect if Popover has a Title child
    const hasTitle = Children.toArray(children).some(
      (child) =>
        isValidElement(child) &&
        (child.type as any)?.displayName === "PopoverTitle"
    );

    // Colors
    const panelBgClass = "bg-gray-800";
    const titleBgClass = "bg-gray-700";
    const borderColorClass = "border-gray-600";
    const borderPositionClass = ARROW_BORDER_POSITIONING_CLASSES[side];
    const arrowOverTitle =
      (hasTitle && side === "bottom") ||
      (hasTitle &&
        (side === "left" || side === "right") &&
        (coords?.arrowOffset?.top ?? Number.POSITIVE_INFINITY) <
          (
            internalPanelRef.current?.querySelector(
              "[data-popover-title]"
            ) as HTMLElement | null
          )?.clientHeight!);
    const arrowFillBgClass = arrowOverTitle ? titleBgClass : panelBgClass;

    const setPanelRefs = (node: HTMLDivElement | null) => {
      internalPanelRef.current = node;
      if (typeof ref === "function") {
        ref(node);
      } else if (ref) {
        (ref as { current: HTMLDivElement | null }).current = node;
      }
    };

    const panel = (
      <div
        role="tooltip"
        ref={setPanelRefs}
        className={clsx(
          "absolute z-50 inline-block text-sm transition-opacity duration-300",
          "text-gray-400 bg-gray-800 border border-gray-600 rounded-lg shadow",
          coords ? "opacity-100 visible" : "opacity-0 invisible",
          className
        )}
        style={{ top: coords?.top, left: coords?.left }}
        aria-hidden={!coords}
      >
        {children}
        {showArrow ? (
          <div
            className={clsx(
              "absolute w-[10px] h-[10px] rotate-45 pointer-events-none",
              borderColorClass,
              borderPositionClass,
              arrowPosClass,
              arrowFillBgClass
            )}
            style={{
              left: coords?.arrowOffset?.left,
              top: coords?.arrowOffset?.top,
            }}
          ></div>
        ) : null}
      </div>
    );

    return createPortal(panel, document.body);
  }
);

export const Popover = PopoverImpl as unknown as PopoverComponent;
Popover.Title = PopoverTitle;
