
import React, { useRef } from 'react';
import { Loader } from './Loader';

interface VideoUploadProps {
  onFileChange: (file: File | null) => void;
  onAnalyze: () => void;
  isLoading: boolean;
  hasFile: boolean;
}

export const VideoUpload: React.FC<VideoUploadProps> = ({ onFileChange, onAnalyze, isLoading, hasFile }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null;
    onFileChange(file);
  };
  
  const handleButtonClick = () => {
      fileInputRef.current?.click();
  }

  return (
    <div className="flex flex-col sm:flex-row items-center justify-center gap-4 w-full">
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileSelect}
        accept="video/mp4"
        className="hidden"
      />
      <button 
        onClick={handleButtonClick}
        className="w-full sm:w-auto flex-grow text-center bg-gray-700 hover:bg-gray-600 text-white font-bold py-3 px-6 rounded-lg transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-cyan-500"
      >
        {hasFile ? 'Change Video' : 'Select Video File (.mp4)'}
      </button>

      <button
        onClick={onAnalyze}
        disabled={!hasFile || isLoading}
        className="w-full sm:w-auto flex-grow bg-cyan-600 hover:bg-cyan-500 disabled:bg-cyan-800 disabled:text-gray-400 disabled:cursor-not-allowed text-white font-bold py-3 px-6 rounded-lg transition-colors duration-300 focus:outline-none focus:ring-2 focus:ring-cyan-400 flex items-center justify-center gap-2"
      >
        {isLoading ? (
          <>
            <Loader className="h-5 w-5" />
            Analyzing...
          </>
        ) : (
          'Analyze Video'
        )}
      </button>
    </div>
  );
};
