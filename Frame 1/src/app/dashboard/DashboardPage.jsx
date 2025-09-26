'use client';
import { useState } from 'react';
import Sidebar from '@/components/common/Sidebar';

export default function DashboardPage() {
  const [activeMenuItem, setActiveMenuItem] = useState('overview');

  const handleMenuItemClick = (item) => {
    setActiveMenuItem(item.id);
  };

  return (
    <main className="flex flex-row justify-start items-center w-full min-h-screen bg-[#171717]">
      {/* Main Content Container */}
      <div className="flex flex-row justify-start items-start w-full px-[20px] sm:px-[30px] lg:px-[40px] mt-[23px] sm:mt-[35px] lg:mt-[46px] mb-[23px] sm:mb-[35px] lg:mb-[46px]">
        
        {/* Sidebar */}
        <Sidebar
          onMenuItemClick={handleMenuItemClick}
          onToggleCollapse={() => {}}
          activeItem={activeMenuItem}
          className="bg-[#323232]"
        />

        {/* Main Content Area */}
        <div className="flex-1 flex justify-center items-center min-h-[400px] sm:min-h-[500px] lg:min-h-[600px] ml-4 lg:ml-0">
          {/* Welcome State with Emoji */}
          <div className="flex flex-col items-center justify-center text-center px-4">
            <div className="text-[60px] sm:text-[80px] md:text-[100px] lg:text-[120px] mb-4 sm:mb-6">
              😊
            </div>
            <h1 className="text-[#fcfcfc] text-[18px] sm:text-[20px] md:text-[24px] lg:text-[28px] font-medium font-['Inter'] mb-2 sm:mb-4">
              Welcome to TaskFlow Pro
            </h1>
            <p className="text-[#fcfcfc] opacity-70 text-[14px] sm:text-[16px] md:text-[18px] font-normal font-['Inter'] max-w-md">
              Select a menu item from the sidebar to get started with managing your tasks and deadlines.
            </p>
          </div>
        </div>

        {/* Floating Emoji Image */}
        <div className="absolute top-[386px] left-[354px] hidden xl:block">
          <img 
            src="/images/img_.png" 
            alt="Floating emoji decoration"
            className="w-[30px] h-[42px]"
          />
        </div>
      </div>
    </main>
  );
}