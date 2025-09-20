
export enum AnalysisStatus {
  IDLE = 'Awaiting video file',
  ANALYZING = 'Analyzing footage...',
  SUCCESS = 'Analysis Complete',
  ERROR = 'An error occurred during analysis',
}

export enum IncidentType {
  NONE = 'None',
  ROBBERY = 'Robbery',
  MEDICAL_EMERGENCY = 'Medical Emergency',
  FIGHT = 'Altercation/Fight',
  VANDALISM = 'Vandalism',
  OTHER = 'Other',
}

export enum RecommendedAction {
  NONE = 'None',
  NOTIFY_AUTHORITIES = 'Notify Authorities',
  NOTIFY_PARAMEDICS = 'Notify Paramedics',
  MONITOR = 'Continue Monitoring',
}

export interface IncidentReport {
  timestamp: string;
  incidentType: IncidentType;
  description: string;
  recommendedAction: RecommendedAction;
}

export interface GeminiResponse {
  incidents: IncidentReport[];
}
