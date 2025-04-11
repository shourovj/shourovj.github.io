document.addEventListener('DOMContentLoaded', function() {
    const toc = document.querySelector('.toc');
    const title = document.querySelector('.toc-title');
    
    if (toc && title) {
        title.addEventListener('click', () => {
            toc.classList.toggle('collapsed');
            
            // Optionally save state
            localStorage.setItem('tocCollapsed', toc.classList.contains('collapsed'));
        });
        
        // Restore previous state
        const wasCollapsed = localStorage.getItem('tocCollapsed') === 'true';
        if (wasCollapsed) {
            toc.classList.add('collapsed');
        }
    }
}); 