import { FC, ReactNode } from "react";

type TopBarProps = {
  children: ReactNode;
};

export const TopBar: FC<TopBarProps> = ({ children }) => {
  return (
    <nav className="border-gray-200 bg-gray-900">
      <div className="max-w-screen-xl flex flex-wrap items-center justify-between mx-auto p-4">
        {children}
      </div>
    </nav>
  );
};
