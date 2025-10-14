import type { FC, ReactNode, RefObject } from "react";
import { useEffect, useRef } from "react";
import { Popover } from "../Popover/Popover";

export type DropdownProps = {
  open: boolean;
  onClose: () => void;
  anchor: RefObject<HTMLElement | null> | HTMLElement | null;
  className?: string;
  children: ReactNode;
};

export const Dropdown: FC<DropdownProps> = ({
  open,
  onClose,
  anchor,
  className,
  children,
}: DropdownProps) => {
  const panelRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) return;
    const handleMouseDown = (e: MouseEvent) => {
      const target = e.target as Node;
      const insidePanel = panelRef.current?.contains(target);
      const anchorEl =
        anchor && "current" in (anchor as RefObject<HTMLElement | null>)
          ? (anchor as RefObject<HTMLElement | null>).current
          : (anchor as HTMLElement | null);
      const insideAnchor = anchorEl?.contains(target);
      if (!insidePanel && !insideAnchor) onClose();
    };
    document.addEventListener("mousedown", handleMouseDown);
    return () => document.removeEventListener("mousedown", handleMouseDown);
  }, [open, onClose, anchor]);

  if (!open) return null;

  return (
    <Popover
      anchor={anchor}
      open={open}
      position="bottom"
      showArrow={false}
      className={className}
      ref={panelRef}
    >
      {children}
    </Popover>
  );
};
