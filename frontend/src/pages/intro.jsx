export default function Intro({ onStart }) {
  return (
    <main className="relative flex min-h-screen w-full flex-col justify-between overflow-hidden bg-[#03060f] px-6 py-8 sm:py-10">
      {/* Looping background video */}
      <video
        autoPlay
        loop
        muted
        playsInline
        preload="auto"
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 h-full w-full object-cover object-center"
      >
        <source src="/video/solar_system_pixabay.mp4" type="video/mp4" />
      </video>

      {/* Edge-only gradient: keeps the zooming star clear in the center while protecting text readability */}
      <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-[#03060f]/80 via-transparent via-45% to-[#03060f]/95" />

      {/* Top Header */}
      <header className="relative z-10 flex flex-col items-center text-center">
        <p className="font-terminal mb-2 text-xs uppercase tracking-[0.35em] text-sky-400/90">
          TRANSMISSION PRIORITAIRE // AN 6026
        </p>
        <h1 className="font-display text-4xl font-black uppercase tracking-[0.22em] text-slate-100 drop-shadow-[0_0_25px_rgba(56,189,248,0.45)] sm:text-6xl">
          STAR CREATOR
        </h1>
      </header>

      {/* Open center viewport for the zooming star and planetary orbits */}
      <div className="min-h-[28vh] flex-1" aria-hidden="true" />

      {/* Bottom Dystopian HUD Panel */}
      <section className="relative z-10 mx-auto w-full max-w-4xl border border-sky-400/30 bg-[#040814]/75 px-6 py-6 shadow-[0_0_50px_rgba(0,0,0,0.85)] backdrop-blur-xs sm:px-8 sm:py-7">
        <span className="pointer-events-none absolute top-0 left-0 h-3 w-3 border-t-2 border-l-2 border-cyan-400" />
        <span className="pointer-events-none absolute top-0 right-0 h-3 w-3 border-t-2 border-r-2 border-cyan-400" />
        <span className="pointer-events-none absolute bottom-0 left-0 h-3 w-3 border-b-2 border-l-2 border-cyan-400" />
        <span className="pointer-events-none absolute bottom-0 right-0 h-3 w-3 border-b-2 border-r-2 border-cyan-400" />

        <div className="font-terminal mb-3 flex items-center justify-between border-b border-sky-400/20 pb-2 text-[11px] uppercase tracking-[0.25em] text-slate-400">
          <span>ARCHIVES IMPÉRIALES // ALERTE ENTROPIE</span>
          <span className="text-red-400/90">STATUT : CRITIQUE</span>
        </div>

        <p className="font-sci text-sm font-medium leading-relaxed tracking-wider text-slate-200 uppercase sm:text-base sm:leading-7">
          An 6026, notre empire intergalactique est un cimetière en sursis.
          Déchiré par sa propre expansion frénétique, l'Univers se disloque
          et succombe à l'entropie. Le froid glace le vide cosmique,
          avalant une à une nos étoiles. Sans leur chaleur, la vie est sur le
          point d'être purgée ; nos mondes se transforment en tombeaux
          de glace.Face à ce froid éternel, l’humanité a conçu l’arme de l’ultime désespoir: une forge titanique capable de créer de nouveaux soleils.
          TU ES UN  STAR CREATOR. Tu fais partie des élus honorés à porté le fardeau de la genèse. 
          à travers les galaxies, les civilisations dont les cieux s’obscurcissent hurlent ton nom. La survie de notre espèce ne tient plus qu’à tes calculs.
        </p>

        <div className="mt-6 flex justify-center sm:justify-end">
          <button
            type="button"
            onClick={onStart}
            className="font-display cursor-pointer border border-cyan-400 bg-cyan-400/15 px-7 py-3 text-xs font-bold uppercase tracking-[0.25em] text-cyan-300 shadow-[0_0_20px_rgba(34,211,238,0.2)] transition duration-200 hover:bg-cyan-400 hover:text-[#03060f] hover:shadow-[0_0_30px_rgba(34,211,238,0.6)] active:scale-95 sm:text-sm"
          >
            [ Accepter la mission ]
          </button>
        </div>
      </section>
    </main>
  )
}