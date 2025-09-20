
import React, { useState, useCallback } from 'react';
import { Header } from './components/Header';
import { VideoUpload } from './components/VideoUpload';
import { VideoPlayer } from './components/VideoPlayer';
import { StatusPanel } from './components/StatusPanel';
import { EventLog } from './components/EventLog';
import { AlertModal } from './components/AlertModal';
import { analyzeVideo } from './services/geminiService';
import { AnalysisStatus, IncidentReport, RecommendedAction } from './types';

const App: React.FC = () => {
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoUrl, setVideoUrl] = useState<string | null>(null);
  const [status, setStatus] = useState<AnalysisStatus>(AnalysisStatus.IDLE);
  const [incidents, setIncidents] = useState<IncidentReport[]>([]);
  const [activeAlert, setActiveAlert] = useState<IncidentReport | null>(null);

  const handleFileChange = (file: File | null) => {
    if (file) {
      setVideoFile(file);
      const url = URL.createObjectURL(file);
      setVideoUrl(url);
      setIncidents([]);
      setStatus(AnalysisStatus.IDLE);
      setActiveAlert(null);
    } else {
      setVideoFile(null);
      setVideoUrl(null);
    }
  };

  const handleAnalyze = useCallback(async () => {
    if (!videoFile) return;

    setStatus(AnalysisStatus.ANALYZING);
    setIncidents([]);
    setActiveAlert(null);

    try {
      const response = await analyzeVideo(videoFile);
      setIncidents(response.incidents);
      setStatus(AnalysisStatus.SUCCESS);

      const criticalIncident = response.incidents.find(
        (inc) =>
          inc.recommendedAction === RecommendedAction.NOTIFY_AUTHORITIES ||
          inc.recommendedAction === RecommendedAction.NOTIFY_PARAMEDICS
      );

      if (criticalIncident) {
        setActiveAlert(criticalIncident);
      }
    } catch (error) {
      console.error('Analysis failed:', error);
      setStatus(AnalysisStatus.ERROR);
    }
  }, [videoFile]);

  const handleCloseAlert = () => {
    setActiveAlert(null);
  };

  return (
    <div className="min-h-screen bg-gray-900 text-gray-200 font-sans">
      <Header />
      <main className="container mx-auto p-4 md:p-8">
        <div className="bg-gray-800 rounded-2xl shadow-2xl p-6 mb-8">
            <VideoUpload
                onFileChange={handleFileChange}
                onAnalyze={handleAnalyze}
                isLoading={status === AnalysisStatus.ANALYZING}
                hasFile={!!videoFile}
            />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 bg-gray-800 rounded-2xl shadow-2xl p-4 flex flex-col">
            <h2 className="text-xl font-bold mb-4 px-2 text-cyan-400">Footage Preview</h2>
            <VideoPlayer videoUrl={videoUrl} />
          </div>
          <div className="bg-gray-800 rounded-2xl shadow-2xl p-6 flex flex-col">
            <StatusPanel status={status} />
            <EventLog incidents={incidents} />
          </div>
        </div>
      </main>
      {activeAlert && (
        <AlertModal incident={activeAlert} onClose={handleCloseAlert} />
      )}
    </div>
  );
};

export default App;
