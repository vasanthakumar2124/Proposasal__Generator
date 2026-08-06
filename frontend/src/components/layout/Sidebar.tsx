import { NavLink } from 'react-router-dom'
import { cn } from '../../lib/utils'
import { useAppSelector } from '../../store/hooks'
import {
  LayoutDashboard,
  FileText,
  FolderOpen,
  Users,
  ChevronLeft,
  ChevronRight,
  Sparkles,
  ScrollText,
  CreditCard,
  BarChart3,
  Activity as ActivityIcon,
  BookOpen,
} from 'lucide-react'
import { Button } from '../../components/ui/Button'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/workspace', icon: FolderOpen, label: 'Workspace' },
  { to: '/projects', icon: FileText, label: 'Projects' },
  { to: '/clients', icon: Users, label: 'Clients' },
  { to: '/knowledge', icon: BookOpen, label: 'Knowledge' },
  { to: '/generate', icon: Sparkles, label: 'Generate' },
  { to: '/history', icon: ScrollText, label: 'Proposals' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/activity', icon: ActivityIcon, label: 'Activity' },
  { to: '/billing', icon: CreditCard, label: 'Billing' },
]

interface SidebarProps {
  collapsed: boolean
  onToggle: () => void
}

export function Sidebar({ collapsed, onToggle }: SidebarProps) {
  const { user } = useAppSelector((state) => state.auth)

  return (
    <aside
      className={cn(
        'flex flex-col border-r bg-sidebar text-sidebar-foreground transition-all duration-300',
        collapsed ? 'w-16' : 'w-64'
      )}
    >
      <div className="flex h-14 items-center justify-between border-b border-sidebar-border px-4">
        {!collapsed && (
          <span className="text-lg font-bold tracking-tight">ProposalCraft</span>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={onToggle}
          className="text-sidebar-foreground hover:bg-sidebar-accent"
        >
          {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
        </Button>
      </div>

      <nav className="flex-1 space-y-1 p-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-sidebar-primary text-sidebar-primary-foreground'
                  : 'text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground',
                collapsed && 'justify-center px-2'
              )
            }
          >
            <item.icon className="h-5 w-5 shrink-0" />
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-sidebar-border p-3">
        {!collapsed && user && (
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-sidebar-primary text-xs font-bold">
              {user.name.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 truncate">
              <p className="text-sm font-medium">{user.name}</p>
              <p className="text-xs text-sidebar-foreground/60">{user.email}</p>
            </div>
          </div>
        )}
      </div>
    </aside>
  )
}
