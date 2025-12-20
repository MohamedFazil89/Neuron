import React, { useEffect, useState } from 'react';
import { gsap } from 'gsap';
import useAnimations from '../hooks/useAnimations';
import './ScrollingAnimation.css';

const ScrollingAnimation = () => {
  const [animations, setAnimations] = useState([]);

  // Fetch animation data from the API
  useEffect(() => {
    const fetchAnimations = async () => {
      const response = await fetch('/api/animations');
      const data = await response.json();
      setAnimations(data.animations);
    };
    fetchAnimations();
  }, []);

  // Trigger animations on scroll
  useEffect(() => {
    const handleScroll = () => {
      animations.forEach(animation => {
        const element = document.getElementById(animation.id);
        if (element) {
          gsap.to(element, {
            x: animation.properties.translateX,
            y: animation.properties.translateY,
            opacity: animation.properties.opacity,
            duration: animation.duration,
            scrollTrigger: {
              trigger: element,
              start: 'top bottom',
              end: 'top center',
              scrub: true,
            },
          });
        }
      });
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [animations]);

  return (
    <div className='scrolling-animation'>
      {animations.map(animation => (
        <div key={animation.id} id={animation.id} className='animation-item'>
          <h2>{animation.name}</h2>
        </div>
      ))}
    </div>
  );
};

export default ScrollingAnimation;
