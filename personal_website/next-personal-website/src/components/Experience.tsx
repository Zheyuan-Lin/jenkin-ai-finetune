'use client';

import { useEffect, useRef } from 'react';

interface Experience {
  date: string;
  title: string;
  company: string;
  description: string;
}

const experiences: Experience[] = [
  {
    date: "2023 - Present",
    title: "Software Engineer Intern",
    company: "Tech Company",
    description: "Working on full-stack development using React and Node.js"
  },
  {
    date: "2022 - 2023",
    title: "Research Assistant",
    company: "University Lab",
    description: "Conducted research in machine learning and computer vision"
  },
  {
    date: "2021 - 2022",
    title: "Web Developer",
    company: "Startup",
    description: "Developed and maintained client websites using modern web technologies"
  }
];

const Experience = () => {
  const timelineRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      { threshold: 0.5 }
    );

    const timelineItems = timelineRef.current?.querySelectorAll('.timeline-item');
    timelineItems?.forEach(item => observer.observe(item));

    return () => observer.disconnect();
  }, []);

  return (
    <section id="experience">
      <h2 className="section-title">Experience</h2>
      <div className="timeline" ref={timelineRef}>
        {experiences.map((exp, index) => (
          <div key={index} className="timeline-item">
            <div className="timeline-content">
              <div className="timeline-date">{exp.date}</div>
              <h3>{exp.title}</h3>
              <h4>{exp.company}</h4>
              <p>{exp.description}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default Experience; 