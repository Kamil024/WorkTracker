'use client';

const MenuText = ({
  text = '',
  className = '',
  ...props
}) => {
  return (
    <span
      className={`text-[30px] sm:text-[24px] md:text-[28px] lg:text-[30px] font-normal leading-[37px] text-left text-[#fcfcfc] font-['Inter'] ${className}`}
      {...props}
    >
      {text}
    </span>
  )
}

export default MenuText