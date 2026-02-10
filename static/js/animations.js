// Simple scroll reveal using IntersectionObserver
(function(){
    const revealSelector = '.reveal';
    const items = document.querySelectorAll(revealSelector);
    if(!items.length) return;

    const onObserve = (entries, obs) => {
        entries.forEach(entry => {
            if(entry.isIntersecting){
                entry.target.classList.add('is-visible');
                obs.unobserve(entry.target);
            }
        });
    };

    if('IntersectionObserver' in window){
        const io = new IntersectionObserver(onObserve, {root:null, rootMargin:'0px 0px -10% 0px', threshold: 0.08});
        items.forEach(i => io.observe(i));
    } else {
        // fallback: make all visible
        items.forEach(i => i.classList.add('is-visible'));
    }
})();

// Desktop category scroller (arrows + fades)
(function(){
    const root = document.querySelector('[data-category-scroll]');
    if(!root) return;
    const viewport = root.querySelector('[data-category-scroll-viewport]');
    const list = root.querySelector('[data-category-scroll-list]');
    const btnLeft = root.querySelector('[data-category-scroll-btn="left"]');
    const btnRight = root.querySelector('[data-category-scroll-btn="right"]');
    if(!viewport || !list || !btnLeft || !btnRight) return;

    function clamp(n, a, b){
        return Math.max(a, Math.min(b, n));
    }

    function update(){
        const maxScroll = Math.max(0, list.scrollWidth - list.clientWidth);
        const left = list.scrollLeft;
        const eps = 2;

        const overflowing = maxScroll > eps;
        root.classList.toggle('is-overflowing', overflowing);
        btnLeft.disabled = !overflowing || left <= eps;
        btnRight.disabled = !overflowing || left >= (maxScroll - eps);
    }

    function scrollByAmount(dir){
        const amount = Math.round(clamp(list.clientWidth * 0.65, 180, 420));
        list.scrollBy({left: dir * amount, behavior: 'smooth'});
    }

    btnLeft.addEventListener('click', function(){
        scrollByAmount(-1);
    });
    btnRight.addEventListener('click', function(){
        scrollByAmount(1);
    });

    list.addEventListener('scroll', function(){
        update();
    }, {passive:true});

    window.addEventListener('resize', function(){
        update();
    }, {passive:true});

    // Initial state
    update();
})();

