import React, { Component } from 'react';
import { gsap } from 'gsap';
import useAnimations from './hooks/useAnimations';

class App extends Component {
  state = {
    animations: [],
  };

  componentDidMount() {
    this.fetchAnimations();
  }

  fetchAnimations = async () => {
    try {
      const response = await fetch('/api/animations');
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const data = await response.json();
      this.setState({ animations: data.animations }, this.animate);
    } catch (error) {
      console.error('Error fetching animations:', error);
    }
  };

  animate = () => {
    const { animations } = this.state;
    animations.forEach(animation => {
      gsap.to(`.animation-${animation.id}`, {
        x: animation.properties.x,
        y: animation.properties.y,
        opacity: animation.properties.opacity,
        duration: animation.duration,
      });
    });
  };

  render() {
    const { animations } = this.state;
    return (
      <div>
        {animations.map(animation => (
          <div key={animation.id} className={`animation-${animation.id}`}> {/* ADDED: GSAP animation */}
            {animation.name}
          </div>
        ))}
      </div>
    );
  }
}

export default App;

/* ADDED: Responsive styles for animations */
@media (max-width: 768px) {
  .animation-{animation.id} {
    font-size: 14px;
  }
}
@media (min-width: 769px) {
  .animation-{animation.id} {
    font-size: 18px;
  }
}
