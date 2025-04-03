'use client';

import { useState, useEffect } from 'react';

const Hero = () => {
  const [text, setText] = useState('');
  const fullText = "I'm Zheyuan Lin, a Computer Science Student";
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < fullText.length) {
      const timeout = setTimeout(() => {
        setText(prev => prev + fullText[currentIndex]);
        setCurrentIndex(prev => prev + 1);
      }, 100);

      return () => clearTimeout(timeout);
    }
  }, [currentIndex]);

  return (
    <section id="hero">
      <div className="hero-content">
        <h1>
          {text}
          <span className="cursor"></span>
        </h1>
        <p>Passionate about creating innovative solutions through code</p>
      </div>
    </section>
  );
};

export default Hero; 