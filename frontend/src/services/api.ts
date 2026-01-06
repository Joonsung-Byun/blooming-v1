import type { ChannelType, CustomerPersona } from '../types/api';

// ⚠️ 백엔드 개발 전까지는 true로 설정해서 가짜 응답을 받습니다.
const USE_MOCK_MODE = true; 

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

interface GenerateRequestParams {
  userId: string;
  channel: ChannelType;
  intention?: string | null;     
  hasBrand?: boolean;
  targetBrand?: string;
  beautyProfile?: Record<string, any>; 
  userPrompt?: string; 
}

export class ApiService {
  static async generateMessage(params: GenerateRequestParams): Promise<{ data: any }> {
    // ---------------------------------------------------------
    // [Mock Mode] 백엔드 코드 건드리지 않고 개발 진행하기
    // ---------------------------------------------------------
    if (USE_MOCK_MODE) {
      console.log("⚠️ MOCK MODE: Generating message with params:", params);
      
      // 1.5초 딜레이(생성 척)
      await new Promise(resolve => setTimeout(resolve, 1500));

      // 가짜 응답 리턴
      return {
        data: {
          content: `(가상 결과) [${params.channel}] 고객님, ${params.intention || '프로모션'}을 제안합니다!\n\n선택하신 톤: ${params.beautyProfile?.preferred_tone || '기본'}\n타겟: ${params.hasBrand ? params.targetBrand : '브랜드 없음'}\n\n이 메시지는 백엔드 연결 없이 생성된 테스트 메시지입니다.`,
          channel: params.channel,
          user_id: params.userId,
          generated_at: new Date().toISOString(),
          compliance_log: ["금칙어 통과", "목업 데이터"]
        }
      };
    }
    // ---------------------------------------------------------

    // 실제 백엔드 연결 코드 (나중에 백엔드 API가 /message로 열리면 그때 사용)
    const response = await fetch(`${API_BASE_URL}/message`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: params.userId,
        channel: params.channel,
        intention: params.intention,
        has_brand: params.hasBrand,
        target_brand: params.targetBrand,
        beauty_profile: params.beautyProfile,
        user_prompt: params.userPrompt
      }),
    });

    if (!response.ok) {
      throw new Error('Server Error');
    }
    return await response.json();
  }

  static async getCustomers(): Promise<CustomerPersona[]> {
    // 여기도 일단 Mock으로 비워둠 (다음 단계에서 Supabase로 교체 예정)
    return [];
  }
}