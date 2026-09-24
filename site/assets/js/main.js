/* =========================================================================
   TUZLA CONTA — etkileşim
   1) Açılış: T ve C kapanır, logo üst bardaki yerine uçar, perde kalkar.
   2) Hero: scroll videoyu kare kare sürer.
   3) Katalog sahnesi: scroll ilerledikçe kategori değişir, tıklama devralır.
   ========================================================================= */
(function () {
  "use strict";
  // her yenilemede sayfa en üstten, animasyonlar baştan başlasın —
  // tarayıcının scroll pozisyonunu hatırlamasına izin verme
  if ("scrollRestoration" in history) history.scrollRestoration = "manual";
  scrollTo(0, 0);

  var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  /* ------------------------------------------------------------- 1. AÇILIŞ */
  function intro() {
    var ld = $("#loader"), mark = $("#ldMark"), nav = $(".nav"), navLogo = $("#navLogo");
    if (!ld) { if (nav) nav.removeAttribute("data-boot"); return; }

    function finish() {
      ld.classList.add("is-gone");
      document.documentElement.classList.remove("is-locked");
    }
    if (reduce) { if (nav) nav.removeAttribute("data-boot"); finish(); return; }

    document.documentElement.classList.add("is-locked");
    var seen = false;
    try { seen = sessionStorage.getItem("tc-intro") === "1"; } catch (e) {}
    var hold = seen ? 420 : 1520;

    requestAnimationFrame(function () { ld.classList.add("run"); });

    setTimeout(function () {
      // FLIP: logoyu bulunduğu yerden üst bardaki yuvasına taşı
      var a = mark.getBoundingClientRect();
      var b = navLogo.getBoundingClientRect();
      var s = b.width / a.width;
      mark.style.transformOrigin = "0 0";
      mark.classList.add("fly");
      mark.style.transform = "translate(" + (b.left - a.left) + "px," + (b.top - a.top) + "px) scale(" + s + ")";
      ld.classList.add("lift");
      if (nav) nav.removeAttribute("data-boot");
      setTimeout(function () { ld.classList.add("up"); }, 420);
      setTimeout(finish, 1500);
      try { sessionStorage.setItem("tc-intro", "1"); } catch (e) {}
    }, hold);
  }

  /* ---------------------------------------------------------- 2. ÜST BAR */
  function nav() {
    var bar = $(".nav"), burger = $(".nav__burger"), menu = $(".nav__menu");
    if (bar) {
      var solid = function () { bar.classList.toggle("solid", scrollY > 24); };
      solid(); addEventListener("scroll", solid, { passive: true });
    }
    if (burger && menu) {
      burger.addEventListener("click", function () {
        var open = menu.classList.toggle("open");
        burger.setAttribute("aria-expanded", open ? "true" : "false");
      });
      menu.addEventListener("click", function (e) {
        if (e.target.closest("a")) {
          menu.classList.remove("open");
          burger.setAttribute("aria-expanded", "false");
        }
      });
    }
  }

  /* ------------------------------------------------------------- 3. HERO
     Scroll, videoyu değil bir KARE DİZİSİNİ sürer. Video ile currentTime
     kurcalamak sunucunun HTTP Range desteğine, codec'e ve tarayıcının
     seek/autoplay politikasına bağımlıydı; biri eksik olduğunda kare hiç
     değişmiyordu. Kare dizisi + canvas bunların hiçbirine bağlı değil:
     her kare sıradan bir görsel, çizim anlıktır. */
  function hero() {
    var sec = $("#hero"); if (!sec) return;
    var cv = $("#heroCanvas", sec), h = $("#heroH", sec), l2 = $("#heroL2", sec);
    var scrim = $(".hero__scrim", sec);
    var raf = 0, last = 0;
    var target = 0, cur = -1;   // scroll oranı ve ekranda gösterilen (yumuşatılmış) oran

    var ctx = null, imgs = [], N = 0, sized = false, drawn = -1;
    if (cv && cv.getContext && !reduce) {
      ctx = cv.getContext("2d", { alpha: false });
      // Dikey telefon: spiralin merkezine göre kırpılmış dikey kareler.
      // Yatay telefon/tablet/masaüstü: 16:9 kareler.
      var portrait = innerWidth < 900 && innerHeight > innerWidth;
      var light = portrait || (navigator.connection || {}).saveData;
      var pat = cv.getAttribute(light ? "data-seq-m" : "data-seq-d");
      N = parseInt(cv.getAttribute(light ? "data-n-m" : "data-n-d"), 10) || 0;

      var pad = function (n) { return n < 10 ? "00" + n : n < 100 ? "0" + n : "" + n; };
      var ok = function (im) { return im && im.complete && im.naturalWidth; };
      var load = function (i) {
        if (imgs[i]) return;
        var im = new Image();
        im.decoding = "async";
        im.src = pat.replace("%", pad(i + 1));
        imgs[i] = im;
        im.onload = function () { drawn = -1; kick(); };
      };

      // ilk kare hemen, kalanlar sırayla ve sessizce arkadan
      load(0);
      var queue = 1;
      var pump = function () {
        var budget = 6;
        while (queue < N && budget-- > 0) load(queue++);
        if (queue < N) setTimeout(pump, 90);
      };
      setTimeout(pump, 60);

      var fit = function () {
        var r = cv.getBoundingClientRect();
        var dpr = Math.min(devicePixelRatio || 1, 2);
        var w = Math.round(r.width * dpr), hh = Math.round(r.height * dpr);
        if (w !== cv.width || hh !== cv.height) { cv.width = w; cv.height = hh; sized = true; return true; }
        return false;
      };
      var nearest = function (i) {
        if (ok(imgs[i])) return i;
        for (var d = 1; d < N; d++) {
          if (i - d >= 0 && ok(imgs[i - d])) return i - d;
          if (i + d < N && ok(imgs[i + d])) return i + d;
        }
        return -1;
      };
      var blit = function (im, a) {
        var cw = cv.width, ch = cv.height;
        var s = Math.max(cw / im.naturalWidth, ch / im.naturalHeight);
        var dw = im.naturalWidth * s, dh = im.naturalHeight * s;
        ctx.globalAlpha = a;
        ctx.drawImage(im, (cw - dw) / 2, (ch - dh) / 2, dw, dh);
      };
      // Kare konumu kesirli: f = 12.4 -> 12. kare tam, 13. kare %40 üstüne.
      // Böylece kare sayısı ne olursa olsun, ekranın her yenilemesinde (120 Hz
      // ekranda saniyede 120 kez) ara bir görüntü çizilir; hareket basamaksız akar.
      var paint = function (f) {
        if (!sized) fit();
        var i = Math.floor(f), t = f - i;
        var key = Math.round(f * 64);
        if (key === drawn) return;
        var a = nearest(i); if (a < 0) return;
        blit(imgs[a], 1);
        if (a === i && t > 0.015 && i + 1 < N && ok(imgs[i + 1])) blit(imgs[i + 1], t);
        ctx.globalAlpha = 1;
        if (drawn < 0) cv.classList.add("on");
        drawn = key;
      };
      var refit = function () { if (fit()) { drawn = -1; kick(); } };
      addEventListener("resize", refit);
      addEventListener("orientationchange", refit);
      // Mobilde ilk boyama, açılış perdesi hâlâ üstteyken ve adres çubuğu
      // yüksekliği oturmadan yapılıyordu; kare doğru ölçülmeyip geriliyordu.
      // ResizeObserver kutunun gerçekten değiştiği her anı yakalar.
      if ("ResizeObserver" in window) new ResizeObserver(refit).observe(cv);
      fit();
    }

    function progress() {
      var r = sec.getBoundingClientRect();
      var span = sec.offsetHeight - innerHeight;
      if (span <= 0) return 0;
      return Math.min(1, Math.max(0, -r.top / span));
    }

    function apply(p) {
      if (ctx && N > 0) paint(p * (N - 1));
      if (h) {
        // metin bloğu görüntü anına yer bırakarak çekilir
        var out = Math.max(0, (p - 0.55) / 0.35);
        h.style.opacity = String(1 - out);
        h.style.transform = "translateY(" + (-out * 46) + "px)";
      }
      if (l2) {
        // ikinci satır birinciye kapanır — contanın kapanışıyla aynı hareket
        var close = Math.min(1, p / 0.45);
        l2.style.transform = "translateY(" + (1 - close) * 15 + "px)";
      }
      if (!reduce && scrim) {
        // metin çekilirken perde de açılır, kare saf haline döner
        scrim.style.opacity = String(1 - Math.min(1, Math.max(0, (p - 0.5) / 0.45)) * 0.55);
      }
    }

    // Scroll'un kendisi basamaklıdır (fare tekerleği 100px'lik sıçramalar yapar).
    // Gösterilen oran hedefe kare hızından bağımsız bir yayla yaklaşır: 60 Hz'de de
    // 120 Hz'de de aynı sürede oturur, ama 120 Hz'de iki kat ara adım çizilir.
    function tick(now) {
      raf = 0;
      var dt = last ? Math.min(64, now - last) : 16.7;
      last = now;
      if (cur < 0) cur = target;
      var k = 1 - Math.pow(1 - 0.16, dt / 16.7);
      cur += (target - cur) * k;
      if (Math.abs(target - cur) < 0.0004) cur = target;
      apply(cur);
      if (cur !== target) raf = requestAnimationFrame(tick);
      else last = 0;
    }
    function kick() { if (!raf) raf = requestAnimationFrame(tick); }
    function onScroll() { target = progress(); kick(); }
    addEventListener("scroll", onScroll, { passive: true });
    addEventListener("resize", onScroll);
    target = progress(); cur = target; apply(cur);
  }


  /* --------------------------------------------------- 4. KATALOG SAHNESİ */
  function stage() {
    var sec = $("#stage"); if (!sec) return;
    var items = $$(".stage__item", sec);
    var shots = $$(".stage__img", sec);
    if (!items.length) return;
    var locked = false, active = -1;

    function show(i) {
      if (i === active || i < 0 || i >= items.length) return;
      active = i;
      items.forEach(function (el, n) { el.classList.toggle("on", n === i); });
      shots.forEach(function (el, n) { el.classList.toggle("on", n === i); });
    }
    show(0);

    var canHover = matchMedia("(hover:hover) and (pointer:fine)").matches;
    items.forEach(function (el, i) {
      var btn = $(".stage__btn", el);
      btn.addEventListener("click", function () { locked = true; show(i); });
      btn.addEventListener("focus", function () { locked = true; show(i); });
      // masaüstünde fare üzerine gelince de sekme açılır — scroll beklemeye gerek yok
      if (canHover) btn.addEventListener("mouseenter", function () { locked = true; show(i); });
    });

    if (!reduce) {
      var raf = 0;
      function tick() {
        raf = 0;
        if (locked) return;
        // bölüm ekranın ortasından geçerken listede aynı oranda ilerle
        var r = sec.getBoundingClientRect();
        var span = r.height - innerHeight * 0.55;
        if (span <= 0) return;
        var p = Math.min(0.999, Math.max(0, (-r.top + innerHeight * 0.32) / span));
        show(Math.floor(p * items.length));
      }
      addEventListener("scroll", function () { if (!raf) raf = requestAnimationFrame(tick); }, { passive: true });
      tick();
    }
  }

  /* ------------------------------------------- 3b. ARKA PLAN VİDEOLARI
     autoplay özniteliğine güvenmiyoruz: tarayıcılar ekran dışındaki veya
     "kullanıcı etkileşimi görmemiş" videoları sessizce duraklatabiliyor.
     Görünür alana girince play() açıkça çağrılıyor, çıkınca duraklıyor. */
  function bgVideos() {
    if (reduce) return;
    var vids = $$("video[autoplay]"); if (!vids.length) return;
    function go(v) { var p = v.play(); if (p && p.catch) p.catch(function () {}); }
    if (!("IntersectionObserver" in window)) { vids.forEach(go); return; }
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        if (en.isIntersecting) go(en.target);
        else { try { en.target.pause(); } catch (e) {} }
      });
    }, { rootMargin: "250px 0px" });
    vids.forEach(function (v) { io.observe(v); });
  }

  /* ------------------------------------------------- 4b. ÜRÜN KARTLARI
     Masaüstünde kart büyümesi salt CSS :hover ile olur. Dokunmatikte hover
     olmadığı için, ekran ortasına en yakın kart aynı büyüme sınıfını alır —
     kaydırırken kartlar sırayla öne çıkar, dokunmayı/gitmeyi engellemez. */
  function productCards() {
    if (reduce || matchMedia("(hover:hover) and (pointer:fine)").matches) return;
    var cards = $$(".card"); if (!cards.length) return;
    var raf = 0, current = null;
    function tick() {
      raf = 0;
      var mid = innerHeight / 2, best = null, bestD = Infinity;
      cards.forEach(function (c) {
        var r = c.getBoundingClientRect();
        if (r.bottom < 0 || r.top > innerHeight) return;
        var d = Math.abs((r.top + r.bottom) / 2 - mid);
        if (d < bestD) { bestD = d; best = c; }
      });
      if (best !== current) {
        if (current) current.classList.remove("is-near");
        if (best) best.classList.add("is-near");
        current = best;
      }
    }
    addEventListener("scroll", function () { if (!raf) raf = requestAnimationFrame(tick); }, { passive: true });
    tick();
  }

  /* --------------------------------------------------------- 5. GİRİŞLER */
  function rise() {
    var els = $$("[data-rise]"); if (!els.length) return;
    if (reduce || !("IntersectionObserver" in window)) {
      els.forEach(function (e) { e.classList.add("in"); }); return;
    }
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (en) {
        if (!en.isIntersecting) return;
        var d = en.target.getAttribute("data-rise");
        en.target.style.transitionDelay = (d ? +d : 0) + "ms";
        en.target.classList.add("in");
        io.unobserve(en.target);
      });
    }, { rootMargin: "0px 0px -12% 0px", threshold: 0.08 });
    els.forEach(function (e) { io.observe(e); });
  }

  /* ---------------------------------------------------------- 6. TEKLİF
     Asıl kanal e-posta: talep info@ kutusuna düşer ve kullanıcı gönderimin
     gerçekten başarılı olduğunu görür. WhatsApp ikinci bir seçenek olarak
     durur — mail gidemezse de yol açık kalsın. */
  function quote() {
    var f = $("#quoteForm"); if (!f) return;
    var btn = $("#quoteSend"), wa = $("#quoteWa");
    var ok = $("#quoteOk"), err = $("#quoteErr");
    var sel = $("#f-urun"), dnWrap = $("#f-dn-wrap"), dn = $("#f-dn");

    // Standart ölçü alanı yalnızca DIN 2576 tablosu olan ürünlerde görünür
    function dnGoster() {
      if (!sel || !dnWrap) return;
      var o = sel.options[sel.selectedIndex];
      var olculu = !!(o && o.hasAttribute("data-olcu"));
      dnWrap.hidden = !olculu;
      if (!olculu && dn) dn.value = "";
    }
    if (sel) {
      // ürün sayfasındaki "Bu ürün için teklif iste" -> ?urun=<slug>
      var q = (location.search.match(/[?&]urun=([a-z0-9-]+)/) || [])[1];
      if (q && sel.querySelector('option[value="' + q + '"]')) sel.value = q;
      sel.addEventListener("change", dnGoster);
      dnGoster();
    }
    function urunAdi() {
      var o = sel && sel.options[sel.selectedIndex];
      return o && o.value ? o.textContent : "";
    }

    function topla() {
      var d = new FormData(f);
      return {
        ad: d.get("ad") || "", firma: d.get("firma") || "", tel: d.get("tel") || "",
        urun: d.get("urun") || "", dn: d.get("dn") || "", adet: d.get("adet") || "",
        olcu: d.get("olcu") || "",
        aciliyet: d.get("aciliyet") || "", not: d.get("not") || "",
        website: d.get("website") || ""   // bot tuzağı; insan kullanıcıda hep boş
      };
    }
    function metin(a) {
      return [
        "Teklif talebi — tuzlaconta.com",
        "Ad: " + a.ad, "Firma: " + a.firma, "Telefon: " + a.tel,
        "Ürün: " + urunAdi() + (a.dn ? " — DN " + a.dn + " (DIN 2576 PN16)" : ""),
        "Adet: " + a.adet, "Ölçü / açıklama: " + a.olcu,
        "Aciliyet: " + a.aciliyet, "Not: " + a.not
      ].join("\n");
    }
    function goster(el) {
      [ok, err].forEach(function (x) { if (x) x.hidden = true; });
      if (el) { el.hidden = false; el.focus(); }
    }

    if (wa) {
      wa.addEventListener("click", function () {
        window.open("https://wa.me/905425962823?text=" +
          encodeURIComponent(metin(topla())), "_blank", "noopener");
      });
    }

    f.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!f.reportValidity()) return;

      var eski = btn ? btn.innerHTML : "";
      if (btn) { btn.disabled = true; btn.textContent = "Gönderiliyor…"; }

      fetch("/api/teklif-gonder", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(topla())
      })
        .then(function (r) { return r.ok ? r.json() : null; })
        .then(function (j) {
          if (j && j.ok) { goster(ok); f.reset(); dnGoster(); }
          else { goster(err); }
        })
        .catch(function () { goster(err); })
        .then(function () {
          if (btn) { btn.disabled = false; btn.innerHTML = eski; }
        });
    });
  }

  /* ---------------------------------------------------------- 7. TEMA
     Üç hal: harmony (varsayılan, marka laciverti) -> dark (gece, siyaha
     yakın) -> light (gündüz, beyaza yakın) -> harmony ... döngüsü. */
  function theme() {
    var btn = $("#themeBtn"); if (!btn) return;
    var meta = $('meta[name="theme-color"]');
    var ORDER = ["harmony", "dark", "light"];
    var COLORS = { harmony: "#162D63", dark: "#0A1322", light: "#F5F8FC" };
    function apply(t, persist) {
      document.documentElement.setAttribute("data-theme", t);
      if (meta) meta.setAttribute("content", COLORS[t] || COLORS.harmony);
      btn.setAttribute("aria-pressed", t !== "harmony" ? "true" : "false");
      if (persist) { try { localStorage.setItem("tc-theme", t); } catch (e) {} }
    }
    btn.addEventListener("click", function () {
      var cur = document.documentElement.getAttribute("data-theme");
      var i = ORDER.indexOf(cur);
      var next = ORDER[(i + 1 + ORDER.length) % ORDER.length];
      apply(next, true);
    });
    // sayfa açılışında head'deki satır içi betik zaten data-theme'i erken
    // ayarladı (yanıp sönmeyi önlemek için); burada sadece meta senkronu
    var boot = document.documentElement.getAttribute("data-theme");
    apply(ORDER.indexOf(boot) >= 0 ? boot : "harmony", false);
  }

  /* --------------------------------------------------------- 8. CURSOR
     Sadece hassas işaretçili (mouse/trackpad) cihazlarda: nokta imlecin tam
     üstünde, halka gevşek bir yayla arkadan takip eder; etkileşimli öğe
     üstündeyken halka büyür. */
  function cursor() {
    if (reduce || !matchMedia("(hover:hover) and (pointer:fine)").matches) return;
    var el = $("#cursor"); if (!el) return;
    var dot = $(".cursor__dot", el), ring = $(".cursor__ring", el);
    var x = innerWidth / 2, y = innerHeight / 2, rx = x, ry = y, seen = false;
    document.documentElement.classList.add("has-cursor");
    addEventListener("mousemove", function (e) {
      x = e.clientX; y = e.clientY;
      dot.style.transform = "translate(" + x + "px," + y + "px) translate(-50%,-50%)";
      if (!seen) { seen = true; el.classList.remove("is-hidden"); rx = x; ry = y; }
    }, { passive: true });
    document.addEventListener("mouseleave", function () { el.classList.add("is-hidden"); });
    document.addEventListener("mouseenter", function () { el.classList.remove("is-hidden"); });
    addEventListener("mousedown", function () { el.classList.add("is-down"); });
    addEventListener("mouseup", function () { el.classList.remove("is-down"); });
    document.addEventListener("mouseover", function (e) {
      var on = !!(e.target.closest && e.target.closest(
        "a,button,[role=button],input,select,textarea,summary,.card,.scene,.stage__btn"));
      el.classList.toggle("is-active", on);
    });
    el.classList.add("is-hidden");
    (function loop() {
      rx += (x - rx) * 0.2; ry += (y - ry) * 0.2;
      ring.style.transform = "translate(" + rx + "px," + ry + "px) translate(-50%,-50%)";
      requestAnimationFrame(loop);
    })();
  }

  /* ------------------------------------------------------------------ */
  function boot() { intro(); nav(); theme(); cursor(); hero(); bgVideos(); stage(); productCards(); rise(); quote(); }
  if (document.readyState === "loading") addEventListener("DOMContentLoaded", boot);
  else boot();
})();
