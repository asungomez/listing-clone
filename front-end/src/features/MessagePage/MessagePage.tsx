import { FC, ReactNode } from "react";

type MessagePageProps = {
  children: ReactNode;
  direction?: "row" | "col";
};

/**
 * Page for displaying a centered message
 */
export const MessagePage: FC<MessagePageProps> = ({
  children,
  direction = "row",
}) => (
  <section className="bg-gray-900 min-h-screen flex items-center justify-center">
    <div
      className={`text-4xl font-extrabold text-white flex flex-${direction} items-center gap-4`}
    >
      {children}
    </div>
  </section>
);
