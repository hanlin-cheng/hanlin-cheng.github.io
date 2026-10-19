// Root override for Stack's code-block enhancement; do not modify the theme.
export function setupCodeCopy() {
    document.querySelectorAll<HTMLElement>('.article-content pre').forEach(pre => {
        let panel = pre.closest<HTMLElement>('.highlight');
        if (panel?.classList.contains('code-panel')) return;
        if (!panel) {
            panel = document.createElement('div');
            panel.className = 'highlight';
            pre.before(panel);
            panel.append(pre);
        }
        const code = panel.querySelector<HTMLElement>('code[data-lang]') || pre.querySelector('code');
        if (!code) return;
        panel.classList.add('code-panel');
        const lang = code.dataset.lang || Array.from(code.classList).find(name => name.startsWith('language-'))?.slice(9) || 'text';
        const labels: Record<string, string> = { 'c++': 'C++', cpp: 'C++', c: 'C', bash: 'Bash', sh: 'Shell', shell: 'Shell', python: 'Python', py: 'Python', javascript: 'JavaScript', js: 'JavaScript', typescript: 'TypeScript', ts: 'TypeScript', yaml: 'YAML', json: 'JSON', cmake: 'CMake', text: '纯文本', plaintext: '纯文本' };
        const toolbar = document.createElement('div');
        toolbar.className = 'code-toolbar';
        const label = document.createElement('span');
        label.className = 'code-language';
        label.textContent = labels[lang.toLowerCase()] || lang;
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'code-copy';
        button.textContent = '复制代码';
        button.setAttribute('aria-label', `复制${label.textContent}代码`);
        const status = document.createElement('span');
        status.className = 'visually-hidden';
        status.setAttribute('role', 'status');
        toolbar.append(label, button, status);
        panel.prepend(toolbar);
        pre.tabIndex = 0;
        pre.setAttribute('aria-label', `${label.textContent}代码，可滚动查看`);
        if (!navigator.clipboard?.writeText) {
            button.disabled = true;
            button.title = '当前浏览器不支持复制，请选中代码手动复制';
        }
        let timer: number | undefined;
        button.addEventListener('click', async () => {
            window.clearTimeout(timer);
            try {
                await navigator.clipboard.writeText(code.textContent || '');
                button.textContent = '已复制';
                status.textContent = '代码已复制';
            } catch {
                button.textContent = '复制失败';
                status.textContent = '复制失败，请选中代码手动复制';
            }
            timer = window.setTimeout(() => { button.textContent = '复制代码'; status.textContent = ''; }, 2000);
        });
    });
}
