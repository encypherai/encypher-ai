import api from '@/lib/api';

export interface DemoGeneratePayload {
  base_path?: string;
  topics?: string[];
  files_per_topic?: number;
  paragraphs_per_file?: number;
  overwrite?: boolean;
  seed?: number;
}

export interface DemoGenerateResponse {
  base_path: string;
  topics_created: string[];
  total_files: number;
  files_per_topic: number;
  paragraphs_per_file: number;
}

const demoService = {
  async generate(payload: DemoGeneratePayload): Promise<DemoGenerateResponse> {
    const response = await api.post('/demo/generate', payload);
    return response.data;
  },
};

export default demoService;
