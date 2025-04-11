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
            const text = popup.textContent.trim();
            const words = text.split(/\s+/).length;
            if (words == 1 ) {
                popup.style.width = 'fit-content';
            } else if (words < 10) {
                // Estimate width based on character count and approximate character width
                const charWidth = 7; // Approximate width of a character in pixels at base font size
                const estimatedWidth = Math.min(text.length * charWidth, 300); // Cap at 300px
                popup.style.width = `${estimatedWidth}pt`;
            } else {
                popup.style.width = `min(500px, calc(${pageWidth}px - 40px))`;
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
    
    // Handle both hover and click events
    document.querySelectorAll('sup[id^="fnref"]').forEach(sup => {
        sup.addEventListener('mouseenter', updatePopups);
        
        // Add click handler for toggle buttons
        const toggleBtn = sup.querySelector('.footnote-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', (e) => {
                e.preventDefault();
                const popup = sup.querySelector('.footnote-popup');
                const ref = sup.querySelector('.footnote-ref');
                const icon = sup.querySelector('.footnote-icon');
                
                // Toggle popup visibility
                popup.classList.toggle('visible');
                
                // Toggle styles on the reference and icon
                if (popup.classList.contains('visible')) {
                    ref.style.backgroundColor = 'var(--link-color)';
                    ref.style.color = 'var(--bg-main)';
                    icon.style.transform = 'rotate(45deg)';
                } else {
                    ref.style.backgroundColor = 'var(--bg-main)';
                    ref.style.color = 'var(--link-color)';
                    icon.style.transform = '';
                }
                
                // Close other popups
                document.querySelectorAll('.footnote-popup.visible').forEach(p => {
                    if (p !== popup) {
                        p.classList.remove('visible');
                        // Reset styles on other refs
                        const otherRef = p.parentElement.querySelector('.footnote-ref');
                        const otherIcon = p.parentElement.querySelector('.footnote-icon');
                        otherRef.style.backgroundColor = 'var(--bg-main)';
                        otherRef.style.color = 'var(--link-color)';
                        otherIcon.style.transform = '';
                    }
                });
            });
        }
    });
    
    // Close popups when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('sup[id^="fnref"]')) {
            document.querySelectorAll('.footnote-popup.visible').forEach(popup => {
                popup.classList.remove('visible');
                // Reset styles on other refs
                const otherRef = popup.parentElement.querySelector('.footnote-ref');
                const otherIcon = popup.parentElement.querySelector('.footnote-icon');
                otherRef.style.backgroundColor = 'var(--bg-main)';
                otherRef.style.color = 'var(--link-color)';
                otherIcon.style.transform = '';
            });
        }
    });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', initializePopups); 