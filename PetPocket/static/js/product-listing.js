document.addEventListener('DOMContentLoaded', function() {
    const productCards = document.querySelectorAll('.product-card');
    const sortSelect = document.getElementById('sort');
    const pagination = document.querySelector('.pagination');
    const filterToggleBtn = document.querySelector('.filter-toggle-btn');
    const filterSidebar = document.querySelector('.filter-sidebar');
    const sidebarOverlay = document.querySelector('.sidebar-overlay');
    const closeSidebarBtn = document.querySelector('.close-sidebar-btn');

    let cartItems = [];
    let wishlistItems = [];

    // Toggle sidebar and overlay
    function toggleSidebar() {
        filterSidebar.classList.toggle('active');
        sidebarOverlay.classList.toggle('active');
    }

    if (filterToggleBtn) {
        filterToggleBtn.addEventListener('click', toggleSidebar);
    }

    if (closeSidebarBtn) {
        closeSidebarBtn.addEventListener('click', toggleSidebar);
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', toggleSidebar);
    }

    // Sort functionality
    function sortProducts() {
        const sortValue = sortSelect.value;
        const productGrid = document.querySelector('.product-grid');
        const cardsArray = Array.from(productCards);

        cardsArray.sort((a, b) => {
            const aPrice = parseFloat(a.querySelector('.product-price').textContent.replace(/[^\d.]/g, ''));
            const bPrice = parseFloat(b.querySelector('.product-price').textContent.replace(/[^\d.]/g, ''));
            const aName = a.querySelector('.product-name').textContent.trim().toLowerCase();
            const bName = b.querySelector('.product-name').textContent.trim().toLowerCase();

            switch (sortValue) {
                case 'price-low-to-high':
                    return aPrice - bPrice;
                case 'price-high-to-low':
                    return bPrice - aPrice;
                case 'name-a-to-z':
                    return aName.localeCompare(bName);
                case 'name-z-to-a':
                    return bName.localeCompare(aName);
                default:
                    return 0;
            }
        });

        // Clear and re-append sorted cards
        productGrid.innerHTML = '';
        cardsArray.forEach(card => productGrid.appendChild(card));
    }

    sortSelect.addEventListener('change', sortProducts);

    // Trigger sort on page load
    sortProducts();

    // Notification function
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
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
            updateCartButtons(); // Update buttons based on new state
        } catch (error) {
            console.error('Error fetching cart state:', error);
        }
    }

    // Check cart state on page load
    fetchCartState();

    // Check cart state when navigating back to the page
    window.addEventListener('pageshow', (event) => {
        if (event.persisted || performance.navigation.type === 2) {
            console.log('Page loaded from cache or via history navigation. Re-fetching cart state.');
            fetchCartState();
        }
    });

    // Update Cart Buttons
    function updateCartButtons() {
        document.querySelectorAll('.add-to-cart').forEach(btn => {
            const productId = parseInt(btn.dataset.productId);
            const isInCart = cartItems.includes(productId);
            
            if (isInCart) {
                btn.classList.add('added', 'go-to-cart');
                btn.innerHTML = '<span class="material-symbols-outlined">shopping_cart</span> <span class="cart-txt">Go to Cart</span>';
                btn.onclick = function(e) {
                    e.stopPropagation();
                    window.location.href = '/cart';
                };
            } else {
                // Reset button state if not in cart
                btn.classList.remove('added', 'go-to-cart');
                btn.innerHTML = '<span class="material-symbols-outlined">add_shopping_cart</span> <span class="cart-txt">Add to Cart</span>';
                btn.onclick = null;
            }
        });
    }

    // Add to cart functionality
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            if (this.classList.contains('added')) {
                window.location.href = '/cart';
                return;
            }

            const productId = parseInt(this.dataset.productId);
            try {
                const response = await fetch('/add_to_cart', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
                    },
                    body: JSON.stringify({ 
                        product_id: productId, 
                        quantity: 1 
                    })
                });

                if (!response.ok) {
                    if (response.status === 401) {
                        showNotification('Please login to add items to cart', 'error');
                        setTimeout(() => window.location.href = '/signin', 1500);
                        return;
                    }
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();
                
                if (data.success) {
                    // Update local state
                    if (!cartItems.includes(productId)) {
                        cartItems.push(productId);
                    }
                    
                    // Update button appearance
                    this.classList.add('added', 'go-to-cart');
                    this.innerHTML = '<span class="material-symbols-outlined">shopping_cart</span> <span class="cart-txt">Go to Cart</span>';
                    
                    // Update click handler
                    this.onclick = function(e) {
                        e.stopPropagation();
                        window.location.href = '/cart';
                    };
                    
                    updateCartCount(data.cart_count);
                } else if (data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    showNotification(data.message || 'Failed to add to cart', 'error');
                }
            } catch (error) {
                console.error('Error adding to cart:', error);
                showNotification('Failed to add to cart. Please try again.', 'error');
            }
        });
    });

    // Update cart count in navbar
    function updateCartCount(count) {
        const cartBadge = document.querySelector('.cart-badge');
        const cartIcon = document.querySelector('.cart-icon');
        
        if (cartIcon) {
            if (cartBadge) {
                cartBadge.textContent = count;
                if (count > 0) {
                    cartBadge.classList.add('cart-badge-visible');
                    cartIcon.classList.add('cart-has-items');
                } else {
                    cartBadge.classList.remove('cart-badge-visible');
                    cartIcon.classList.remove('cart-has-items');
                }
            } else if (count > 0) {
                const badge = document.createElement('span');
                badge.className = 'cart-badge';
                badge.textContent = count;
                cartIcon.appendChild(badge);
                cartIcon.classList.add('cart-has-items');
            }
        }
    }

    // Wishlist functionality
    document.querySelectorAll('.add-to-wishlist').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.stopPropagation();
            const productId = parseInt(this.dataset.productId);
            const isInWishlist = wishlistItems.includes(productId);
            const endpoint = isInWishlist ? '/remove_from_wishlist' : '/add_to_wishlist';
            try {
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')
                    },
                    body: JSON.stringify({ product_id: productId })
                });

                if (!response.ok) {
                    if (response.status === 401) {
                        showNotification('Please login to update wishlist', 'error');
                        setTimeout(() => window.location.href = '/signin', 1500);
                        return;
                    }
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }

                const data = await response.json();

                if (data.success) {
                    if (isInWishlist) {
                        wishlistItems = wishlistItems.filter(id => id !== productId);
                        showNotification('Product removed from wishlist!', 'success');
                    } else {
                        wishlistItems.push(productId);
                        showNotification('Product added to wishlist!', 'success');
                    }
                    updateWishlistButtons(); // Update all wishlist buttons on the page
                } else {
                    showNotification(data.message || 'Failed to update wishlist', 'error');
                }
            } catch (error) {
                console.error('Wishlist toggle failed:', error);
                showNotification('Failed to update wishlist. Please try again.', 'error');
            }
        });
    });

    function updateWishlistButtons() {
        document.querySelectorAll('.add-to-wishlist').forEach(btn => {
            const productId = parseInt(btn.dataset.productId);
            if (wishlistItems.includes(productId)) {
                btn.classList.add('in-wishlist');
                btn.querySelector('.material-symbols-outlined').style.fontVariationSettings = "'FILL' 1";
            } else {
                btn.classList.remove('in-wishlist');
                btn.querySelector('.material-symbols-outlined').style.fontVariationSettings = "'FILL' 0";
            }
        });
    }

    // Navigate to product detail page on card click
    productCards.forEach(card => {
        card.addEventListener('click', function(e) {
            if (!e.target.closest('.add-to-cart') && !e.target.closest('.add-to-wishlist')) {
                const productId = this.getAttribute('data-product-id');
                console.log(`Navigating to product: ${productId}`); // Debug log
                window.location.href = `/product/${productId}`;
            }
        });
    });

    // Check initial wishlist status
    fetch('/check_wishlist_status')
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => {
                    throw new Error(`Server returned ${response.status}: ${text}`);
                });
            }
            return response.json();
        })
        .then(data => {
            productCards.forEach(card => {
                const productId = parseInt(card.getAttribute('data-product-id'));
                if (data.items.includes(productId)) {
                    card.querySelector('.add-to-wishlist').classList.add('in-wishlist');
                }
            });
        })
        .catch(error => {
            console.error('Initial wishlist check failed:', error);
            fetch('/check_wishlist_status')
                .then(response => response.text())
                .then(text => console.error('Initial wishlist response body:', text))
                .catch(err => console.error('Debug fetch failed:', err));
        });

    // Enhance pagination UX with smooth scrolling
    const paginationLinks = document.querySelectorAll('.pagination-link');
    paginationLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const href = this.getAttribute('href');
            window.location.href = href;
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    });

    // Update cart count on pageshow (for browser back/forward)
    async function fetchAndUpdateCartCount() {
        try {
            const response = await fetch('/check_cart_status');
            if (response.ok) {
                const data = await response.json();
                updateCartCount(data.items ? data.items.length : 0);
            }
        } catch (error) {
            console.error('Error fetching cart count:', error);
        }
    }
    
    window.addEventListener('pageshow', fetchAndUpdateCartCount);

    // Check wishlist status on page load and on pageshow event
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
            console.error('Error fetching wishlist status:', error);
        }
    }

    fetchWishlistState();

    window.addEventListener('pageshow', (event) => {
        if (event.persisted || performance.navigation.type === 2) {
            console.log('Page loaded from cache or via history navigation. Re-fetching wishlist state.');
            fetchWishlistState();
        }
    });

    window.addEventListener('pageshow', function(event) {
        document.querySelectorAll('.product-card').forEach(card => {
            const productId = card.getAttribute('data-product-id');
            fetch(`/api/product_review_stats/${productId}`)
                .then(response => response.json())
                .then(data => {
                    const starsElem = card.querySelector('.product-rating .stars');
                    const countElem = card.querySelector('.product-rating .rating-count');
                    if (starsElem && data.avg_rating !== undefined) {
                        starsElem.innerHTML = Array.from({length: 5}, (_, i) => 
                            i < Math.round(data.avg_rating) ? '★' : '☆'
                        ).join('');
                    }
                    if (countElem && data.total_reviews !== undefined) {
                        countElem.textContent = `(${data.total_reviews})`;
                    }
                });
        });
    });
});