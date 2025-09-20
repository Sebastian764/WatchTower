
import React from 'react';
import { CameraIcon } from './icons';

interface VideoPlayerProps {
  videoUrl: string | null;
}

export const VideoPlayer: React.FC<VideoPlayerProps> = ({ videoUrl }) => {
  return (
    <div className="aspect-video w-full bg-black rounded-lg overflow-hidden flex items-center justify-center">
      {videoUrl ? (
        <video src={videoUrl} controls className="w-full h-full object-contain" />
      ) : (
        <div className="text-center text-gray-500">
          <CameraIcon className="h-16 w-16 mx-auto mb-2" />
          <p>Upload a video to see the preview here</p>
        </div>
      )}
    </div>
  );
};
