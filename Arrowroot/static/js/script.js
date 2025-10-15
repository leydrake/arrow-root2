// Test script to confirm static JS loading
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Arrowroot static JavaScript loaded successfully!');
    
    // Add a visual indicator that JS is working
    const testElement = document.createElement('div');
    testElement.id = 'js-test-indicator';
    testElement.className = 'fixed bottom-4 right-4 bg-green-500 text-white px-3 py-1 rounded text-sm z-50';
    testElement.textContent = '✅ JS Active';
    testElement.style.display = 'none';
    
    document.body.appendChild(testElement);
    
    // Show indicator for 3 seconds
    setTimeout(() => {
        testElement.style.display = 'block';
        setTimeout(() => {
            testElement.style.display = 'none';
        }, 3000);
    }, 500);
    
    // Add smooth scrolling to navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});

// Utility function for future use
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 px-4 py-2 rounded shadow-lg z-50 ${
        type === 'success' ? 'bg-green-500' : 
        type === 'error' ? 'bg-red-500' : 'bg-blue-500'
    } text-white`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}