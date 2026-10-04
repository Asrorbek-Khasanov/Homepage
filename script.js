(() => {
  'use strict';

  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const lerp = (a, b, t) => a + (b - a) * t;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = matchMedia('(hover: hover) and (pointer: fine)').matches;
  const body = document.body;

  /* ---------------- Split hero title into letters ---------------- */
  $$('.split').forEach((el) => {
    const text = el.textContent;
    el.textContent = '';
    el.setAttribute('aria-label', text);
    [...text].forEach((ch, i) => {
      const s = document.createElement('span');
      s.className = 'char';
      s.style.setProperty('--ci', i);
      s.setAttribute('aria-hidden', 'true');
      s.textContent = ch;
      el.appendChild(s);
    });
  });

  /* ---------------- Preloader ---------------- */
  const countEl = $('#loadCount');
  const barEl = $('#loadBar');
  let progress = 0;
  const finish = () => {
    body.classList.remove('is-loading');
    setTimeout(() => body.classList.add('is-ready'), reduced ? 0 : 350);
  };
  if (reduced) {
    finish();
  } else {
    const tick = () => {
      progress = Math.min(100, progress + Math.random() * 9 + 2);
      countEl.textContent = Math.floor(progress);
      barEl.style.width = progress + '%';
      if (progress < 100) setTimeout(tick, 40 + Math.random() * 60);
      else setTimeout(finish, 250);
    };
    tick();
  }

  /* ---------------- Clock (Tashkent) ---------------- */
  const clock = $('#clock');
  const fmt = new Intl.DateTimeFormat('en-GB', {
    hour: '2-digit', minute: '2-digit', second: '2-digit', timeZone: 'Asia/Tashkent',
  });
  const updateClock = () => { clock.textContent = fmt.format(new Date()); };
  updateClock();
  setInterval(updateClock, 1000);

  /* ---------------- Theme toggle ---------------- */
  $('#themeToggle').addEventListener('click', () => {
    const root = document.documentElement;
    const next = root.dataset.theme === 'light' ? 'dark' : 'light';
    root.dataset.theme = next;
    try { localStorage.setItem('theme', next); } catch (e) { /* ignore */ }
  });

  /* ---------------- Custom cursor ---------------- */
  const mouse = { x: innerWidth / 2, y: innerHeight / 2 };
  const cur = { x: mouse.x, y: mouse.y };
  const cursor = $('.cursor');
  const cursorLabel = $('.cursor__label');

  addEventListener('pointermove', (e) => { mouse.x = e.clientX; mouse.y = e.clientY; }, { passive: true });

  if (finePointer) {
    $$('a, button').forEach((el) => {
      el.addEventListener('mouseenter', () => cursor.classList.add('is-hover'));
      el.addEventListener('mouseleave', () => cursor.classList.remove('is-hover'));
    });
    $$('[data-cursor]').forEach((el) => {
      el.addEventListener('mouseenter', () => {
        cursorLabel.textContent = el.dataset.cursor;
        cursor.classList.add('has-label');
      });
      el.addEventListener('mouseleave', () => cursor.classList.remove('has-label'));
    });
  }

  /* ---------------- Magnetic elements ---------------- */
  if (finePointer && !reduced) {
    $$('[data-magnetic]').forEach((el) => {
      const strength = el.classList.contains('contact__btn') ? 0.4 : 0.25;
      el.addEventListener('mousemove', (e) => {
        const r = el.getBoundingClientRect();
        const dx = e.clientX - (r.left + r.width / 2);
        const dy = e.clientY - (r.top + r.height / 2);
        el.style.transform = `translate(${dx * strength}px, ${dy * strength}px)`;
        const inner = el.firstElementChild;
        if (inner) inner.style.transform = `translate(${dx * strength * 0.5}px, ${dy * strength * 0.5}px)`;
      });
      el.addEventListener('mouseleave', () => {
        el.style.transform = '';
        const inner = el.firstElementChild;
        if (inner) inner.style.transform = '';
      });
    });
  }

  /* ---------------- Work preview follows cursor ---------------- */
  const preview = $('.work__preview');
  const previewInner = $('.work__preview-inner');
  const previewTitle = $('.work__preview-title');
  const prev = { x: mouse.x, y: mouse.y, rot: 0 };
  if (finePointer) {
    $$('.work__item').forEach((item) => {
      item.addEventListener('mouseenter', () => {
        const c1 = item.dataset.color, c2 = item.dataset.color2 || c1;
        previewInner.style.background = `linear-gradient(135deg, ${c1}, ${c2})`;
        previewTitle.textContent = $('.work__title', item).textContent;
        preview.classList.add('is-on');
      });
      item.addEventListener('mouseleave', () => preview.classList.remove('is-on'));
    });
  }

  /* ---------------- Interactive dot field (hero) ---------------- */
  const canvas = $('#field');
  const ctx = canvas.getContext('2d');
  let dots = [], cw = 0, ch = 0, dpr = 1, inkColor = '#fff', accentColor = '#d4ff3a';
  const readColors = () => {
    const cs = getComputedStyle(document.documentElement);
    inkColor = cs.getPropertyValue('--ink').trim();
    accentColor = cs.getPropertyValue('--accent').trim();
  };
  const buildField = () => {
    dpr = Math.min(devicePixelRatio || 1, 2);
    cw = canvas.offsetWidth; ch = canvas.offsetHeight;
    canvas.width = cw * dpr; canvas.height = ch * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const gap = cw < 600 ? 28 : 36;
    dots = [];
    for (let y = gap / 2; y < ch; y += gap) {
      for (let x = gap / 2; x < cw; x += gap) dots.push({ ox: x, oy: y, x, y });
    }
  };
  readColors();
  buildField();
  addEventListener('resize', buildField);
  new MutationObserver(readColors).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

  let heroVisible = true;
  new IntersectionObserver(([e]) => { heroVisible = e.isIntersecting; }).observe(canvas);

  const drawField = (t) => {
    ctx.clearRect(0, 0, cw, ch);
    const rect = canvas.getBoundingClientRect();
    const mx = mouse.x - rect.left, my = mouse.y - rect.top;
    const R = 160;
    for (const d of dots) {
      const dx = d.ox - mx, dy = d.oy - my;
      const dist = Math.hypot(dx, dy);
      let tx = d.ox, ty = d.oy, size = 1.1, near = 0;
      if (dist < R && !reduced) {
        near = 1 - dist / R;
        const push = near * near * 40;
        tx += (dx / (dist || 1)) * push;
        ty += (dy / (dist || 1)) * push;
        size = 1.1 + near * 2.4;
      }
      if (!reduced) ty += Math.sin(t * 0.0012 + d.ox * 0.02) * 1.5;
      d.x = lerp(d.x, tx, 0.15);
      d.y = lerp(d.y, ty, 0.15);
      ctx.globalAlpha = near > 0 ? 0.35 + near * 0.65 : 0.18;
      ctx.fillStyle = near > 0.35 ? accentColor : inkColor;
      ctx.beginPath();
      ctx.arc(d.x, d.y, size, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  };

  /* ---------------- Scroll-velocity marquee ---------------- */
  const marquee = $('#marquee');
  let mqX = 0, lastScroll = scrollY, velocity = 0;

  /* ---------------- Main loop ---------------- */
  const loop = (t) => {
    // cursor
    cur.x = lerp(cur.x, mouse.x, 0.2);
    cur.y = lerp(cur.y, mouse.y, 0.2);
    cursor.style.transform = `translate3d(${cur.x}px, ${cur.y}px, 0) translate(-50%, -50%)`;

    // preview (slower, with tilt based on horizontal velocity)
    const vx = mouse.x - prev.x;
    prev.x = lerp(prev.x, mouse.x, 0.12);
    prev.y = lerp(prev.y, mouse.y, 0.12);
    prev.rot = lerp(prev.rot, Math.max(-15, Math.min(15, vx * 0.15)), 0.1);
    preview.style.left = prev.x + 'px';
    preview.style.top = prev.y + 'px';
    preview.style.rotate = prev.rot + 'deg';

    // marquee
    const sy = scrollY;
    velocity = lerp(velocity, sy - lastScroll, 0.1);
    lastScroll = sy;
    if (!reduced) {
      mqX -= 1 + Math.abs(velocity) * 0.6;
      const half = marquee.scrollWidth / 2;
      if (half && -mqX >= half) mqX += half;
      marquee.style.transform = `translate3d(${mqX}px,0,0) skewX(${Math.max(-12, Math.min(12, -velocity * 0.4))}deg)`;
    }

    if (heroVisible) drawField(t);
    requestAnimationFrame(loop);
  };
  requestAnimationFrame(loop);

  /* ---------------- Reveal on scroll ---------------- */
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add('in');
      io.unobserve(e.target);
    });
  }, { threshold: 0.15, rootMargin: '0px 0px -8% 0px' });
  $$('.reveal, .contact__title').forEach((el) => io.observe(el));

  /* ---------------- Counters ---------------- */
  const countIO = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      const el = e.target, end = +el.dataset.count;
      const dur = reduced ? 0 : 1600, start = performance.now();
      const step = (now) => {
        const p = dur ? Math.min(1, (now - start) / dur) : 1;
        el.textContent = Math.round(end * (1 - Math.pow(1 - p, 4)));
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
      countIO.unobserve(el);
    });
  }, { threshold: 0.6 });
  $$('[data-count]').forEach((el) => countIO.observe(el));

  /* ---------------- Word-by-word scroll scrub ---------------- */
  $$('[data-scrub]').forEach((el) => {
    const words = el.textContent.trim().split(/\s+/);
    el.textContent = '';
    const spans = words.map((w, i) => {
      const s = document.createElement('span');
      s.className = 'w';
      s.textContent = w;
      el.appendChild(s);
      if (i < words.length - 1) el.appendChild(document.createTextNode(' '));
      return s;
    });
    const update = () => {
      const r = el.getBoundingClientRect();
      const p = (innerHeight * 0.85 - r.top) / (r.height + innerHeight * 0.35);
      const n = Math.floor(Math.max(0, Math.min(1, p)) * spans.length);
      spans.forEach((s, i) => s.classList.toggle('on', i < n));
    };
    addEventListener('scroll', update, { passive: true });
    update();
  });

  /* ---------------- Stacking cards scale down as next card arrives ---------------- */
  const cards = $$('.card');
  if (!reduced) {
    const updateCards = () => {
      cards.forEach((card, i) => {
        const next = cards[i + 1];
        if (!next) return;
        const r = next.getBoundingClientRect();
        const p = Math.max(0, Math.min(1, 1 - (r.top - 100) / innerHeight));
        card.style.transform = `scale(${1 - p * 0.06})`;
        card.style.filter = `brightness(${1 - p * 0.35})`;
      });
    };
    addEventListener('scroll', updateCards, { passive: true });
    updateCards();
  }
})();
