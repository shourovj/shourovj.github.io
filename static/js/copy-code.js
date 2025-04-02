function addCopyButtons() {
    // Find all code blocks
    document.querySelectorAll('.highlight').forEach(block => {
        // Create button
        const button = document.createElement('button');
        button.className = 'copy-button';
        button.setAttribute('aria-label', 'Copy code');
        
        // Add click handler
        button.addEventListener('click', async () => {
            // Get the code content
            const code = block.querySelector('pre').textContent;
            
            try {
                await navigator.clipboard.writeText(code);
                button.classList.add('success');
                
                // Reset after 2 seconds
                setTimeout(() => {
                    button.classList.remove('success');
                }, 2000);
            } catch (err) {
                console.error('Failed to copy:', err);
            }
        });
        
        // Add button to code block
        block.appendChild(button);
    });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', addCopyButtons); 