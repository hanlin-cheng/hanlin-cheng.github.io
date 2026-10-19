// Each visit or refresh samples all published notes with equal probability.
const randomNotes = document.querySelector<HTMLElement>('#random-notes');
const notePool = document.querySelector<HTMLTemplateElement>('#random-notes-pool');
const refreshNotes = document.querySelector<HTMLButtonElement>('.notes-refresh');
if (randomNotes && notePool && refreshNotes) {
    const cards = Array.from(notePool.content.querySelectorAll<HTMLElement>('.note-card'));
    const count = Math.min(Number(randomNotes.dataset.count) || 8, cards.length);
    const status = document.querySelector<HTMLElement>('.random-notes-status');
    let batch = 0;
    const showRandomNotes = () => {
        const shuffled = [...cards];
        // Fisher–Yates: no category weighting and no duplicates within a batch.
        for (let i = shuffled.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
        }
        randomNotes.replaceChildren(...shuffled.slice(0, count).map(card => card.cloneNode(true)));
        batch += 1;
        if (status && batch > 1) status.textContent = `已随机展示 ${count} 篇笔记，第 ${batch} 批`;
    };
    if (count > 0) {
        showRandomNotes();
        refreshNotes.hidden = false;
        refreshNotes.addEventListener('click', showRandomNotes);
        window.addEventListener('pageshow', event => {
            if (event.persisted) showRandomNotes();
        });
    }
}

// Keep section headings below the sticky navigation, including mobile navigation.
document.addEventListener('click', (event: MouseEvent) => {
    const element = event.target instanceof Element ? event.target : null;
    const link = element?.closest<HTMLAnchorElement>('a[href^="#"]');
    const href = link?.getAttribute('href');
    if (!href || href === '#' || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    let target: HTMLElement | null = null;
    try { target = document.getElementById(decodeURIComponent(href.slice(1))); } catch { return; }
    if (!target) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    const navigationHeight = document.querySelector('.topbar')?.getBoundingClientRect().height || 0;
    history.pushState(null, '', href);
    window.scrollTo({
        top: target.getBoundingClientRect().top + window.scrollY - navigationHeight - 20,
        behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth',
    });
}, true);

// Native lightbox for Markdown and inline HTML images, with no CDN dependency.
const imageViewer = document.querySelector<HTMLDialogElement>('.image-viewer');
if (imageViewer) {
    const preview = imageViewer.querySelector<HTMLImageElement>('.image-viewer-image')!;
    const stage = imageViewer.querySelector<HTMLElement>('.image-viewer-stage')!;
    const zoomButton = imageViewer.querySelector<HTMLButtonElement>('.image-viewer-zoom')!;
    const closeButton = imageViewer.querySelector<HTMLButtonElement>('.image-viewer-close')!;
    let previousOverflow = '';

    const resetZoom = () => {
        stage.classList.remove('is-zoomed');
        preview.style.removeProperty('width');
        zoomButton.textContent = '放大细节';
        zoomButton.setAttribute('aria-pressed', 'false');
        stage.scrollTop = 0;
        stage.scrollLeft = 0;
    };
    const toggleZoom = () => {
        if (stage.classList.contains('is-zoomed')) { resetZoom(); return; }
        const width = Math.max(preview.naturalWidth, preview.getBoundingClientRect().width * 2);
        stage.classList.add('is-zoomed');
        preview.style.width = `${width}px`;
        zoomButton.textContent = '适应屏幕';
        zoomButton.setAttribute('aria-pressed', 'true');
    };
    document.querySelectorAll<HTMLImageElement>('.article-content img').forEach((image, index) => {
        // Keep links to other content and existing interactive elements intact.
        if (image.closest('a, button')) return;
        const trigger = document.createElement('button');
        trigger.type = 'button';
        trigger.className = 'image-zoom-trigger';
        trigger.setAttribute('aria-label', `放大图片：${image.alt || `第 ${index + 1} 张图片`}`);
        trigger.setAttribute('aria-haspopup', 'dialog');
        image.before(trigger);
        trigger.append(image);
        trigger.addEventListener('click', () => {
            resetZoom();
            preview.src = image.currentSrc || image.src;
            preview.alt = image.alt || '笔记图片';
            previousOverflow = document.body.style.overflow;
            document.body.style.overflow = 'hidden';
            imageViewer.showModal();
        });
    });
    zoomButton.addEventListener('click', toggleZoom);
    preview.addEventListener('click', toggleZoom);
    closeButton.addEventListener('click', () => imageViewer.close());
    imageViewer.addEventListener('click', event => {
        if (event.target === imageViewer || event.target === stage) imageViewer.close();
    });
    imageViewer.addEventListener('close', () => {
        document.body.style.overflow = previousOverflow;
        preview.removeAttribute('src');
        resetZoom();
    });
}
