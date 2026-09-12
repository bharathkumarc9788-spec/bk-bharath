export function SearchBar({ value, onChange, placeholder = 'Search students…' }) {
  return (
    <input
      className="form-group search-input"
      style={{
        padding: '9px 12px', borderRadius: 10, border: '1px solid var(--border)',
        fontSize: 14, minWidth: 220,
      }}
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder={placeholder}
    />
  )
}

export default SearchBar