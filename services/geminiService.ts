
import { GoogleGenAI, Type } from '@google/genai';
import { GeminiResponse, IncidentReport, IncidentType, RecommendedAction } from '../types';

if (!process.env.API_KEY) {
    throw new Error("API_KEY environment variable not set");
}

const ai = new GoogleGenAI({ apiKey: process.env.API_KEY });

const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onload = () => {
            const result = reader.result as string;
            // remove the "data:mime/type;base64," prefix
            resolve(result.split(',')[1]);
        };
        reader.onerror = (error) => reject(error);
    });
};

export const analyzeVideo = async (videoFile: File): Promise<GeminiResponse> => {
    const base64Video = await fileToBase64(videoFile);

    const prompt = `You are an expert security AI system. Analyze this video footage. Identify any security incidents like robberies, medical emergencies, fights, or vandalism. For each incident, provide its timestamp, a description, classify its type, and recommend an action. If there are no incidents, return an empty 'incidents' array. Respond ONLY with a JSON object adhering to the provided schema.`;

    const responseSchema = {
        type: Type.OBJECT,
        properties: {
            incidents: {
                type: Type.ARRAY,
                items: {
                    type: Type.OBJECT,
                    properties: {
                        timestamp: {
                            type: Type.STRING,
                            description: "The approximate time in the video when the incident occurred (e.g., '00:45').",
                        },
                        incidentType: {
                            type: Type.STRING,
                            enum: Object.values(IncidentType),
                        },
                        description: {
                            type: Type.STRING,
                            description: "A brief, clear description of the incident.",
                        },
                        recommendedAction: {
                            type: Type.STRING,
                            enum: Object.values(RecommendedAction),
                        },
                    },
                    required: ["timestamp", "incidentType", "description", "recommendedAction"],
                },
            },
        },
        required: ["incidents"],
    };

    const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash',
        contents: {
            parts: [
                { text: prompt },
                {
                    inlineData: {
                        mimeType: videoFile.type,
                        data: base64Video,
                    },
                },
            ],
        },
        config: {
            responseMimeType: "application/json",
            responseSchema: responseSchema
        },
    });

    try {
        const jsonText = response.text.trim();
        const parsedResponse: { incidents: IncidentReport[] } = JSON.parse(jsonText);
        return parsedResponse;
    } catch (e) {
        console.error("Failed to parse Gemini response:", response.text);
        throw new Error("Invalid JSON response from API");
    }
};
