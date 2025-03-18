function initializePopups() {
    const updatePopups = () => {
        const pageWidth = document.querySelector('.page').offsetWidth;
        
        document.querySelectorAll('sup[id^="fnref"]').forEach(sup => {
            const rect = sup.getBoundingClientRect();
            const pageRect = document.querySelector('.page').getBoundingClientRect();
            const leftOffset = rect.left - pageRect.left;
            const popup = sup.querySelector('.footnote-popup');
            
            if (!popup) return;

            // Check word count and set width accordingly
            const words = popup.textContent.trim().split(/\s+/).length;
            if (words === 1) {
                popup.style.width = 'fit-content';
            } else {
                popup.style.width = `min(400px, calc(${pageWidth}px - 40px))`;
            }
            
            const popupWidth = popup.offsetWidth;
            
            // Calculate center position
            const centerPosition = leftOffset + (rect.width / 2);
            
            // Calculate how far the popup would extend past each edge
            const leftOverflow = (popupWidth / 2) - centerPosition;
            const rightOverflow = (centerPosition + popupWidth / 2) - pageWidth;
            
            // Calculate required shift
            let shift = 0;
            if (leftOverflow > 0) {
                shift = leftOverflow;
            } else if (rightOverflow > 0) {
                shift = -rightOverflow;
            }
            
            sup.style.setProperty('--popup-shift', `${shift}px`);
        });
    };

    // Initial update
    updatePopups();
    
    // Update on window resize
    window.addEventListener('resize', updatePopups);
    
    // Update on mouseenter
    document.querySelectorAll('sup[id^="fnref"]').forEach(sup => {
        sup.addEventListener('mouseenter', updatePopups);
    });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializePopups); 