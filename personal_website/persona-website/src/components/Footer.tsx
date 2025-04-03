'use client';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer>
      <ul className="social-links">
        <li>
          <a
            href="https://github.com/yourusername"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
        </li>
        <li>
          <a
            href="https://linkedin.com/in/yourusername"
            target="_blank"
            rel="noopener noreferrer"
          >
            LinkedIn
          </a>
        </li>
        <li>
          <a
            href="https://twitter.com/yourusername"
            target="_blank"
            rel="noopener noreferrer"
          >
            Twitter
          </a>
        </li>
      </ul>
      <p>&copy; {currentYear} Zheyuan Lin. All rights reserved.</p>
    </footer>
  );
};

export default Footer;