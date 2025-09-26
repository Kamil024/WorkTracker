'use client';
import { useState } from 'react';
 import MenuItem from'../ui/MenuItem';

const SidebarMenu = ({ 
  onMenuItemClick, 
  activeItem = 'overview',
  className = '',
  ...props 
}) => {
  const [selectedItem, setSelectedItem] = useState(activeItem)

  const menuItems = [
    {
      id: 'overview',
      text: '📊 Overview',
      href: '/dashboard/overview'
    },
    {
      id: 'add-deadline',
      text: '➕ Add Deadline',
      href: '/dashboard/add-deadline'
    },
    {
      id: 'upcoming-deadlines',
      text: '⏰ Upcoming Deadlines',
      href: '/dashboard/upcoming-deadlines'
    },
    {
      id: 'my-tasks',
      text: '📝 My Tasks',
      href: '/dashboard/my-tasks'
    },
    {
      id: 'progress-reports',
      text: '📈 Progress Reports',
      href: '/dashboard/progress-reports'
    }
  ]

  const handleMenuItemClick = (item) => {
    setSelectedItem(item.id)
    
    if (typeof onMenuItemClick === 'function') {
      onMenuItemClick(item)
    }
  }

  return (
    <nav 
      className={`flex flex-col justify-start items-center w-full ${className}`}
      role="navigation"
      aria-label="Sidebar menu"
      {...props}
    >
      {menuItems.map((item) => (
        <MenuItem
          key={item.id}
          text={item.text}
          href={item.href}
          isActive={selectedItem === item.id}
          onClick={() => handleMenuItemClick(item)}
          className="w-full"
        />
      ))}
    </nav>
  )
}

export default SidebarMenu