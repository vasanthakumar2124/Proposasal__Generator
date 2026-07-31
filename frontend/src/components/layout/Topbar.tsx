import { Bell, Search, Moon, Sun } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Input } from '../../components/ui/Input'
import { useTheme } from '../../providers/ThemeProvider'
import { useAppSelector } from '../../store/hooks'

export function Topbar() {
  const { theme, setTheme } = useTheme()
  const { user } = useAppSelector((state) => state.auth)

  return (
    <header className="flex h-14 items-center gap-4 border-b bg-background px-6">
      <div className="relative flex-1 max-w-md">
        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Search proposals, clients..."
          className="pl-8"
        />
      </div>

      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
        >
          {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
        </Button>
        <Button variant="ghost" size="icon" className="relative">
          <Bell className="h-4 w-4" />
          <span className="absolute -right-1 -top-1 flex h-4 w-4 items-center justify-center rounded-full bg-destructive text-[10px] text-destructive-foreground">
            3
          </span>
        </Button>
        {user && (
          <div className="flex items-center gap-2 border-l pl-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-xs font-bold text-primary-foreground">
              {user.name.charAt(0).toUpperCase()}
            </div>
            <span className="hidden text-sm font-medium md:block">{user.name}</span>
          </div>
        )}
      </div>
    </header>
  )
}
