
import React from 'react';
import { IncidentReport, RecommendedAction } from '../types';
import { ParamedicIcon, PoliceIcon } from './icons';

interface AlertModalProps {
  incident: IncidentReport;
  onClose: () => void;
}

export const AlertModal: React.FC<AlertModalProps> = ({ incident, onClose }) => {
  const isPolice = incident.recommendedAction === RecommendedAction.NOTIFY_AUTHORITIES;
  const isParamedics = incident.recommendedAction === RecommendedAction.NOTIFY_PARAMEDICS;
  
  const iconColor = isPolice ? 'text-red-500' : 'text-blue-500';
  const bgColor = isPolice ? 'bg-red-500/10' : 'bg-blue-500/10';
  const buttonColor = isPolice ? 'bg-red-600 hover:bg-red-500' : 'bg-blue-600 hover:bg-blue-500';

  const Icon = isPolice ? PoliceIcon : ParamedicIcon;
  const title = isPolice ? "AUTHORITIES ALERTED" : "PARAMEDICS ALERTED";

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4" onClick={onClose}>
      <div 
        className={`relative w-full max-w-lg bg-gray-900 border-2 ${isPolice ? 'border-red-500' : 'border-blue-500'} rounded-2xl shadow-2xl p-8 text-center animate-pulse-slow transform scale-100 transition-transform duration-300`} 
        onClick={(e) => e.stopPropagation()}
      >
        <div className={`mx-auto mb-6 w-24 h-24 rounded-full flex items-center justify-center ${bgColor}`}>
          <Icon className={`w-16 h-16 ${iconColor}`} />
        </div>
        
        <h2 className={`text-3xl font-bold tracking-wider uppercase ${iconColor}`}>{title}</h2>
        <p className="text-lg text-gray-200 mt-4">
          <span className="font-bold">{incident.incidentType}</span> detected at timestamp <span className="font-mono text-cyan-400">@{incident.timestamp}</span>.
        </p>
        <p className="text-gray-400 mt-2">{incident.description}</p>
        
        <button 
          onClick={onClose} 
          className={`mt-8 w-full ${buttonColor} text-white font-bold py-3 px-6 rounded-lg transition-colors duration-300 focus:outline-none focus:ring-4 ${isPolice ? 'focus:ring-red-400/50' : 'focus:ring-blue-400/50'}`}
        >
          Acknowledge & Dismiss
        </button>
      </div>
       <style>{`
        @keyframes pulse-slow {
          0%, 100% { box-shadow: 0 0 0 0 ${isPolice ? 'rgba(239, 68, 68, 0.4)' : 'rgba(59, 130, 246, 0.4)'}; }
          70% { box-shadow: 0 0 0 20px rgba(239, 68, 68, 0); }
        }
        .animate-pulse-slow {
          animation: pulse-slow 2s infinite;
        }
      `}</style>
    </div>
  );
};
