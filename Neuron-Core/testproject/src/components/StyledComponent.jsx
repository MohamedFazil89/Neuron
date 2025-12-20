import React, { useEffect, useState } from 'react';

const StyledComponent = () => {
  const [styles, setStyles] = useState({});

  useEffect(() => {
    const fetchStyles = async () => {
      try {
        const response = await fetch('/api/styles');
        if (!response.ok) {
          throw new Error('Styles not found');
        }
        const data = await response.json();
        setStyles(data.styles);
      } catch (error) {
        console.error('Error fetching styles:', error);
      }
    };
    fetchStyles();
  }, []);

  return (
    <div style={styles.container}> {/* ADDED: responsive styles */}
      <h1 style={styles.title}>Styled Component</h1> {/* ADDED: responsive styles */}
      <p style={styles.description}>This component is styled dynamically.</p> {/* ADDED: responsive styles */}
    </div>
  );
};

export default StyledComponent;