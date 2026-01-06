import React, { useEffect, useState } from 'react';
import { useAppStore } from '../../store/useAppStore';

const PersonaGrid = () => {
  const { selectedPersonaId, selectPersona, personas, setPersonas } = useAppStore();
  const [hoveredId, setHoveredId] = useState<string | null>(null);

  useEffect(() => {
    // 추후 API 연결 시 setPersonas로 덮어쓰기
  }, [setPersonas]);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {personas.map((persona) => {
        const isSelected = persona.id === selectedPersonaId;

        return (
          <button
            key={persona.id}
            type="button"
            onClick={() => selectPersona(isSelected ? null : persona.id)} // ✅ 핵심
            onMouseEnter={() => setHoveredId(persona.id)}
            onMouseLeave={() => setHoveredId(null)}
            className={`
              relative p-5 text-left border-2 border-black transition-all duration-200 h-full flex flex-col
              ${isSelected
                ? 'bg-yellow-300 translate-x-[2px] translate-y-[2px] shadow-none'
                : 'bg-white shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] hover:bg-white/80'
              }
            `}
          >
            <h3 className="text-lg font-black mb-1 uppercase italic tracking-tight leading-tight">
              {persona.name}
            </h3>

            <p className="text-xs font-bold text-gray-500 mb-3 border-b-2 border-black/10 pb-1 inline-block">
              {persona.tone}
            </p>

            <p className="text-xs font-medium leading-relaxed mb-4 text-gray-800 flex-1 break-keep">
              {persona.desc}
            </p>

            <div className="flex flex-wrap gap-1 mt-auto pt-2">
              {persona.keywords.map((kw, idx) => (
                <span
                  key={`${persona.id}-${kw}-${idx}`}
                  className="text-[10px] font-bold border border-black px-1.5 py-0.5 bg-white whitespace-nowrap"
                >
                  #{kw}
                </span>
              ))}
            </div>
          </button>
        );
      })}
    </div>
  );
};

export default PersonaGrid;