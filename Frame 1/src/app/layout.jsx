import '../styles/index.css'

export const viewport = {
  width: 'device-width',
  initialScale: 1,
}

export const metadata = {
  title: {
    default: 'TaskFlow Pro - Task Management Dashboard',
    template: 'TaskFlow Pro | %s',
  },
  description: 'Comprehensive task management platform for teams and individuals. Organize projects, track deadlines, manage tasks, and generate progress reports efficiently.',
  keywords: 'task management, project tracking, deadline management, team collaboration, progress reports, productivity',
  
  openGraph: {
    type: 'website',
    title: {
      default: 'TaskFlow Pro - Task Management Dashboard',
      template: 'TaskFlow Pro | %s',
    },
    description: 'Streamline your workflow with TaskFlow Pro. Manage tasks, track deadlines, and boost team productivity with our intuitive dashboard.',
  },
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}<script type="module" src="https://static.rocket.new/rocket-web.js?_cfg=https%3A%2F%2Fjaysonka9838back.builtwithrocket.new&_be=https%3A%2F%2Fapplication.rocket.new&_v=0.1.8"></script>
</body>
    </html>
  )
}