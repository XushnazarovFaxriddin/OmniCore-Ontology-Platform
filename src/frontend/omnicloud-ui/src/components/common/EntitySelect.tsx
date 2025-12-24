import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { rootsApi } from '../../api/client';
import type { Root } from '../../types';

type Props = {
  value: string;
  onChange: (entityId: string, entity?: Root) => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  searchPlaceholder?: string;
  showType?: boolean;
};

function EntitySelect({
  value,
  onChange,
  placeholder = 'Select an entity…',
  disabled = false,
  required = false,
  searchPlaceholder = 'Search entities…',
  showType = true,
}: Props) {
  const [query, setQuery] = useState('');

  const { data, isLoading, isError } = useQuery({
    queryKey: ['roots', 'entity-select'],
    queryFn: () => rootsApi.list(0, 1000),
    staleTime: 30_000,
  });

  const entities = data?.items ?? [];

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return entities;
    return entities.filter((e) => {
      const haystack = `${e.name} ${e.root_type} ${e.description ?? ''}`.toLowerCase();
      return haystack.includes(q);
    });
  }, [entities, query]);

  const selected = useMemo(() => entities.find((e) => e.id === value), [entities, value]);

  const handleSelect = (entityId: string) => {
    const entity = entities.find((e) => e.id === entityId);
    onChange(entityId, entity);
  };

  return (
    <div>
      <input
        type="text"
        className="form-input"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={searchPlaceholder}
        disabled={disabled || isLoading || isError}
        style={{ marginBottom: 8 }}
      />
      <select
        className="form-select"
        value={value}
        onChange={(e) => handleSelect(e.target.value)}
        disabled={disabled || isLoading || isError}
        required={required}
      >
        <option value="">{isLoading ? 'Loading…' : placeholder}</option>
        {filtered.map((entity) => (
          <option key={entity.id} value={entity.id}>
            {entity.name}
            {showType ? ` (${entity.root_type})` : ''}
          </option>
        ))}
      </select>

      {selected && (
        <div style={{ marginTop: 6, fontSize: 12, color: 'var(--text-secondary)' }}>
          Selected: {selected.name}
        </div>
      )}
      {isError && (
        <div style={{ marginTop: 6, fontSize: 12, color: 'var(--danger-color)' }}>
          Failed to load entities. Please open Roots page and refresh.
        </div>
      )}
      {data?.has_more && (
        <div style={{ marginTop: 6, fontSize: 12, color: 'var(--text-secondary)' }}>
          Showing first 1000 entities. If you can’t find one, create it in Roots.
        </div>
      )}
    </div>
  );
}

export default EntitySelect;

