"use client";

import { useEffect, useMemo, useState } from "react";

export type MatrixRow = {
  id: number;
  module: string;
  module_display: string;
  action: string;
  assigned: boolean;
};

type PermissionMatrixEditorProps = {
  rows: MatrixRow[];
  readOnly?: boolean;
  saving?: boolean;
  onSave?: (permissionIds: number[]) => void;
};

export function PermissionMatrixEditor({
  rows,
  readOnly = false,
  saving = false,
  onSave,
}: PermissionMatrixEditorProps) {
  const [selected, setSelected] = useState<Set<number>>(() => new Set(rows.filter((r) => r.assigned).map((r) => r.id)));

  useEffect(() => {
    setSelected(new Set(rows.filter((r) => r.assigned).map((r) => r.id)));
  }, [rows]);

  const grouped = useMemo(() => {
    const map = new Map<string, MatrixRow[]>();
    for (const row of rows) {
      const list = map.get(row.module) ?? [];
      list.push(row);
      map.set(row.module, list);
    }
    return Array.from(map.entries()).sort(([a], [b]) => a.localeCompare(b));
  }, [rows]);

  function toggle(id: number) {
    if (readOnly) return;
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function toggleModule(moduleRows: MatrixRow[], checked: boolean) {
    if (readOnly) return;
    setSelected((prev) => {
      const next = new Set(prev);
      for (const row of moduleRows) {
        if (checked) next.add(row.id);
        else next.delete(row.id);
      }
      return next;
    });
  }

  return (
    <div className="space-y-4">
      {!readOnly && onSave ? (
        <div className="flex justify-end">
          <button
            type="button"
            disabled={saving}
            onClick={() => onSave(Array.from(selected))}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-60"
          >
            {saving ? "Saving…" : "Save permissions"}
          </button>
        </div>
      ) : null}

      <div className="overflow-x-auto rounded-xl border border-gray-100">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-3 py-2 text-left font-medium text-gray-600">Module</th>
              {["view", "create", "edit", "delete", "export", "import", "approve"].map((action) => (
                <th key={action} className="px-2 py-2 text-center font-medium capitalize text-gray-600">
                  {action}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {grouped.map(([moduleKey, moduleRows]) => {
              const allChecked = moduleRows.every((r) => selected.has(r.id));
              return (
                <tr key={moduleKey} className="hover:bg-gray-50/80">
                  <td className="px-3 py-2 font-medium text-gray-900">
                    <div className="flex items-center gap-2">
                      {!readOnly ? (
                        <input
                          type="checkbox"
                          checked={allChecked}
                          onChange={(e) => toggleModule(moduleRows, e.target.checked)}
                          aria-label={`Toggle all ${moduleRows[0]?.module_display}`}
                        />
                      ) : null}
                      {moduleRows[0]?.module_display ?? moduleKey}
                    </div>
                  </td>
                  {["view", "create", "edit", "delete", "export", "import", "approve"].map((action) => {
                    const row = moduleRows.find((r) => r.action === action);
                    if (!row) {
                      return <td key={action} className="px-2 py-2 text-center text-gray-300">—</td>;
                    }
                    return (
                      <td key={action} className="px-2 py-2 text-center">
                        <input
                          type="checkbox"
                          checked={selected.has(row.id)}
                          disabled={readOnly}
                          onChange={() => toggle(row.id)}
                          aria-label={`${row.module_display} ${action}`}
                        />
                      </td>
                    );
                  })}
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
