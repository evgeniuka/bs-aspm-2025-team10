import React, { useEffect, useState } from 'react';
import { Typography } from '@mui/material';

const formatTime = (seconds) => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${minutes}:${String(remainingSeconds).padStart(2, '0')}`;
};

const RestTimer = ({ initialSeconds = 0, running = false, onTick }) => {
  const [remaining, setRemaining] = useState(initialSeconds);

  useEffect(() => {
    setRemaining(initialSeconds);
  }, [initialSeconds]);

  useEffect(() => {
    if (!running || remaining <= 0) return undefined;
    const interval = setInterval(() => {
      setRemaining((prev) => Math.max(prev - 1, 0));
    }, 1000);
    return () => clearInterval(interval);
  }, [running, remaining]);

  useEffect(() => {
    if (onTick) {
      onTick(remaining);
    }
  }, [onTick, remaining]);

  return (
    <Typography variant="h5" fontWeight="bold" color="warning.main" align="center">
      ⏱ REST: {formatTime(remaining)}
    </Typography>
  );
};

export default RestTimer;
