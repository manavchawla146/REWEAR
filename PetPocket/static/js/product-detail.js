document.addEventListener('DOMContentLoaded', function() {
    const productId = window.location.pathname.split('/').pop();
    let cartItems = [];
    let wishlistItems = [];

    // Notification function
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        // Add notification styles if they don't exist
        if (!document.querySelector('style[data-notification-styles]')) {
            const style = document.createElement('style');
            style.setAttribute('data-notification-styles', '');
            style.textContent = `
                .notification {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 12px 20px;
                    border-radius: 5px;
                    color: white;
                    font-weight: 500;
                    z-index: 1000;
                    opacity: 0;
                    transform: translateX(100%);
                    transition: all 0.3s ease;
                }
                .notification.success { background-color: #4caf50; }
                .notification.error { background-color: #f44336; }
                .notification.show {
                    opacity: 1;
                    transform: translateX(0);
                }
            `;
            document.head.appendChild(style);
        }
        
        document.body.appendChild(notification);
        setTimeout(() => { notification.classList.add('show'); }, 100);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => { notification.remove(); }, 300);
        }, 3000);
    }

    // Function to fetch current cart state
    async function fetchCartState() {
        try {
            const response = await fetch('/check_cart_status');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const data = await response.json();
            cartItems = data.items || [];
            updateCartButtons();
            updateNavbarCartCount(data.items.length);
        } catch (error) {
            console.error('Error fetching cart state:', error);
        }
    }

    // Function to fetch current wishlist state
    async function fetchWishlistState() {
        try {
            const response = await fetch('/check_wishlist_status');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            const data = await response.json();
            wishlistItems = data.items || [];
            updateWishlistButtons();
        } catch (error) {
            console.error('Error fetching wishlist state:', error);
        }
    }

    // Update Navbar Cart Count
    function updateNavbarCartCount(totalCount) {
        const cartIcon = document.querySelector('.cart-icon');
        let cartBadge = document.querySelector('.cart-badge');
        if (cartIcon) {
            if (!cartBadge) {
                cartBadge = document.createElement('span');
                cartBadge.className = 'cart-badge cart-badge-visible';
                cartIcon.appendChild(cartBadge);
            }
            cartBadge.textContent = totalCount;
            if (totalCount > 0) {
                cartBadge.classList.add('cart-badge-visible');
                cartIcon.classList.add('cart-has-items');
                cartBadge.style.display = 'block';
            } else {
                cartBadge.classList.remove('cart-badge-visible');
                cartIcon.classList.remove('cart-has-items');
                cartBadge.style.display = 'none';
            }
        }
    }

    // Update Cart Buttons
    function updateCartButtons() {
        document.querySelectorAll('.add-to-cart').forEach(btn => {
            const productId = parseInt(btn.dataset.productId);
            const isInCart = cartItems.includes(productId);
            const isMainButton = btn.closest('.product-action');

            if (isInCart) {
                btn.classList.add('added', 'go-to-cart');
                if (isMainButton) {
                    btn.innerHTML = '<span class="material-symbols-outlined">shopping_cart</span> Go to Cart';
                } else {
                    btn.innerHTML = '<span class="material-symbols-outlined">shopping_cart</span> <span class="cart-txt">Go to Cart</span>';
                }
                btn.style.backgroundColor = '#4caf50';
                btn.style.color = '#fff';
            } else {
                btn.classList.remove('added', 'go-to-cart');
                if (isMainButton) {
                    btn.innerHTML = '<span class="material-symbols-outlined">shopping_cart</span> Add to Cart';
                } else {
                    btn.innerHTML = '<span class="material-symbols-outlined">add_shopping_cart</span> <span class="cart-txt">Add to Cart</span>';
                }
                btn.style.backgroundColor = '';
                btn.style.color = '';
            }
        });
    }

    // Update Wishlist Buttons
    function updateWishlistButtons() {
        document.querySelectorAll('.add-to-wishlist').forEach(btn => {
            const productId = parseInt(btn.dataset.productId);
            const isInWishlist = wishlistItems.includes(productId);
            
            if (isInWishlist) {
                btn.classList.add('in-wishlist', 'active');
                btn.querySelector('.material-symbols-outlined').style.fontVariationSettings = "'FILL' 1";
                const txt = btn.querySelector('.wishlist-txt');
                if (txt) txt.textContent = 'In Wishlist';
            } else {
                btn.classList.remove('in-wishlist', 'active');
                btn.querySelector('.material-symbols-outlined').style.fontVariationSettings = "'FILL' 0";
                const txt = btn.querySelector('.wishlist-txt');
                if (txt) txt.textContent = 'Add to Wishlist';
            }
        });
    }

    // Get CSRF token
    function getCSRFToken() {
        const token = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
        console.log('CSRF Token:', token); // Debug log
        if (!token) {
            console.error('CSRF token not found');
            return '';
        }
        return token;
    }

    // Handle Add to Cart
    async function handleAddToCart(productId, button) {
        if (button.classList.contains('go-to-cart')) {
            window.location.href = '/cart';
            return;
        }
        try {
            const quantityInput = document.querySelector('.quantity-input');
            const quantity = quantityInput ? parseInt(quantityInput.value) || 1 : 1;
            const requestData = {
                product_id: parseInt(productId),
                quantity: quantity
            };
            const response = await fetch('/add_to_cart', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin',
                body: JSON.stringify(requestData)
            });
            const responseText = await response.text();
            let data;
            try {
                data = JSON.parse(responseText);
            } catch (e) {
                console.error('Failed to parse response:', e);
                throw new Error('Invalid server response');
            }
            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/signin';
                    return;
                }
                return;
            }
            if (data.success) {
                button.classList.add('go-to-cart');
                button.classList.add('added-to-cart');
                button.innerHTML = '<span class="material-symbols-outlined">shopping_cart</span> Go to Cart';
                updateNavbarCartCount(data.cart_count);
            }
        } catch (error) {
            console.error('Error adding to cart:', error);
        }
    }

    // Handle Wishlist Toggle
    async function toggleWishlist(productId, button) {
        try {
            const requestData = {
                product_id: parseInt(productId)
            };
            const response = await fetch('/add_to_wishlist', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                credentials: 'same-origin',
                body: JSON.stringify(requestData)
            });
            const responseText = await response.text();
            let data;
            try {
                data = JSON.parse(responseText);
            } catch (e) {
                console.error('Failed to parse response:', e);
                throw new Error('Invalid server response');
            }
            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/signin';
                    return;
                }
                return;
            }
            if (data.success) {
                const isInWishlist = button.classList.contains('in-wishlist');
                if (isInWishlist) {
                    button.classList.remove('in-wishlist');
                    button.querySelector('.material-symbols-outlined').style.fontVariationSettings = "'FILL' 0";
                    const txt = button.querySelector('.wishlist-txt');
                    if (txt) txt.textContent = 'Add to Wishlist';
                } else {
                    button.classList.add('in-wishlist');
                    button.querySelector('.material-symbols-outlined').style.fontVariationSettings = "'FILL' 1";
                    const txt = button.querySelector('.wishlist-txt');
                    if (txt) txt.textContent = 'In Wishlist';
                }
            }
        } catch (error) {
            console.error('Error updating wishlist:', error);
        }
    }

    // Event listeners for buttons - using event delegation to avoid conflicts
    document.addEventListener('click', function(e) {
        // Handle Add to Cart button clicks
        const addToCartBtn = e.target.closest('.add-to-cart');
        if (addToCartBtn) {
            e.preventDefault();
            e.stopPropagation();
            const productId = parseInt(addToCartBtn.dataset.productId);
            handleAddToCart(productId, addToCartBtn);
            return;
        }

        // Handle Add to Wishlist button clicks
        const addToWishlistBtn = e.target.closest('.add-to-wishlist');
        if (addToWishlistBtn) {
            e.preventDefault();
            e.stopPropagation();
            const productId = parseInt(addToWishlistBtn.dataset.productId);
            toggleWishlist(productId, addToWishlistBtn);
            return;
        }

        // Handle product card clicks (for related products)
        const productCard = e.target.closest('.product-card');
        if (productCard && !e.target.closest('.add-to-cart') && !e.target.closest('.add-to-wishlist')) {
            const productId = productCard.dataset.productId;
            if (productId) {
                window.location.href = `/product/${productId}`;
            }
        }
    });

    // Check initial states on page load
    fetchCartState();
    fetchWishlistState();

    // Re-fetch states when navigating back to the page
    window.addEventListener('pageshow', (event) => {
        if (event.persisted || performance.navigation.type === 2) {
            fetchCartState();
            fetchWishlistState();
            // Also update cart/wishlist button states immediately
            setTimeout(() => {
                updateCartButtons();
                updateWishlistButtons();
            }, 100);
        }
    });

    // Tabs functionality
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById(tab.dataset.tab).classList.add('active');
        });
    });

    // Image Gallery functionality
    const mainImage = document.querySelector('#main-product-image');
    const thumbnails = document.querySelectorAll('.thumbnail');
    let currentImageIndex = 0;

    // Always set the main image as the first thumbnail
    function updateImage(index) {
        thumbnails.forEach(t => t.classList.remove('active'));
        thumbnails[index].classList.add('active');
        mainImage.src = thumbnails[index].dataset.imageUrl;
        currentImageIndex = index;
    }

    const prevBtn = document.querySelector('.image-nav-btn.prev');
    const nextBtn = document.querySelector('.image-nav-btn.next');

    if (prevBtn) {
        prevBtn.addEventListener('click', () => {
        let newIndex = currentImageIndex - 1;
        if (newIndex < 0) newIndex = thumbnails.length - 1;
        updateImage(newIndex);
    });
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => {
        let newIndex = (currentImageIndex + 1) % thumbnails.length;
        updateImage(newIndex);
    });
    }

    thumbnails.forEach((thumbnail, index) => {
        thumbnail.addEventListener('click', () => updateImage(index));
    });

    // On page load, ensure the main image is set and the first thumbnail is active
    updateImage(0);

    // Quantity Selector functionality
    const quantityInput = document.querySelector('.quantity-input');
    const decreaseBtn = document.querySelector('.quantity-btn.decrease');
    const increaseBtn = document.querySelector('.quantity-btn.increase');

    if (quantityInput && decreaseBtn && increaseBtn) {
        decreaseBtn.addEventListener('click', () => {
            let value = parseInt(quantityInput.value);
            if (value > 1) {
                quantityInput.value = value - 1;
            }
        });

        increaseBtn.addEventListener('click', () => {
            let value = parseInt(quantityInput.value);
            let max = parseInt(quantityInput.max);
            if (value < max) {
                quantityInput.value = value + 1;
            }
        });

        quantityInput.addEventListener('change', () => {
            let value = parseInt(quantityInput.value);
            let max = parseInt(quantityInput.max);
            if (isNaN(value) || value < 1) {
                quantityInput.value = 1;
            } else if (value > max) {
                quantityInput.value = max;
            }
        });
    }

    // Review Form Submission
    const reviewForm = document.getElementById('review-form');
    if (reviewForm) {
        const ratingInputs = reviewForm.querySelectorAll('.rating-select input[type="radio"]');
        const ratingLabels = reviewForm.querySelectorAll('.rating-select label');

        // Initialize rating display
        function initializeRatingDisplay() {
            ratingLabels.forEach((label, index) => {
                const svg = label.querySelector('svg');
                if (svg) {
                    svg.style.fill = '#e8e8e8';
                    svg.style.transition = 'fill 0.2s ease';
                }
            });
        }

        // Update rating display
        function updateRatingDisplay(rating) {
            ratingLabels.forEach((label, index) => {
                const svg = label.querySelector('svg');
                if (svg) {
                    svg.style.fill = index < rating ? '#ffca28' : '#e8e8e8';
                }
            });
        }

        // Initialize rating display
        initializeRatingDisplay();

        // Handle rating interactions
        ratingInputs.forEach((input, index) => {
            const currentRating = index + 1;

            // Handle click/change
            input.addEventListener('change', () => {
                updateRatingDisplay(currentRating);
            });

            // Handle hover
            const label = input.nextElementSibling;
            if (label) {
                label.addEventListener('mouseenter', () => {
                    updateRatingDisplay(currentRating);
            });

                label.addEventListener('mouseleave', () => {
                    const checkedInput = reviewForm.querySelector('input[name="rating"]:checked');
                    const checkedRating = checkedInput ? parseInt(checkedInput.value) : 0;
                    updateRatingDisplay(checkedRating);
                });
            }
        });

        // Handle form submission
        reviewForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const productId = reviewForm.dataset.productId;
            const ratingInput = reviewForm.querySelector('input[name="rating"]:checked');
            const contentTextarea = reviewForm.querySelector('#review-content');

            if (!ratingInput) {
                showNotification('Please select a rating.', 'error');
                return;
            }
            
            if (!contentTextarea || !contentTextarea.value.trim()) {
                showNotification('Please write a review.', 'error');
                return;
            }

            const rating = parseInt(ratingInput.value);
            const content = contentTextarea.value.trim();

            // Disable form during submission
            const submitButton = reviewForm.querySelector('.submit-review');
            const originalButtonText = submitButton.innerHTML;
            submitButton.disabled = true;
            submitButton.innerHTML = '<span class="material-symbols-outlined">hourglass_empty</span> Submitting...';

            try {
                const response = await fetch('/api/reviews/add', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCSRFToken() || ''
                    },
                    body: JSON.stringify({ 
                        product_id: parseInt(productId), 
                        rating: rating, 
                        content: content 
                    })
                });

                if (!response.ok) {
                    if (response.status === 401) {
                        showNotification('Please login to submit a review.', 'error');
                        setTimeout(() => window.location.href = '/signin', 1500);
                        return;
                    }
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();

                if (data.success || (data.message && data.message.includes('successfully'))) {
                    // Success - add the new review to the page
                    addNewReviewToPage(data);
                    
                    // Reset form
                    reviewForm.reset();
                    initializeRatingDisplay();
                    
                    showNotification('Review submitted successfully!', 'success');
                    
                    // Scroll to the new review
                    setTimeout(() => {
                        const reviewList = document.querySelector('.review-list');
                        if (reviewList) {
                            reviewList.scrollIntoView({ behavior: 'smooth' });
                        }
                    }, 500);
                } else {
                    showNotification(data.error || data.message || 'Failed to submit review', 'error');
                }
            } catch (error) {
                console.error('Error submitting review:', error);
                showNotification('Failed to submit review. Please try again.', 'error');
            } finally {
                // Re-enable form
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonText;
            }
        });
    }

    // Helper to format review date like the template
    function formatReviewDate(dateStr) {
        if (!dateStr) return 'Just now';
        // Handles 'YYYY-MM-DD HH:mm:ss' and ISO
        const date = new Date(dateStr.replace(' ', 'T'));
        if (isNaN(date)) return dateStr; // fallback
        const options = { year: 'numeric', month: 'long', day: '2-digit' };
        return date.toLocaleDateString('en-US', options);
    }

    function addNewReviewToPage(data) {
        const reviewList = document.querySelector('.review-list');
        if (!reviewList) return;

        // Remove "no reviews" message if it exists
        const noReviewsMsg = reviewList.querySelector('p');
        if (noReviewsMsg && noReviewsMsg.textContent.includes('No reviews yet')) {
            noReviewsMsg.remove();
        }

        // Remove any existing review by this user
        const allReviews = reviewList.querySelectorAll('.review-item');
        allReviews.forEach(item => {
            const name = item.querySelector('.reviewer-name');
            if (name && name.textContent.trim() === (data.user || 'Anonymous')) {
                item.remove();
            }
        });

        // Create new review element
        const reviewItem = document.createElement('div');
        reviewItem.className = 'review-item';
        // Generate stars HTML
        const starsHtml = Array.from({length: 5}, (_, i) => 
            i < data.rating ? '★' : '☆'
        ).join('');
        // Format date
        const formattedDate = formatReviewDate(data.created_at);
        reviewItem.innerHTML = `
            <div class="review-header">
                <div class="name-rating">
                    <p class="reviewer-name">${escapeHtml(data.user || 'Anonymous')}</p>
                    <div class="review-rating">
                        <span class="stars">${starsHtml}</span>
                    </div>
                </div>
                <div class="date">
                    <p class="review-date">${formattedDate}</p>
                </div>
            </div>
            <p class="review-content">${escapeHtml(data.content)}</p>
        `;
        // Add to top of review list
        reviewList.insertBefore(reviewItem, reviewList.firstChild);
        // Update review statistics if provided
        updateReviewStatistics(data);
    }

    // Function to update review statistics
    function updateReviewStatistics(data) {
        if (data.average_rating && data.total_reviews) {
            const ratingValue = document.querySelector('.rating-value');
            const totalReviews = document.querySelector('.total-reviews');
            const avgStars = document.querySelector('.average-rating .stars');
            const rightStars = document.querySelector('.right-rating-stars');
            const rightCount = document.querySelector('.right-rating-count');

            if (ratingValue) {
                ratingValue.textContent = parseFloat(data.average_rating).toFixed(1);
            }
            if (totalReviews) {
                const reviewText = data.total_reviews === 1 ? 'review' : 'reviews';
                totalReviews.textContent = `(${data.total_reviews} customer ${reviewText})`;
            }
            if (avgStars) {
                const avgRating = Math.floor(parseFloat(data.average_rating));
                avgStars.innerHTML = Array.from({length: 5}, (_, i) => 
                    i < avgRating ? '★' : '☆'
                ).join('');
            }
            if (rightStars) {
                const avgRating = Math.floor(parseFloat(data.average_rating));
                rightStars.innerHTML = Array.from({length: 5}, (_, i) => 
                    i < avgRating ? '★' : '☆'
                ).join('');
            }
            if (rightCount) {
                rightCount.textContent = `(${data.total_reviews} reviews)`;
            }

            // Update rating bars if the data includes rating counts
            if (data.rating_counts) {
                updateRatingBars(data.rating_counts, data.total_reviews);
            }
        }
    }

    // Function to update rating bars
    function updateRatingBars(ratingCounts, totalReviews) {
        for (let i = 1; i <= 5; i++) {
            const ratingBar = document.querySelector(`.rating-bar:nth-child(${6-i})`);
            if (ratingBar) {
                const count = ratingCounts[i] || 0;
                const percentage = totalReviews > 0 ? (count / totalReviews * 100) : 0;
                
                const progressFill = ratingBar.querySelector('.rating-progress-fill');
                const countElement = ratingBar.querySelector('.rating-count');
                
                if (progressFill) progressFill.style.width = `${percentage}%`;
                if (countElement) countElement.textContent = count;
            }
        }
    }

    // Utility function to escape HTML
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Product slider controls
    const slider = document.querySelector('.product-cards');
    const prevSliderBtn = document.querySelector('.product-header-control.prev');
    const nextSliderBtn = document.querySelector('.product-header-control.next');

    if (slider && prevSliderBtn && nextSliderBtn) {
        prevSliderBtn.addEventListener('click', () => {
            slider.scrollBy({ left: -slider.offsetWidth, behavior: 'smooth' });
        });

        nextSliderBtn.addEventListener('click', () => {
            slider.scrollBy({ left: slider.offsetWidth, behavior: 'smooth' });
        });

        slider.addEventListener('scroll', () => {
            prevSliderBtn.disabled = slider.scrollLeft === 0;
            nextSliderBtn.disabled = slider.scrollLeft + slider.offsetWidth >= slider.scrollWidth - 1;
        });
    }

    // Track Product View
    if (productId && !isNaN(productId)) {
    fetch(`/track/product-view/${productId}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
    }).catch(error => console.error('Error tracking product view:', error));
    }
});