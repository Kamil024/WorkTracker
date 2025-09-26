import DashboardPage from './DashboardPage';

export const metadata = {
  title: 'Task Management Dashboard - TaskFlow Pro',
  description: 'Comprehensive task management dashboard for organizing projects, tracking deadlines, managing tasks, and generating progress reports. Streamline your workflow with TaskFlow Pro.',
  keywords: 'task management dashboard, project organization, deadline tracking, task tracking, progress reports, team productivity, workflow management',
  
  openGraph: {
    title: 'Task Management Dashboard - TaskFlow Pro',
    description: 'Organize, track, and complete projects efficiently with our intuitive task management dashboard. Access overview insights, manage deadlines, and track progress.',
  }
}

export default function Page() {
  return <DashboardPage />
}