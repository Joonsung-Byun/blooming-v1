import { create } from 'zustand';
import { PERSONA_DB } from '../data/PersonaData';
import { PERSONA_OPTIONS, type PersonaOptionSet } from '../data/personaOptions';
import { SKIN_TYPE_OPTIONS, SKIN_CONCERN_OPTIONS, TONE_OPTIONS, KEYWORD_OPTIONS } from '../data/schemaData';
import { CustomerDB } from '../services/customerService';

// 데이터 타입 정의
export interface SimulationData {
  skin_type: string[];
  skin_concerns: string[];
  preferred_tone: string;
  keywords: string[];
}

export type ChannelType = 'APP_PUSH' | 'SMS' | 'KAKAO' | 'EMAIL';

// 페르소나 타입 정의
export interface Persona {
  id: string;
  name: string;
  desc: string;
  tone: string;
  keywords: string[];
}

interface AppState {
  // 상태
  personas: Persona[];
  selectedPersonaId: string | null;
  simulationData: SimulationData;
  intention: string | null;
  isBrandTargeting: boolean;
  targetBrand: string;
  selectedChannel: ChannelType | null;
  isGenerating: boolean;
  generatedResult: string | null;
  activeOptions: PersonaOptionSet;
  customerList: CustomerDB[];
  selectedCustomer: CustomerDB | null;

  // 액션
  setPersonas: (list: Persona[]) => void;
  setSelectedPersonaId: (id: string | null) => void;
  setSimulationData: (data: Partial<SimulationData>) => void;
  setIntention: (val: string | null) => void;
  setBrandTargeting: (val: boolean) => void;
  setTargetBrand: (brand: string) => void;
  setSelectedChannel: (channel: ChannelType | null) => void;
  setIsGenerating: (val: boolean) => void;
  setGeneratedResult: (result: string | null) => void;
  setCustomerList: (list: CustomerDB[]) => void;
  setSelectedCustomer: (customer: CustomerDB | null) => void;

  // 기능 액션
  resetAll: () => void;
  selectPersona: (id: string | null) => void;
}

// 초기값 상수화
const INITIAL_SIMULATION_DATA: SimulationData = {
  skin_type: [],
  skin_concerns: [],
  preferred_tone: 'Neutral',
  keywords: [],
};

function buildDefaultOptions(): PersonaOptionSet {
  return {
    skinTypes: Object.keys(SKIN_TYPE_OPTIONS),
    concerns: Object.keys(SKIN_CONCERN_OPTIONS),
    tone: Object.keys(TONE_OPTIONS),
    keywords: Object.keys(KEYWORD_OPTIONS),
  };
}

export const useAppStore = create<AppState>((set, get) => ({
  // ✅ 기존 초기값들
  personas: Object.values(PERSONA_DB).map((p) => ({
    ...p,
    keywords: [...p.keywords],
  })),
  selectedPersonaId: null,
  simulationData: { ...INITIAL_SIMULATION_DATA },
  intention: null,
  isBrandTargeting: false,
  targetBrand: '',
  selectedChannel: null,
  isGenerating: false,
  generatedResult: null,
  activeOptions: buildDefaultOptions(),

  // ✅ 추가: 고객 리스트/선택 고객
  customerList: [],
  selectedCustomer: null,

  // ✅ 기존 세터
  setPersonas: (list) => set({ personas: list }),
  setSelectedPersonaId: (id) => set({ selectedPersonaId: id }),
  setSimulationData: (newData) =>
    set((state) => ({
      simulationData: { ...state.simulationData, ...newData },
    })),
  setIntention: (val) => set({ intention: val }),
  setBrandTargeting: (val) => set({ isBrandTargeting: val }),
  setTargetBrand: (brand) => set({ targetBrand: brand }),
  setSelectedChannel: (channel) => set({ selectedChannel: channel }),
  setIsGenerating: (val) => set({ isGenerating: val }),
  setGeneratedResult: (result) => set({ generatedResult: result }),

  // ✅ 추가: 고객 리스트 세터
  setCustomerList: (list) => set({ customerList: list }),

  // ✅ 추가: 고객 선택 시 simulationData에 반영
  setSelectedCustomer: (customer) =>
    set((state) => {
      if (!customer) {
        return {
          selectedCustomer: null,
          simulationData: { ...INITIAL_SIMULATION_DATA },
        };
      }

      return {
        selectedCustomer: customer,
        simulationData: {
          ...state.simulationData,
          skin_type: customer.skin_type ?? [],
          skin_concerns: customer.skin_concerns ?? [],
          preferred_tone: customer.preferred_tone ?? 'Neutral',
          keywords: customer.keywords ?? [],
        },
      };
    }),

  // ✅ 리셋 기능 (고객도 같이 리셋)
  resetAll: () =>
    set({
      selectedPersonaId: null,
      selectedCustomer: null,
      customerList: [], // 필요 없으면 제거 가능
      activeOptions: buildDefaultOptions(),
      simulationData: { ...INITIAL_SIMULATION_DATA },
      intention: null,
      isBrandTargeting: false,
      targetBrand: '',
      selectedChannel: null,
      isGenerating: false,
      generatedResult: null,
    }),

  // ✅ 페르소나 선택 기능 (고객 선택이 있으면 그 값으로 simulationData 다시 채움)
  selectPersona: (id) => {
    if (!id) {
      set({
        selectedPersonaId: null,
        activeOptions: buildDefaultOptions(),
        simulationData: { ...INITIAL_SIMULATION_DATA },
      });

      // ✅ 고객이 선택돼 있으면 초기화 후 다시 고객값 주입
      const customer = get().selectedCustomer;
      if (customer) {
        get().setSelectedCustomer(customer);
      }
      return;
    }

    const allowed = PERSONA_OPTIONS[id] ?? buildDefaultOptions();

    set({
      selectedPersonaId: id,
      activeOptions: allowed,
      simulationData: { ...INITIAL_SIMULATION_DATA },
    });

    // ✅ 고객이 선택돼 있으면 초기화 후 다시 고객값 주입
    const customer = get().selectedCustomer;
    if (customer) {
      get().setSelectedCustomer(customer);
    }
  },
}));