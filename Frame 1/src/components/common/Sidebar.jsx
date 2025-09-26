'use client';
import { useState } from 'react';
import { twMerge } from 'tailwind-merge';
 import SidebarMenu from'./SidebarMenu';

const Sidebar = ({
  className,
  onMenuItemClick,
  activeItem,
  isCollapsed = false,
  onToggleCollapse,
  ...props
}) => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen)
  }

  const handleMenuItemClick = (item) => {
    // Close mobile menu when item is clicked
    setIsMobileMenuOpen(false)
    
    if (typeof onMenuItemClick === 'function') {
      onMenuItemClick(item)
    }
  }

  return (
    <>
      {/* Mobile Hamburger Menu Button */}
      <button
        className="fixed top-4 left-4 z-50 block lg:hidden p-3 bg-bg-background-secondary text-text-primary rounded-md hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-400 transition-colors duration-200"
        onClick={toggleMobileMenu}
        aria-label="Toggle navigation menu"
        aria-expanded={isMobileMenuOpen}
      >
        <svg
          className="w-6 h-6"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          {isMobileMenuOpen ? (
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          ) : (
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          )}
        </svg>
      </button>

      {/* Mobile Overlay */}
      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={toggleMobileMenu}
          aria-hidden="true"
        />
      )}

      {/* Sidebar */}
      <aside
        className={twMerge(
          // Base styles
          'fixed top-0 left-0 h-full bg-bg-sidebar-background transition-transform duration-300 ease-in-out z-40',
          // Mobile styles - hidden by default, shown when menu is open
          'transform -translate-x-full lg:translate-x-0',
          isMobileMenuOpen && 'translate-x-0',
          // Desktop styles
          'lg:static lg:transform-none',
          // Width handling
          isCollapsed ? 'w-16 lg:w-20' : 'w-full max-w-sm lg:w-[36%] lg:max-w-[400px]',
          // Responsive width
          'sm:max-w-xs md:max-w-sm',
          className
        )}
        role="navigation"
        aria-label="Main navigation"
        {...props}
      >
        {/* Sidebar Content Container */}
        <div className="flex flex-col h-full w-full pt-[70px] px-4 lg:px-0">
          {/* Close button for mobile */}
          <button
            className="absolute top-4 right-4 lg:hidden p-2 text-text-primary hover:bg-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-400 transition-colors duration-200"
            onClick={toggleMobileMenu}
            aria-label="Close navigation menu"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>

          {/* Sidebar Menu */}
          <div className="flex-1 mt-4 lg:mt-0">
            <SidebarMenu
              onMenuItemClick={handleMenuItemClick}
              activeItem={activeItem}
              className="space-y-1"
            />
          </div>

          {/* Optional Footer Content */}
          <div className="mt-auto pb-6 hidden lg:block">
            <div className="text-center text-text-primary opacity-60 text-sm">
              TaskFlow Pro
            </div>
          </div>
        </div>
      </aside>

      {/* Spacer for desktop layout */}
      <div
        className={twMerge(
          'hidden lg:block flex-shrink-0 transition-all duration-300',
          isCollapsed ? 'w-16 lg:w-20' : 'w-[36%] max-w-[400px]'
        )}
        aria-hidden="true"
      />
    </>
  )
}

export default Sidebar