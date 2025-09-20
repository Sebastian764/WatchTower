
import React from 'react';
import { AnalysisStatus } from '../types';
import { Loader } from './Loader';

interface StatusPanelProps {
  status: AnalysisStatus;
}

export const StatusPanel: React.FC<StatusPanelProps> = ({ status }) => {
  const getStatusColor = () => {
    switch (status) {
      case AnalysisStatus.ANALYZING:
        return 'text-yellow-400';
      case AnalysisStatus.SUCCESS:
        return 'text-green-400';
      case AnalysisStatus.ERROR:
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="mb-6">
      <h2 className="text-xl font-bold mb-3 text-cyan-400">Analysis Status</h2>
      <div className="flex items-center gap-3 p-4 bg-gray-900/50 rounded-lg">
        {status === AnalysisStatus.ANALYZING && <Loader className="h-5 w-5 text-yellow-400" />}
        <p className={`font-medium ${getStatusColor()}`}>{status}</p>
      </div>
    </div>
  );
};
