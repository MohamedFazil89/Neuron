import { useState } from 'react';

const useAuth = () => {
  const [user, setUser] = useState(null);

  const login = async (email, password) => {
    // Logic for logging in the user
  };

  const logout = () => {
    // Logic for logging out the user
  };

  return { user, login, logout };
};

export default useAuth;