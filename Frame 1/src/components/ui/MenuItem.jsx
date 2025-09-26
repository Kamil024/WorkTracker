'use client';
import Link from'next/link';
 import MenuText from'./MenuText';

const MenuItem = ({
  text,
  href = '#',
  isActive = false,
  onClick,
  className = '',
  ...props
}) => {
  const handleClick = (e) => {
    if (typeof onClick === 'function') {
      onClick(e)
    }
  }

  const itemContent = (
    <div 
      className={`flex flex-row justify-start items-center w-full px-[10px] py-[10px] transition-colors duration-200 hover:bg-gray-600 hover:bg-opacity-30 rounded-md cursor-pointer ${className}`}
      role="menuitem"
      tabIndex={0}
      onClick={handleClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault()
          handleClick(e)
        }
      }}
      {...props}
    >
      <MenuText 
        text={text}
        className="mt-[6px] mb-[6px]"
      />
    </div>
  )

  if (href && href !== '#') {
    return (
      <Link href={href} className="w-full">
        {itemContent}
      </Link>
    )
  }

  return itemContent
}

export default MenuItem