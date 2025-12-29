import { ReactNode, useState } from 'react';
import { Sidebar } from './Sidebar';
import { RightPanel } from './RightPanel';
import { BottomDrawer } from './BottomDrawer';

interface DashboardLayoutProps {
  children: ReactNode;
}

export const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  const [isBottomDrawerOpen, setIsBottomDrawerOpen] = useState(false);

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      <Sidebar />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
        
        <BottomDrawer 
          isOpen={isBottomDrawerOpen} 
          onToggle={() => setIsBottomDrawerOpen(!isBottomDrawerOpen)} 
        />
      </div>
      
      <RightPanel />
    </div>
  );
};
