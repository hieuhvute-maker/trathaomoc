document.addEventListener('DOMContentLoaded', function () {
    const nav = document.getElementById('mainNav');
    const backToTop = document.getElementById('backToTop');

    function onScroll() {
        const y = window.scrollY;
        if (nav) nav.classList.toggle('scrolled', y > 50);
        if (backToTop) backToTop.classList.toggle('show', y > 400);
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    if (backToTop) {
        backToTop.addEventListener('click', function (e) {
            e.preventDefault();
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    const menuLinks = document.querySelectorAll('#mainMenu .nav-link');
    const collapse = document.getElementById('mainMenu');
    menuLinks.forEach(function (link) {
        link.addEventListener('click', function () {
            if (collapse && collapse.classList.contains('show')) {
                bootstrap.Collapse.getOrCreateInstance(collapse).hide();
            }
        });
    });

    const certModal = document.getElementById('certModal');
    if (certModal) {
        certModal.addEventListener('show.bs.modal', function (event) {
            const trigger = event.relatedTarget;
            document.getElementById('certModalImg').src = trigger.dataset.src;
            document.getElementById('certModalTitle').textContent = trigger.dataset.title;
        });
    }

    const galleryModal = document.getElementById('galleryModal');
    if (galleryModal) {
        galleryModal.addEventListener('show.bs.modal', function (event) {
            const trigger = event.relatedTarget;
            const img = document.getElementById('galleryModalImg');
            img.src = trigger.dataset.src;
            img.alt = trigger.dataset.caption;
        });
    }

    const filterButtons = document.querySelectorAll('.btn-filter');
    filterButtons.forEach(function (btn) {
        btn.addEventListener('click', function () {
            filterButtons.forEach(function (b) { b.classList.remove('active'); });
            btn.classList.add('active');
            const filter = btn.dataset.filter;
            document.querySelectorAll('.gallery-item').forEach(function (item) {
                const show = filter === 'all' || item.dataset.category === filter;
                item.classList.toggle('hidden', !show);
            });
        });
    });

    const revealEls = document.querySelectorAll('.value-card, .process-step, .card-organic, .stat-box, .cert-item');
    if ('IntersectionObserver' in window && revealEls.length) {
        revealEls.forEach(function (el) { el.classList.add('reveal'); });
        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.15 });
        revealEls.forEach(function (el) { observer.observe(el); });
    }
});
