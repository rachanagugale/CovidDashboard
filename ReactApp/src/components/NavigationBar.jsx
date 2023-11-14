import "./NavigationBar.css";

export default function NavigationBar({ routes }) {
  return (
    <nav>
      <a href="/">
        <span className="material-symbols-outlined">token</span>
      </a>

      <div className="links">
        {routes
          .filter(({ path }) => path != "/")
          .map(({ label, path }) => (
            <a key={label} href={path}>
              {label}
            </a>
          ))}
      </div>
    </nav>
  );
}
