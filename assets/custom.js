// Custom JavaScript for additional interactivity

// Add loading animation
document.addEventListener('DOMContentLoaded', function() {
    // Add custom event listeners for smooth interactions
    const tabs = document.querySelectorAll('[data-testid="stTab"]');
    tabs.forEach(tab => {
        tab.addEventListener('click', function() {
            // Add smooth transition effect
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
    });
});

// Add scroll to top functionality
function scrollToTop() {
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Custom tooltip for metrics
function addMetricTooltips() {
    const metrics = document.querySelectorAll('[data-testid="metric-container"]');
    metrics.forEach(metric => {
        metric.title = "Click to filter or see details";
        metric.style.cursor = "pointer";
    });
}

// Initialize when page loads
window.onload = function() {
    addMetricTooltips();
    
    // Add subtle animation to header
    const header = document.querySelector('.main-header');
    if (header) {
        header.style.opacity = '0';
        header.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            header.style.transition = 'all 0.8s ease';
            header.style.opacity = '1';
            header.style.transform = 'translateY(0)';
        }, 300);
    }
};