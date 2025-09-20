
import React from 'react';
import { IncidentReport } from '../types';
import { EventCard } from './EventCard';

interface EventLogProps {
  incidents: IncidentReport[];
}

export const EventLog: React.FC<EventLogProps> = ({ incidents }) => {
  return (
    <div className="flex-grow flex flex-col">
      <h2 className="text-xl font-bold mb-3 text-cyan-400">Event Log</h2>
      <div className="flex-grow bg-gray-900/50 rounded-lg p-2 overflow-y-auto h-64 md:h-auto">
        {incidents.length > 0 ? (
          <div className="space-y-3 p-2">
            {incidents.map((incident, index) => (
              <EventCard key={index} incident={incident} />
            ))}
          </div>
        ) : (
          <div className="flex items-center justify-center h-full text-gray-500">
            <p>No incidents detected yet.</p>
          </div>
        )}
      </div>
    </div>
  );
};
