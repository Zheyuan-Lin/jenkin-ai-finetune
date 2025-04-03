'use client';

import { useState, useEffect, useRef } from 'react';

interface Skill {
  name: string;
  level: number;
  description: string;
}

const skills: Skill[] = [
  {
    name: "Full Stack Development",
    level: 90,
    description: "Experience with React, Node.js, and various databases"
  },
  {
    name: "Machine Learning",
    level: 85,
    description: "Knowledge of ML algorithms and frameworks like TensorFlow"
  },
  {
    name: "Data Structures & Algorithms",
    level: 95,
    description: "Strong foundation in problem-solving and optimization"
  },
  {
    name: "UI/UX Design",
    level: 80,
    description: "Creating responsive and user-friendly interfaces"
  }
];

const Skills = () => {
  const [expandedSkill, setExpandedSkill] = useState<number | null>(null);
  const skillsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const progressBars = entry.target.querySelectorAll('.skill-progress');
            progressBars.forEach(bar => {
              const width = bar.getAttribute('data-level');
              if (width) {
                (bar as HTMLElement).style.width = `${width}%`;
              }
            });
          }
        });
      },
      { threshold: 0.5 }
    );

    if (skillsRef.current) {
      observer.observe(skillsRef.current);
    }

    return () => observer.disconnect();
  }, []);

  return (
    <section id="skills">
      <h2 className="section-title">Skills</h2>
      <div className="skills-container" ref={skillsRef}>
        {skills.map((skill, index) => (
          <div
            key={skill.name}
            className={`skill-card ${expandedSkill === index ? 'expanded' : ''}`}
            onClick={() => setExpandedSkill(expandedSkill === index ? null : index)}
          >
            <h3>{skill.name}</h3>
            <div className="skill-level">
              <div
                className="skill-progress"
                data-level={skill.level}
                style={{ width: '0%' }}
              ></div>
            </div>
            <p>{skill.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
};

export default Skills; 