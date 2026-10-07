import { useChat } from '../chat'

/**
 * "Open late. Ask the librarian any time." — and it means it: the line opens the
 * reference desk. It looked clickable before and wasn't, which is worse than not
 * looking clickable at all.
 */
export function OpenLate({ className = '' }: { className?: string }) {
  const { setOpen } = useChat()
  return (
    <button
      type="button"
      className={`open-late ${className}`}
      onClick={() => setOpen(true)}
    >
      <span className="lamp-dot" aria-hidden />
      Open late. Ask the librarian any time.
    </button>
  )
}
