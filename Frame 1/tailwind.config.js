module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,html,mdx}"],
  darkMode: "class",
  screens: {
    sm: '640px',   
    md: '768px',    
    lg: '1024px',   
    xl: '1280px',
    '2xl': '1536px'
  },
  theme: {
    extend: {
      colors: {
        /* Global Colors */
        background: {
          primary: "var(--global-bg-primary)",
          secondary: "var(--global-bg-secondary)",
        },
        text: {
          primary: "var(--global-text-primary)",
        },
        /* Component-specific Colors */
        sidebar: {
          background: "var(--sidebar-bg)",
        },
        menu: {
          text: "var(--menu-text-color)",
        }
      },
      fontSize: {
        'lg': 'var(--font-size-lg)',
      },
      fontWeight: {
        'normal': 'var(--font-weight-normal)',
      },
      lineHeight: {
        'lg': 'var(--line-height-lg)',
      },
      fontFamily: {
        'primary': 'var(--font-family-primary)',
      },
      spacing: {
        'xs': 'var(--spacing-xs)',
        'sm': 'var(--spacing-sm)',
        'md': 'var(--spacing-md)',
        'lg': 'var(--spacing-lg)',
        'xl': 'var(--spacing-xl)',
        '2xl': 'var(--spacing-2xl)',
        '3xl': 'var(--spacing-3xl)',
      },
      width: {
        'sidebar': 'var(--width-sidebar)',
        'auto': 'var(--width-auto)',
        'flex': 'var(--width-flex)',
        'full': 'var(--width-full)',
      }
    },
  },
  plugins: []
};