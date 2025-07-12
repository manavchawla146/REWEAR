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