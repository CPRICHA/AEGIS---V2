import { useState, cloneElement, isValidElement } from 'react'
import RightPanel from '../panels/RightPanel'
import NotificationPanel from '../panels/NotificationPanel'
import CoordinationPanel from '../panels/CoordinationPanel'

export default function AppShell({ children }) {
  const [isAsideOpen, setIsAsideOpen] = useState(true)

  const child = isValidElement(children)
    ? cloneElement(children, { isAsideOpen, setIsAsideOpen })
    : children

  return (
    <div className="app-shell">
      <main className="app-shell__main">
        {child}
      </main>

      <aside
        className={`app-shell__aside ${isAsideOpen ? '' : 'app-shell__aside--closed'}`}
        aria-hidden={!isAsideOpen}
      >
        <div className="app-shell__aside-body">
          <RightPanel />
          <NotificationPanel />
          <CoordinationPanel />
        </div>
      </aside>
    </div>
  )
}