// Mobile categories drawer
(function(){
    const roots = Array.from(document.querySelectorAll('[data-mobile-categories]'));
    if(!roots.length) return;

    function getToggleForRoot(root){
        const host = root.closest('li');
        if(!host) return null;
        return host.querySelector('[data-action="toggle-categories"]');
    }

    function closeAll(){
        roots.forEach(r => {
            const btn = getToggleForRoot(r);
            r.classList.remove('is-open');
            r.setAttribute('aria-hidden', 'true');
            r.style.removeProperty('--mc-top');
            r.style.removeProperty('--mc-left');
            r.style.removeProperty('--mc-width');
            if(btn) btn.setAttribute('aria-expanded', 'false');
        });
    }

    function position(root){
        const btn = getToggleForRoot(root);
        if(!btn) return;
        const bar = document.querySelector('.category-bar');
        const btnRect = btn.getBoundingClientRect();
        const barRect = bar ? bar.getBoundingClientRect() : btnRect;
        const panel = root.querySelector('.mobile-categories__panel');
        const sidePad = 18;
        const desiredWidth = Math.min(320, Math.floor(window.innerWidth - (sidePad * 2)));
        const left = Math.max(sidePad, Math.min(Math.floor(btnRect.left), Math.floor(window.innerWidth - desiredWidth - sidePad)));
        const top = Math.floor(barRect.bottom + 8);
        root.style.setProperty('--mc-left', left + 'px');
        root.style.setProperty('--mc-top', top + 'px');
        root.style.setProperty('--mc-width', desiredWidth + 'px');
        if(panel) panel.style.maxWidth = (window.innerWidth - (sidePad * 2)) + 'px';
    }

    function open(root){
        closeAll();
        const btn = getToggleForRoot(root);
        root.classList.add('is-open');
        root.setAttribute('aria-hidden', 'false');
        if(btn) btn.setAttribute('aria-expanded', 'true');
        position(root);
        const panel = root.querySelector('.mobile-categories__panel');
        if(panel) panel.focus();
    }

    function toggle(root){
        if(root.classList.contains('is-open')) closeAll();
        else open(root);
    }

    roots.forEach(root => {
        const btn = getToggleForRoot(root);
        if(!btn) return;

        btn.addEventListener('click', function(e){
            e.preventDefault();
            e.stopPropagation();
            toggle(root);
        });

        root.addEventListener('click', function(e){
            const actionEl = e.target.closest('[data-action]');
            if(!actionEl) return;
            const action = actionEl.getAttribute('data-action');
            if(action === 'close-categories') closeAll();
        });
    });

    document.addEventListener('click', function(e){
        const clickedToggle = e.target.closest('[data-action="toggle-categories"]');
        if(clickedToggle) return;
        const clickedInside = e.target.closest('[data-mobile-categories]');
        if(clickedInside) return;
        closeAll();
    });

    document.addEventListener('keydown', function(e){
        if(e.key !== 'Escape') return;
        closeAll();
    });

    window.addEventListener('resize', function(){
        const openRoot = roots.find(r => r.classList.contains('is-open'));
        if(openRoot) position(openRoot);
    });

    window.addEventListener('scroll', function(){
        const openRoot = roots.find(r => r.classList.contains('is-open'));
        if(openRoot) position(openRoot);
    }, {passive:true});
})();
// Add-to-cart visual feedback
(function(){
    function animateAdd(btn){
        const rect = btn.getBoundingClientRect();
        const dot = document.createElement('div');
        dot.style.position = 'fixed';
        dot.style.left = (rect.left + rect.width/2) + 'px';
        dot.style.top = (rect.top + rect.height/2) + 'px';
        dot.style.width = '14px';
        dot.style.height = '14px';
        dot.style.borderRadius = '50%';
        dot.style.background = 'rgba(194,165,123,0.95)';
        dot.style.zIndex = 9999;
        dot.style.pointerEvents = 'none';
        document.body.appendChild(dot);
        dot.animate([
            {transform: 'translateY(0) scale(1)', opacity:1},
            {transform: 'translateY(-40px) scale(.6)', opacity:0.6},
        ], {duration:700, easing:'cubic-bezier(.2,.9,.2,1)'}).onfinish = () => dot.remove();
    }

    document.addEventListener('click', function(e){
        const btn = e.target.closest('.btn-add');
        if(!btn) return;
        e.preventDefault();
        e.stopPropagation();
        animateAdd(btn);
        // AJAX add to cart
        const pk = btn.getAttribute('data-pk');
        if(!pk) return;

        function getCookie(name){
            const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
            return v ? v.pop() : '';
        }

        fetch('/cart/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({pk: pk, qty: 1})
        }).then(r=>r.json()).then(data=>{
            if(data && data.ok){
                const el = document.getElementById('cart-count');
                if(el) el.textContent = data.items;
            }
        }).catch(()=>{});
    });

// Cart quantity and remove controls
document.addEventListener('click', function(e){
    const inc = e.target.closest('.cart-increase');
    const dec = e.target.closest('.cart-decrease');
    const rem = e.target.closest('.cart-remove');
    const btn = inc || dec || rem;
    if(!btn) return;
    e.preventDefault();
    const pk = btn.getAttribute('data-pk');
    let action = 'inc';
    if(dec) action = 'dec';
    if(rem) action = 'remove';

    function getCookie(name){
        const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
        return v ? v.pop() : '';
    }

    fetch('/cart/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({pk: pk, action: action})
    }).then(r=>r.json()).then(data=>{
        if(!data || !data.ok) return;
        const countEl = document.getElementById('cart-count');
        if(countEl) countEl.textContent = data.items;

        if(parseInt(data.items, 10) === 0){
            window.location.reload();
            return;
        }

        // update item qty/subtotal
        const qtyEl = document.getElementById('qty-' + pk);
        const subEl = document.getElementById('subtotal-' + pk);
        if(data.item_qty && qtyEl) qtyEl.textContent = data.item_qty;
        if(subEl) subEl.textContent = (data.item_subtotal ? data.item_subtotal : '0') + ' ₴';

        // if removed, remove row
        if(!data.item_qty){
            const row = document.querySelector('.cart-row[data-pk="' + pk + '"]');
            if(row) row.remove();
        }

        // update total
        const totalEl = document.getElementById('cart-total');
        if(totalEl) totalEl.textContent = data.total;
    }).catch(()=>{});
});
})();

/* Simple banner carousel */
(function(){
    const banner = document.querySelector('.hero-banner');
    if(!banner) return;
    const slides = banner.querySelectorAll('.slide');
    const dotsWrap = banner.querySelector('.dots');
    const prev = banner.querySelector('.banner-prev');
    const next = banner.querySelector('.banner-next');
    let idx = 0;
    let timer = null;

    // create dots
    slides.forEach((s, i) =>{
        const btn = document.createElement('button');
        if(i===0) btn.classList.add('active');
        btn.addEventListener('click', ()=> go(i));
        dotsWrap.appendChild(btn);
    });

    function setActive(i){
        slides.forEach((s, k)=> s.classList.toggle('is-active', k===i));
        const dots = dotsWrap.querySelectorAll('button');
        dots.forEach((d,k)=> d.classList.toggle('active', k===i));
        idx = i;
    }

    function go(i){
        setActive((i+slides.length)%slides.length);
    }

    function nextSlide(){
        go(idx+1);
    }

    // bind prev/next only if present (buttons were removed for a cleaner banner)
    if(next) next.addEventListener('click', ()=>{ nextSlide(); resetTimer(); });
    if(prev) prev.addEventListener('click', ()=>{ go(idx-1); resetTimer(); });

    function startTimer(){
        // autoplay every 2 seconds per request
        timer = setInterval(nextSlide, 4000);
    }
    function resetTimer(){
        if(timer) clearInterval(timer);
        startTimer();
    }

    banner.addEventListener('mouseenter', ()=> { if(timer) clearInterval(timer); });
    banner.addEventListener('mouseleave', ()=> startTimer());

    startTimer();
})();
