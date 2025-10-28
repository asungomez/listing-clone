import { FC } from "react";

export const LoadingSkeleton: FC = () => {
  return (
    <div className="min-h-screen bg-gray-900 animate-pulse">
      {/* Page content */}
      <div className="max-w-7xl mx-auto px-4 md:px-6 py-6 grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Main */}
        <main className="md:col-span-9 space-y-6">
          <div className="h-8 w-1/3 rounded bg-gray-700" />

          <div className="space-y-4">
            <div className="h-48 w-full rounded bg-gray-700" />
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="h-32 rounded bg-gray-700" />
              <div className="h-32 rounded bg-gray-700" />
            </div>
            <div className="space-y-2">
              <div className="h-4 w-full rounded bg-gray-700" />
              <div className="h-4 w-5/6 rounded bg-gray-700" />
              <div className="h-4 w-2/3 rounded bg-gray-700" />
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};
