function addCopyButtons() {
    // Find all code blocks
    document.querySelectorAll('.highlight').forEach(block => {
        // Create button
        const button = document.createElement('button');
        button.className = 'copy-button';
        button.setAttribute('aria-label', 'Copy code');
        
        // Add click handler
        button.addEventListener('click', async () => {
            // Select the code content more robustly
            // Try finding code within the table structure first
            let codeElement = block.querySelector('.code pre');
            if (!codeElement) {
                // Fallback for blocks without line numbers
                codeElement = block.querySelector('pre');
            }

            if (codeElement) {
                const code = codeElement.textContent;
                try {
                    await navigator.clipboard.writeText(code);
                    button.classList.add('success');
                    
                    // Reset after 2 seconds
                    setTimeout(() => {
                        button.classList.remove('success');
                    }, 2000);
                } catch (err) {
                    console.error('Failed to copy:', err);
                    // Optional: Provide user feedback on error
                }
            } else {
                console.error('Could not find code element within .highlight block');
            }
        });
        
        // Insert button as the FIRST child of the block
        // This ensures it stays relative to the outer container
        if (block.firstChild) {
            block.insertBefore(button, block.firstChild);
        } else {
            // Fallback if the block is somehow empty
            block.appendChild(button);
        }
    });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', addCopyButtons); 