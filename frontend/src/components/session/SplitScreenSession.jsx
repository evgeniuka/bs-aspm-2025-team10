import React, { useEffect, useMemo, useState } from 'react';
import { Box } from '@mui/material';
import ClientQuadrant from './ClientQuadrant';
import { socketService } from '../../services/socket';

const borderColors = ['#2196F3', '#4CAF50', '#FF9800', '#9C27B0']; // Blue, Green, Orange, Purple

const SplitScreenSession = ({
  sessionId,
  session,
  totalSlots = 4,
  onSelect,
  onRestTimeUpdate,
  onSessionUpdate
}) => {
  const [localSession, setLocalSession] = useState(session);

  useEffect(() => {
    setLocalSession(session);
  }, [session]);

  useEffect(() => {
    if (!sessionId) return undefined;

    socketService.connect();
    socketService.joinSession(sessionId);

    socketService.onSessionUpdate((data) => {
      setLocalSession((prevSession) => {
        if (!prevSession) return prevSession;
        const nextSession = {
          ...prevSession,
          clients: prevSession.clients.map((client) =>
            client.id === data.client_id
              ? { ...client, ...data.updated_data }
              : client
          )
        };
        onSessionUpdate?.(nextSession);
        return nextSession;
      });
    });

    return () => {
      socketService.offSessionUpdate();
      socketService.leaveSession(sessionId);
      socketService.disconnect();
    };
  }, [onSessionUpdate, sessionId]);

  const clients = useMemo(
    () => localSession?.clients?.slice(0, totalSlots) || [],
    [localSession, totalSlots]
  );

  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
        gridTemplateRows: { xs: 'auto auto', sm: '1fr 1fr' },
        gap: 1,
        height: '100%'
      }}
    >
      {Array.from({ length: totalSlots }).map((_, idx) => {
        const client = clients[idx];
        return client ? (
          <ClientQuadrant
            key={client.id}
            client={client}
            borderColor={borderColors[idx]}
            onSelect={onSelect}
            onRestTimeUpdate={onRestTimeUpdate}
          />
        ) : (
          <Box
            key={`empty-${idx}`}
            sx={{
              border: '2px dashed #ccc',
              borderRadius: 2,
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              fontSize: '1.2rem',
              color: '#999',
              bgcolor: '#fff'
            }}
          >
            No client assigned
          </Box>
        );
      })}
    </Box>
  );
};

export default SplitScreenSession;
