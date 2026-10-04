(() => {
  'use strict';

  const $ = (s, c = document) => c.querySelector(s);
  const $$ = (s, c = document) => [...c.querySelectorAll(s)];
  const lerp = (a, b, t) => a + (b - a) * t;
  const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
  const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = matchMedia('(hover: hover) and (pointer: fine)').matches;
  const root = document.documentElement;
  const body = document.body;
  const store = {
    get: (k) => { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: (k, v) => { try { localStorage.setItem(k, v); } catch (e) { /* ignore */ } },
  };

  /* =======================================================
     Text helpers: split letters (hero) and words (scrub)
     ======================================================= */
  const splitChars = (el, animate) => {
    const text = el.textContent;
    el.textContent = '';
    el.setAttribute('aria-label', text);
    [...text].forEach((ch, i) => {
      const s = document.createElement('span');
      s.className = animate ? 'char char--pre' : 'char';
      s.style.setProperty('--ci', i);
      s.setAttribute('aria-hidden', 'true');
      s.textContent = ch;
      el.appendChild(s);
    });
    if (animate) {
      requestAnimationFrame(() => requestAnimationFrame(() => {
        $$('.char--pre', el).forEach((c) => c.classList.remove('char--pre'));
      }));
    }
  };

  const splitWords = (el) => {
    const words = el.textContent.trim().split(/\s+/);
    el.textContent = '';
    el._words = words.map((w, i) => {
      const s = document.createElement('span');
      s.className = 'w';
      s.textContent = w;
      el.appendChild(s);
      if (i < words.length - 1) el.appendChild(document.createTextNode(' '));
      return s;
    });
  };

  /* =======================================================
     i18n
     ======================================================= */
  const LANGS = ['uz', 'en', 'ru'];
  const detectLang = () => {
    const q = new URLSearchParams(location.search).get('lang');
    if (LANGS.includes(q)) return q;
    const saved = store.get('lang');
    if (LANGS.includes(saved)) return saved;
    const nav = (navigator.language || 'uz').slice(0, 2).toLowerCase();
    return LANGS.includes(nav) ? nav : 'uz';
  };
  let lang = detectLang();

  const applyLang = (l, animate) => {
    const dict = window.I18N[l];
    if (!dict) return;
    lang = l;
    root.lang = l;
    document.title = dict['meta.title'];
    const desc = $('meta[name="description"]');
    if (desc) desc.setAttribute('content', dict['meta.desc']);

    $$('[data-i18n]').forEach((el) => {
      const v = dict[el.dataset.i18n];
      if (v == null) return;
      el.textContent = v;
      if (el.classList.contains('split')) splitChars(el, animate);
      if (el.hasAttribute('data-scrub')) splitWords(el);
    });
    $$('[data-i18n-cursor]').forEach((el) => { el.dataset.cursor = dict[el.dataset.i18nCursor] || ''; });
    $$('.roll').forEach((el) => {
      const inner = el.querySelector(':scope > span');
      if (inner) el.dataset.text = inner.textContent;
    });
    $$('.lang__btn').forEach((b) => {
      const on = b.dataset.lang === l;
      b.classList.toggle('is-active', on);
      b.setAttribute('aria-pressed', on);
    });
    scrubAll();
  };

  $$('.lang__btn').forEach((btn) => {
    btn.addEventListener('click', () => {
      const l = btn.dataset.lang;
      if (l === lang) return;
      store.set('lang', l);
      const url = new URL(location.href);
      url.searchParams.set('lang', l);
      history.replaceState(null, '', url);
      if (reduced) { applyLang(l, false); return; }
      body.classList.add('is-switching');
      setTimeout(() => {
        applyLang(l, true);
        body.classList.remove('is-switching');
      }, 250);
    });
  });

  /* Word-by-word scroll scrub */
  const scrubAll = () => {
    $$('[data-scrub]').forEach((el) => {
      const spans = el._words || [];
      const r = el.getBoundingClientRect();
      const p = (innerHeight * 0.85 - r.top) / (r.height + innerHeight * 0.35);
      const n = Math.floor(clamp(p, 0, 1) * spans.length);
      spans.forEach((s, i) => s.classList.toggle('on', i < n));
    });
  };
  addEventListener('scroll', scrubAll, { passive: true });

  applyLang(lang, false);

  /* =======================================================
     Preloader
     ======================================================= */
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

  /* =======================================================
     Clock (Uzbekistan time)
     ======================================================= */
  const clock = $('#clock');
  const fmt = new Intl.DateTimeFormat('en-GB', {
    hour: '2-digit', minute: '2-digit', second: '2-digit', timeZone: 'Asia/Tashkent',
  });
  const updateClock = () => { clock.textContent = fmt.format(new Date()); };
  updateClock();
  setInterval(updateClock, 1000);

  /* =======================================================
     Theme toggle
     ======================================================= */
  $('#themeToggle').addEventListener('click', () => {
    const next = root.dataset.theme === 'light' ? 'dark' : 'light';
    root.dataset.theme = next;
    store.set('theme', next);
  });

  /* =======================================================
     Cursor
     ======================================================= */
  const mouse = { x: innerWidth / 2, y: innerHeight / 2, last: 0 };
  const cur = { x: mouse.x, y: mouse.y };
  const cursor = $('.cursor');
  const cursorLabel = $('.cursor__label');

  addEventListener('pointermove', (e) => {
    mouse.x = e.clientX; mouse.y = e.clientY; mouse.last = performance.now();
  }, { passive: true });

  if (finePointer) {
    $$('a, button').forEach((el) => {
      el.addEventListener('mouseenter', () => cursor.classList.add('is-hover'));
      el.addEventListener('mouseleave', () => cursor.classList.remove('is-hover'));
    });
    $$('[data-cursor], [data-i18n-cursor]').forEach((el) => {
      el.addEventListener('mouseenter', () => {
        if (!el.dataset.cursor) return;
        cursorLabel.textContent = el.dataset.cursor;
        cursor.classList.add('has-label');
      });
      el.addEventListener('mouseleave', () => cursor.classList.remove('has-label'));
    });
  }

  /* Magnetic elements */
  if (finePointer && !reduced) {
    $$('[data-magnetic]').forEach((el) => {
      const strength = el.classList.contains('contact__btn') ? 0.4 : 0.25;
      const inner = el.firstElementChild;
      el.addEventListener('mousemove', (e) => {
        const r = el.getBoundingClientRect();
        const dx = e.clientX - (r.left + r.width / 2);
        const dy = e.clientY - (r.top + r.height / 2);
        el.style.transform = `translate(${dx * strength}px, ${dy * strength}px)`;
        if (inner) inner.style.transform = `translate(${dx * strength * 0.5}px, ${dy * strength * 0.5}px)`;
      });
      el.addEventListener('mouseleave', () => {
        el.style.transform = '';
        if (inner) inner.style.transform = '';
      });
    });
  }

  /* =======================================================
     Publication material tags (coloured on hover)
     ======================================================= */
  $$('.pub').forEach((item) => {
    const tag = document.createElement('span');
    tag.className = 'pub__tag';
    tag.textContent = item.dataset.tag;
    tag.style.setProperty('--c1', item.dataset.color);
    tag.style.setProperty('--c2', item.dataset.color2 || item.dataset.color);
    item.insertBefore(tag, $('.pub__year', item));
  });

  /* Floating material card: follows the cursor horizontally but sits
     above the hovered row (or below it near the top), never over its title */
  const preview = $('.pub-preview');
  const previewInner = $('.pub-preview__inner');
  const previewTag = $('.pub-preview__tag');
  const prev = { x: mouse.x, y: mouse.y, rot: 0, row: null };
  if (finePointer) {
    $$('.pub').forEach((item) => {
      item.addEventListener('mouseenter', () => {
        const c1 = item.dataset.color, c2 = item.dataset.color2 || c1;
        previewInner.style.background = `linear-gradient(135deg, ${c1}, ${c2})`;
        previewTag.textContent = item.dataset.tag;
        if (!prev.row) { prev.x = mouse.x; prev.y = item.getBoundingClientRect().top; }
        prev.row = item;
        preview.classList.add('is-on');
      });
      item.addEventListener('mouseleave', () => {
        prev.row = null;
        preview.classList.remove('is-on');
      });
    });
  }
  const placePreview = () => {
    if (!prev.row) return;
    const r = prev.row.getBoundingClientRect();
    const w = preview.offsetWidth, h = preview.offsetHeight;
    const gap = 14;
    let ty = r.top - gap - h / 2;
    if (r.top - gap - h < 80) ty = r.bottom + gap + h / 2;
    const tx = clamp(mouse.x, w / 2 + 16, innerWidth - w / 2 - 16);
    const vx = tx - prev.x;
    prev.x = lerp(prev.x, tx, 0.14);
    prev.y = lerp(prev.y, ty, 0.2);
    prev.rot = lerp(prev.rot, clamp(vx * 0.08, -8, 8), 0.12);
    preview.style.left = prev.x + 'px';
    preview.style.top = prev.y + 'px';
    preview.style.rotate = prev.rot + 'deg';
  };

  /* =======================================================
     Hero: crystal lattice that bonds around the cursor
     ======================================================= */
  const canvas = $('#field');
  const ctx = canvas.getContext('2d');
  let dots = [], cols = 0, cw = 0, ch = 0, inkColor = '#fff', accentColor = '#d4ff3a';
  const readColors = () => {
    const cs = getComputedStyle(root);
    inkColor = cs.getPropertyValue('--ink').trim();
    accentColor = cs.getPropertyValue('--accent').trim();
  };
  const buildField = () => {
    const dpr = Math.min(devicePixelRatio || 1, 2);
    cw = canvas.offsetWidth; ch = canvas.offsetHeight;
    canvas.width = cw * dpr; canvas.height = ch * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const gap = cw < 600 ? 28 : 34;
    dots = [];
    cols = Math.ceil(cw / gap);
    for (let y = gap / 2; y < ch; y += gap) {
      for (let c = 0; c < cols; c++) {
        const x = gap / 2 + c * gap;
        dots.push({ ox: x, oy: y, x, y, near: 0 });
      }
    }
  };
  readColors();
  buildField();
  addEventListener('resize', buildField);
  new MutationObserver(readColors).observe(root, { attributes: true, attributeFilter: ['data-theme'] });

  let heroVisible = true;
  new IntersectionObserver(([e]) => { heroVisible = e.isIntersecting; }).observe(canvas);

  const drawField = (t) => {
    ctx.clearRect(0, 0, cw, ch);
    const rect = canvas.getBoundingClientRect();
    let mx = mouse.x - rect.left, my = mouse.y - rect.top;
    // No pointer for a while (or touch device): a virtual "electron" wanders
    if (!finePointer || t - mouse.last > 4000) {
      mx = cw * (0.5 + 0.32 * Math.sin(t * 0.00035));
      my = ch * (0.45 + 0.25 * Math.sin(t * 0.00052 + 1));
    }
    const R = Math.min(190, cw * 0.3);
    for (const d of dots) {
      const dx = d.ox - mx, dy = d.oy - my;
      const dist = Math.hypot(dx, dy);
      let tx = d.ox, ty = d.oy;
      d.near = 0;
      if (dist < R && !reduced) {
        d.near = 1 - dist / R;
        const push = d.near * d.near * 34;
        tx += (dx / (dist || 1)) * push;
        ty += (dy / (dist || 1)) * push;
      }
      if (!reduced) ty += Math.sin(t * 0.0012 + d.ox * 0.02) * 1.4;
      d.x = lerp(d.x, tx, 0.15);
      d.y = lerp(d.y, ty, 0.15);
    }
    // bonds
    ctx.strokeStyle = accentColor;
    ctx.lineWidth = 1;
    for (let i = 0; i < dots.length; i++) {
      const d = dots[i];
      if (d.near < 0.08) continue;
      const right = (i + 1) % cols !== 0 ? dots[i + 1] : null;
      const down = dots[i + cols];
      const diag = right && dots[i + cols + 1];
      ctx.globalAlpha = d.near * 0.55;
      ctx.beginPath();
      if (right && right.near > 0.08) { ctx.moveTo(d.x, d.y); ctx.lineTo(right.x, right.y); }
      if (down && down.near > 0.08) { ctx.moveTo(d.x, d.y); ctx.lineTo(down.x, down.y); }
      if (diag && diag.near > 0.3) { ctx.moveTo(d.x, d.y); ctx.lineTo(diag.x, diag.y); }
      ctx.stroke();
    }
    // atoms
    for (const d of dots) {
      ctx.globalAlpha = d.near > 0 ? 0.3 + d.near * 0.7 : 0.18;
      ctx.fillStyle = d.near > 0.3 ? accentColor : inkColor;
      ctx.beginPath();
      ctx.arc(d.x, d.y, 1.1 + d.near * 2.6, 0, Math.PI * 2);
      ctx.fill();
    }
    ctx.globalAlpha = 1;
  };

  /* =======================================================
     Research lab: memristor pinched hysteresis + filament
     ======================================================= */
  const lab = (() => {
    const N = 480;
    const Ron = 1, Roff = 14, mu = 2.2;
    const pts = [];
    let x = 0.08;
    // integrate a few periods so we sample a steady-state loop
    for (let p = 0; p < 4; p++) {
      for (let i = 0; i < N; i++) {
        const V = Math.sin((i / N) * Math.PI * 2);
        x += mu * V * (x * (1 - x) + 0.004) * ((Math.PI * 2) / N);
        x = clamp(x, 0.02, 0.98);
        if (p === 3) pts.push({ V, I: V / (Roff - (Roff - Ron) * x), x });
      }
    }
    const Imax = Math.max(...pts.map((p) => Math.abs(p.I)));
    const xs = pts.map((p) => p.x);
    const xMin = Math.min(...xs), xMax = Math.max(...xs);
    pts.forEach((p) => {
      p.px = 200 + p.V * 165;
      p.py = 130 - (p.I / Imax) * 112;
      p.k = (p.x - xMin) / (xMax - xMin || 1); // normalised filament length
    });
    const toPath = (arr) => arr.map((p, i) => (i ? 'L' : 'M') + p.px.toFixed(1) + ' ' + p.py.toFixed(1)).join('');
    $('#ivGhost').setAttribute('d', toPath(pts) + 'Z');

    // Two filament species: oxygen vacancies (VCM) and metal ions (ECM)
    const NS = 'http://www.w3.org/2000/svg';
    const g = $('#vacancies');
    const SLOTS = 9;
    const COLS = [{ x: 240, cls: 'vac', r: 4.2 }, { x: 160, cls: 'ion', r: 4.6 }];
    const filaments = COLS.map(({ x, cls, r }) => {
      const arr = [];
      for (let i = 0; i < SLOTS; i++) {
        const c = document.createElementNS(NS, 'circle');
        c.setAttribute('cx', x + (i % 2 ? 4 : -4));
        c.setAttribute('cy', 113 - i * 9.6);
        c.setAttribute('r', r);
        c.setAttribute('class', cls);
        g.appendChild(c);
        arr.push(c);
      }
      return arr;
    });
    let seed = 7;
    const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);
    for (let i = 0; i < 34; i++) {
      const c = document.createElementNS(NS, 'circle');
      let cx, cy, tries = 0;
      do {
        cx = 72 + rnd() * 256;
        cy = 38 + rnd() * 76;
        tries++;
      } while (tries < 20 && (COLS.some((col) => Math.abs(cx - col.x) < 18) || (cx < 130 && cy < 56)));
      const ion = i % 5 < 2;
      c.setAttribute('cx', cx.toFixed(1));
      c.setAttribute('cy', cy.toFixed(1));
      c.setAttribute('r', ion ? 3 : 2.6);
      c.setAttribute('class', ion ? 'ion' : 'vac');
      c.style.opacity = 0.3;
      g.appendChild(c);
    }

    const path = $('#ivPath'), dot = $('#ivDot'), vEl = $('#labV'), stateEl = $('#labState');
    const TRAIL = Math.floor(N * 0.3);
    let visible = false;
    new IntersectionObserver(([e]) => { visible = e.isIntersecting; }).observe($('#lab'));

    const render = (t) => {
      const i = reduced ? Math.floor(N * 0.3) : Math.floor(((t / 5200) % 1) * N);
      const p = pts[i];
      const trail = [];
      for (let k = TRAIL; k >= 0; k--) trail.push(pts[(i - k + N) % N]);
      path.setAttribute('d', toPath(trail));
      dot.setAttribute('cx', p.px.toFixed(1));
      dot.setAttribute('cy', p.py.toFixed(1));
      vEl.textContent = (p.V >= 0 ? '+' : '−') + Math.abs(p.V).toFixed(2);
      const on = p.k > 0.5;
      stateEl.textContent = on ? 'LRS' : 'HRS';
      stateEl.classList.toggle('is-on', on);
      const n = p.k * SLOTS;
      filaments.forEach((arr) => arr.forEach((c, j) => {
        c.style.opacity = clamp(n - j, 0.12, 1);
      }));
    };
    render(0);
    return { render: (t) => { if (visible) render(t); } };
  })();

  /* =======================================================
     Main loop
     ======================================================= */
  const marquee = $('#marquee');
  let mqX = 0, lastScroll = scrollY, velocity = 0;

  const loop = (t) => {
    cur.x = lerp(cur.x, mouse.x, 0.2);
    cur.y = lerp(cur.y, mouse.y, 0.2);
    cursor.style.transform = `translate3d(${cur.x}px, ${cur.y}px, 0) translate(-50%, -50%)`;
    placePreview();

    const sy = scrollY;
    velocity = lerp(velocity, sy - lastScroll, 0.1);
    lastScroll = sy;
    if (!reduced) {
      mqX -= 1 + Math.abs(velocity) * 0.6;
      const half = marquee.scrollWidth / 2;
      if (half && -mqX >= half) mqX += half;
      marquee.style.transform = `translate3d(${mqX}px,0,0) skewX(${clamp(-velocity * 0.4, -12, 12)}deg)`;
    }

    if (heroVisible) drawField(t);
    if (!reduced) lab.render(t);
    requestAnimationFrame(loop);
  };
  requestAnimationFrame(loop);

  /* =======================================================
     Reveal on scroll + counters
     ======================================================= */
  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      e.target.classList.add('in');
      io.unobserve(e.target);
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
  $$('.reveal, .contact__title').forEach((el) => io.observe(el));

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

  /* =======================================================
     Stacking cards shrink as the next one arrives
     ======================================================= */
  const cards = $$('.card');
  if (!reduced) {
    const updateCards = () => {
      cards.forEach((card, i) => {
        const next = cards[i + 1];
        if (!next) return;
        const r = next.getBoundingClientRect();
        const p = clamp(1 - (r.top - 100) / innerHeight, 0, 1);
        card.style.transform = `scale(${1 - p * 0.06})`;
        card.style.filter = `brightness(${1 - p * 0.35})`;
      });
    };
    addEventListener('scroll', updateCards, { passive: true });
    updateCards();
  }
})();
