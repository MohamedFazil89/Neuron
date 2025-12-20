import { useEffect, useState } from 'react';

const useAnimations = () => {
  const [animations, setAnimations] = useState([]);

  useEffect(() => {
    const fetchAnimations = async () => {
      const response = await fetch('/api/animations');
      const data = await response.json();
      setAnimations(data.animations);
    };
    fetchAnimations();
  }, []);

  return animations;
};

export default useAnimations;
