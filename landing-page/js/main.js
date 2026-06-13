/**
 * 科学探险家 Landing Page — Interactions
 * - Sticky header shadow on scroll
 * - Smooth scroll for anchor links
 * - Scroll-triggered reveal animations
 * - Canvas scaling for large screens
 */

(function () {
  'use strict';

  // ===== Sticky Header Shadow =====
  const header = document.getElementById('header');
  let lastScrollY = 0;

  function updateHeaderShadow() {
    const scrollY = window.scrollY;
    if (scrollY > 10) {
      header.style.boxShadow = '0 6px 24px rgba(200, 200, 240, 0.5)';
    } else {
      header.style.boxShadow = '0 4px 16px rgba(200, 200, 240, 0.35)';
    }
    lastScrollY = scrollY;
    requestAnimationFrame(() => {});
  }

  window.addEventListener('scroll', updateHeaderShadow, { passive: true });

  // ===== Smooth Scroll for Anchor Links =====
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      var targetId = this.getAttribute('href');
      if (targetId === '#') return;
      
      var target = document.querySelector(targetId);
      if (target) {
        e.preventDefault();
        var headerHeight = header.offsetHeight;
        var targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight - 20;
        
        window.scrollTo({
          top: targetPosition,
          behavior: 'smooth'
        });
      }
    });
  });

  // ===== Scroll-Triggered Reveal =====
  var revealElements = document.querySelectorAll(
    '.feature-card, .step, .hero-badge, .hero-headline, .hero-subline, .hero-ctas'
  );

  var observerOptions = {
    root: null,
    rootMargin: '0px 0px -60px 0px',
    threshold: 0.15
  };

  var revealObserver = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        revealObserver.unobserve(entry.target);
      }
    });
  }, observerOptions);

  revealElements.forEach(function (el) {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    revealObserver.observe(el);
  });

  // ===== Hero elements visible immediately =====
  setTimeout(function () {
    document.querySelectorAll('.hero-badge, .hero-headline, .hero-subline, .hero-ctas, .hero-visual').forEach(function (el) {
      el.style.opacity = '1';
      el.style.transform = 'translateY(0)';
    });
  }, 100);

  // ===== Canvas Scaling for Large Screens =====
  function applyCanvasScale() {
    var pageWidth = 1440;
    var viewportWidth = window.innerWidth;
    
    if (viewportWidth > pageWidth) {
      // Center the content with max-width
      document.body.style.display = 'flex';
      document.body.style.flexDirection = 'column';
      document.body.style.alignItems = 'center';
    } else if (viewportWidth > 768 && viewportWidth < pageWidth) {
      // Scale down proportionally
      var scale = viewportWidth / pageWidth;
      document.body.style.transform = 'scale(' + scale + ')';
      document.body.style.transformOrigin = 'top center';
      document.body.style.width = pageWidth + 'px';
    }
  }

  // Only apply scaling on desktop
  if (window.innerWidth >= 1025) {
    applyCanvasScale();
    window.addEventListener('resize', applyCanvasScale);
  }

  console.log('🔮 科学探险家 · Landing Page Ready!');
})();
