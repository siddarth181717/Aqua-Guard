import './globals.css';
import Sidebar from '@/components/layout/Sidebar';
import Topbar from '@/components/layout/Topbar';

export const metadata = {
  title: 'AquaGuard - AI-Driven Geospatial Surveillance',
  description: 'Monitor water bodies, detect environmental change, and prioritize restoration using geospatial intelligence.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="flex h-screen overflow-hidden bg-navy-900 text-slate-100">
        <Sidebar />
        <div className="flex-1 flex flex-col min-w-0 overflow-y-auto">
          <Topbar />
          <main className="flex-1 p-6">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
