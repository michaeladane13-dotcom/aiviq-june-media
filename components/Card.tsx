export default function Card({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <section className="rounded-2xl bg-card p-5 shadow-lg">
      <div className="mb-3 flex items-baseline justify-between gap-3">
        <h2 className="text-xs font-semibold uppercase tracking-wider text-ink/50">
          {title}
        </h2>
        {subtitle ? (
          <span className="font-mono text-[10px] text-ink/40">{subtitle}</span>
        ) : null}
      </div>
      {children}
    </section>
  );
}
