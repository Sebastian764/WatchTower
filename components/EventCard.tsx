
import React from 'react';
import { IncidentReport, IncidentType, RecommendedAction } from '../types';
import { AlertIcon, ParamedicIcon, PoliceIcon } from './icons';

interface EventCardProps {
  incident: IncidentReport;
}

const getCardStyle = (action: RecommendedAction) => {
    switch(action) {
        case RecommendedAction.NOTIFY_AUTHORITIES:
            return 'border-l-4 border-red-500 bg-red-900/20';
        case RecommendedAction.NOTIFY_PARAMEDICS:
            return 'border-l-4 border-blue-500 bg-blue-900/20';
        default:
            return 'border-l-4 border-yellow-500 bg-yellow-900/20';
    }
}

const getIcon = (action: RecommendedAction) => {
    switch(action) {
        case RecommendedAction.NOTIFY_AUTHORITIES:
            return <PoliceIcon className="h-6 w-6 text-red-400" />;
        case RecommendedAction.NOTIFY_PARAMEDICS:
            return <ParamedicIcon className="h-6 w-6 text-blue-400" />;
        default:
            return <AlertIcon className="h-6 w-6 text-yellow-400" />;
    }
}

export const EventCard: React.FC<EventCardProps> = ({ incident }) => {
    return (
        <div className={`p-4 rounded-md shadow-md transition-transform hover:scale-105 ${getCardStyle(incident.recommendedAction)}`}>
            <div className="flex items-start gap-4">
                <div className="flex-shrink-0 mt-1">
                    {getIcon(incident.recommendedAction)}
                </div>
                <div>
                    <div className="flex items-baseline gap-3">
                        <p className="font-bold text-lg text-gray-100">{incident.incidentType}</p>
                        <span className="text-sm font-mono bg-gray-700 text-cyan-300 px-2 py-0.5 rounded">
                           @{incident.timestamp}
                        </span>
                    </div>
                    <p className="text-gray-300 mt-1">{incident.description}</p>
                    <p className="text-xs text-gray-400 mt-2">Action: {incident.recommendedAction}</p>
                </div>
            </div>
        </div>
    )
}
