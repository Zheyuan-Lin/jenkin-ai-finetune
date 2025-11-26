'use client';

import { useState } from 'react';

interface Project {
  title: string;
  description: string;
  technologies: string[];
  githubLink: string;
  liveLink: string;
  image: string;
}

const projects: Project[] = [
  {
    title: "Personal Portfolio",
    description: "A responsive personal portfolio website built with Next.js and TypeScript",
    technologies: ["Next.js", "TypeScript", "CSS"],
    githubLink: "https://github.com/yourusername/portfolio",
    liveLink: "https://your-portfolio.com",
    image: "/portfolio.jpg"
  },
  {
    title: "E-commerce Platform",
    description: "Full-stack e-commerce platform with user authentication and payment integration",
    technologies: ["React", "Node.js", "MongoDB", "Stripe"],
    githubLink: "https://github.com/yourusername/ecommerce",
    liveLink: "https://your-ecommerce.com",
    image: "/ecommerce.jpg"
  },
  {
    title: "ML Image Classifier",
    description: "Machine learning model for image classification using TensorFlow",
    technologies: ["Python", "TensorFlow", "OpenCV"],
    githubLink: "https://github.com/yourusername/ml-classifier",
    liveLink: "https://your-ml-app.com",
    image: "/ml-project.jpg"
  }
];

const Projects = () => {
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleProjectClick = (project: Project) => {
    setSelectedProject(project);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setSelectedProject(null);
  };

  return (
    <section id="projects">
      <h2 className="section-title">Projects</h2>
      <div className="project-container">
        {projects.map((project) => (
          <div
            key={project.title}
            className="project-card"
            onClick={() => handleProjectClick(project)}
          >
            <div className="project-img">
              <img src={project.image} alt={project.title} />
            </div>
            <div className="project-info">
              <h3>{project.title}</h3>
              <p>{project.description}</p>
              <div className="technologies">
                {project.technologies.map((tech) => (
                  <span key={tech} className="tech-tag">
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {isModalOpen && selectedProject && (
        <div className="project-modal" onClick={closeModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <span className="close-modal" onClick={closeModal}>&times;</span>
            <h2>{selectedProject.title}</h2>
            <p>{selectedProject.description}</p>
            <div className="technologies">
              {selectedProject.technologies.map((tech) => (
                <span key={tech} className="tech-tag">
                  {tech}
                </span>
              ))}
            </div>
            <div className="modal-buttons">
              <a
                href={selectedProject.githubLink}
                target="_blank"
                rel="noopener noreferrer"
                className="btn"
              >
                GitHub
              </a>
              <a
                href={selectedProject.liveLink}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-outline"
              >
                Live Demo
              </a>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};

export default Projects;