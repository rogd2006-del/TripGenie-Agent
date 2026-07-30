import React, { createContext, useState } from 'react';

export const TripContext = createContext(null);

export const TripProvider = ({ children }) => {
  const [currentTrip, setCurrentTrip] = useState(null);
  const [agentLogs, setAgentLogs] = useState([]);
  const [isPlanning, setIsPlanning] = useState(false);

  const addAgentLog = (log) => {
    setAgentLogs(prev => [...prev, log]);
  };

  const clearAgentLogs = () => {
    setAgentLogs([]);
  };

  return (
    <TripContext.Provider value={{
      currentTrip,
      setCurrentTrip,
      agentLogs,
      addAgentLog,
      clearAgentLogs,
      isPlanning,
      setIsPlanning
    }}>
      {children}
    </TripContext.Provider>
  );
};
