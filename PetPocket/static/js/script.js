document.addEventListener('DOMContentLoaded', function () {
    const carousel = document.querySelector('.carousel');
    const slides = document.querySelectorAll('.slide');
    const prevButton = document.querySelector('.carousel-control.prev');
    const nextButton = document.querySelector('.carousel-control.next');
    let currentSlide = 0;
  
    function thereAreSlides() {
      return slides.length > 0;
    }
  
    function showSlide(index) {
      if (!thereAreSlides()) {
        console.warn('No slides found in carousel.');
        return;
      }
      slides.forEach(slide => {
        slide.classList.remove('active');
        slide.style.transform = ''; // Reset transform
      });
      if (index >= 0 && index < slides.length) {
        slides[index].classList.add('active');
      }
    }
  
    function nextSlide() {
      if (!thereAreSlides()) return;
      currentSlide = (currentSlide + 1) % slides.length;
      showSlide(currentSlide);
    }
  
    function prevSlide() {
      if (!thereAreSlides()) return;
      currentSlide = (currentSlide - 1 + slides.length) % slides.length;
      showSlide(currentSlide);
    }
  
    /* @tweakable Time in seconds between automatic slides */
    const autoSlideInterval = 5;
    let autoSlideTimer;
    if (thereAreSlides()) {
      autoSlideTimer = setInterval(nextSlide, autoSlideInterval * 1000);
    } else {
      console.warn('Auto-slide disabled: no slides found.');
    }
  
    function resetTimer() {
      if (!thereAreSlides()) return;
      clearInterval(autoSlideTimer);
      autoSlideTimer = setInterval(nextSlide, autoSlideInterval * 1000);
    }
  
    if (thereAreSlides() && prevButton && nextButton) {
      prevButton.addEventListener('click', () => {
        prevSlide();
        resetTimer();
      });
      nextButton.addEventListener('click', () => {
        nextSlide();
        resetTimer();
      });
            } else {
      if (prevButton) prevButton.style.display = 'none';
      if (nextButton) nextButton.style.display = 'none';
      console.warn('Carousel buttons disabled: no slides found.');
    }
  
    if (thereAreSlides()) {
      showSlide(currentSlide);
    }
  
    // FAQ functionality
    const faqItems = document.querySelectorAll('.faq-item');
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        question.addEventListener('click', () => {
            const isActive = item.classList.contains('active');
            faqItems.forEach(i => i.classList.remove('active'));
            if (!isActive) {
                item.classList.add('active');
            }
        });
    });

    // Parallax effect on scroll
    const handleParallax = () => {
        const items = document.querySelectorAll('.faq-item');
        items.forEach(item => {
            const rect = item.getBoundingClientRect();
            const windowHeight = window.innerHeight;
            if (rect.top <= windowHeight * 0.8 && rect.bottom >= 0) {
                item.classList.add('parallax');
                item.style.animation = 'parallaxShift 0.8s ease-out forwards';
            }
        });
    };

    window.addEventListener('scroll', handleParallax);
    window.addEventListener('load', handleParallax);

    // Read More functionality
    const storyContainer = document.getElementById('storyContainer');
    const readMoreBtn = document.getElementById('readMoreBtn');
    if (storyContainer && readMoreBtn) {
        readMoreBtn.addEventListener('click', () => {
            storyContainer.classList.toggle('expanded');
            readMoreBtn.textContent = storyContainer.classList.contains('expanded') ? 'Read Less' : 'Read More';
        });
    }

    // Product sliders functionality
    const productLists = document.querySelectorAll('.product-list');
    productLists.forEach(list => {
        const slider = list.querySelector('.product-cards');
        const prevBtn = list.querySelector('.prev');
        const nextBtn = list.querySelector('.next');
        let scrollAmount = 0;
        const cardWidth = 270; // Width of each card + margin

        if (prevBtn && nextBtn && slider) {
            prevBtn.addEventListener('click', () => {
                scrollAmount = Math.max(scrollAmount - cardWidth, 0);
                slider.scrollTo({ left: scrollAmount, behavior: 'smooth' });
            });

            nextBtn.addEventListener('click', () => {
                const maxScroll = slider.scrollWidth - slider.clientWidth;
                scrollAmount = Math.min(scrollAmount + cardWidth, maxScroll);
                slider.scrollTo({ left: scrollAmount, behavior: 'smooth' });
            });
        }
    });

    // Fetch and render products
    function renderProducts(container, products) {
        if (!container) return;
        
        if (products.length === 0) {
            container.innerHTML = '<div class="no-products">No products available.</div>';
            return;
        }

        container.innerHTML = '';
        products.forEach(product => {
            const stars = '★'.repeat(Math.round(product.rating)) + '☆'.repeat(5 - Math.round(product.rating));
            const card = `
                <div class="product-card" data-product-id="${product.id}">
                    <div class="product-content" onclick="window.location.href='/product/${product.id}'">
                        <img src="${product.image_url || 'https://placehold.co/200x200/46f27a/ffffff?text=Product'}" 
                             alt="${product.name}">
                        <h3>${product.name}</h3>
                        <div class="product-details">
                            <span class="product-price">₹${product.price.toFixed(2)}</span>
                            <span class="product-rating">${stars} (${product.review_count})</span>
                        </div>
                    </div>
                    <div class="product-actions">
                        <button class="add-to-cart">
                            <span class="material-symbols-outlined">shopping_cart</span> Add to Cart
                        </button>
                        <button class="add-to-wishlist">
                            <span class="material-symbols-outlined">favorite</span>
                        </button>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', card);
        });

        // Attach event listeners to buttons
        container.querySelectorAll('.add-to-cart').forEach(btn => {
            btn.addEventListener('click', async function(e) {
                e.stopPropagation();
                const card = btn.closest('.product-card');
                const productId = parseInt(card.dataset.productId);
                if (btn.classList.contains('go-to-cart')) {
                    window.location.href = '/cart';
                    return;
                }
                btn.disabled = true;
                fetch('/add_to_cart', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
                    },
                    body: JSON.stringify({ product_id: productId, quantity: 1 })
                })
                .then(response => {
                    if (response.status === 401) {
                        window.location.href = '/signin';
                        return;
                    }
                    return response.json();
                })
                .then(data => {
                    btn.disabled = false;
                    if (data && data.success) {
                        btn.classList.add('go-to-cart');
                        btn.style.backgroundColor = '#4caf50';
                        btn.style.color = '#fff';
                        btn.innerHTML = '<span class="material-symbols-outlined">shopping_cart</span> Go to Cart';
                        updateCartCount(data.cart_count);
                    } else if (data && !data.success) {
                        alert(data.message || 'Failed to add to cart');
                    }
                })
                .catch(error => {
                    btn.disabled = false;
                    alert('Error adding to cart');
                });
            });
        });

        container.querySelectorAll('.add-to-wishlist').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const card = btn.closest('.product-card');
                const productId = parseInt(card.dataset.productId);
                fetch('/add_to_wishlist', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
                    },
                    body: JSON.stringify({ product_id: productId })
                })
                .then(response => {
                    if (response.status === 401) {
                        window.location.href = '/signin';
                        return;
                    }
                    return response.json();
                })
                .then(data => {
                    if (data && data.success) {
                        btn.classList.toggle('in-wishlist');
                        // Add animation
                        btn.classList.add('wishlist-animate');
                        setTimeout(() => btn.classList.remove('wishlist-animate'), 500);
                        // Toggle heart fill
                        const icon = btn.querySelector('.material-symbols-outlined');
                        if (btn.classList.contains('in-wishlist')) {
                            icon.style.fontVariationSettings = "'FILL' 1";
                        } else {
                            icon.style.fontVariationSettings = "'FILL' 0";
                        }
                    } else if (data && !data.success) {
                        alert(data.message || 'Failed to update wishlist');
                    }
                })
                .catch(error => {
                    alert('Error updating wishlist');
                });
            });
        });

        // Update wishlist status
        fetch('/check_wishlist_status')
            .then(response => response.json())
            .then(data => {
                const wishlistItems = data.items || [];
                container.querySelectorAll('.product-card').forEach(card => {
                    const productId = parseInt(card.dataset.productId);
                    const btn = card.querySelector('.add-to-wishlist');
                    const icon = btn.querySelector('.material-symbols-outlined');
                    if (wishlistItems.includes(productId)) {
                        btn.classList.add('in-wishlist');
                        icon.style.fontVariationSettings = "'FILL' 1";
                    } else {
                        btn.classList.remove('in-wishlist');
                        icon.style.fontVariationSettings = "'FILL' 0";
                    }
                });
            });

        // Update cart button state for products already in cart
        fetch('/check_cart_status')
            .then(response => response.json())
            .then(data => {
                const cartItems = data.items || [];
                container.querySelectorAll('.product-card').forEach(card => {
                    const productId = parseInt(card.dataset.productId);
                    if (cartItems.includes(productId)) {
                        const btn = card.querySelector('.add-to-cart');
                        btn.classList.add('go-to-cart');
                        btn.innerHTML = '<span class="material-symbols-outlined">shopping_cart</span> Go to Cart';
                        btn.style.backgroundColor = '#4caf50';
                        btn.style.color = '#fff';
                    } else {
                        const btn = card.querySelector('.add-to-cart');
                        btn.classList.remove('go-to-cart');
                        btn.innerHTML = '<span class="material-symbols-outlined">shopping_cart</span> <p class="cart-txt">Add to Cart</p>';
                        btn.style.backgroundColor = '';
                        btn.style.color = '';
                    }
                });
            });
    }

    // Fetch all home product sections from the new endpoint
    const recommendedContainer = document.getElementById('recommended-products');
    const petParentContainer = document.getElementById('pet-parent-loves');
    const bestSellersContainer = document.getElementById('best-sellers');
    if (recommendedContainer || petParentContainer || bestSellersContainer) {
        fetch('/api/home_products')
            .then(response => response.json())
            .then(data => {
                if (recommendedContainer) {
                    recommendedContainer.innerHTML = '';
                    renderProducts(recommendedContainer, data.recommendations || []);
                }
                if (petParentContainer) {
                    petParentContainer.innerHTML = '';
                    renderProducts(petParentContainer, data.pet_parent_loves || []);
                }
                if (bestSellersContainer) {
                    bestSellersContainer.innerHTML = '';
                    renderProducts(bestSellersContainer, data.best_sellers || []);
                }
            })
            .catch(error => {
                if (recommendedContainer) recommendedContainer.innerHTML = '<div class="error-message">Error loading recommended products.</div>';
                if (petParentContainer) petParentContainer.innerHTML = '<div class="error-message">Error loading products.</div>';
                if (bestSellersContainer) bestSellersContainer.innerHTML = '<div class="error-message">Error loading products.</div>';
                console.error('Error fetching home products:', error);
            });
    }

    // Cart functionality
    function handleAddToCart(productId, button) {
        fetch('/add_to_cart', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
            },
            body: JSON.stringify({ product_id: productId })
        })
        .then(response => {
            if (response.status === 401) {
                window.location.href = '/signin';
                return;
            }
            return response.json();
        })
        .then(data => {
            if (data && data.success) {
                button.classList.add('added');
                button.innerHTML = '<span class="material-symbols-outlined">check_circle</span> Added to Cart';
                setTimeout(() => {
                    button.classList.remove('added');
                    button.innerHTML = '<span class="material-symbols-outlined">shopping_cart</span> Add to Cart';
                }, 3000);
                updateCartCount(data.cart_count);
            } else if (data && !data.success) {
                console.error('Error adding to cart:', data.message);
            }
        })
        .catch(error => console.error('Error adding to cart:', error));
    }

    // Wishlist functionality
    function handleAddToWishlist(productId, button) {
        fetch('/add_to_wishlist', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || ''
            },
            body: JSON.stringify({ product_id: productId })
        })
        .then(response => {
            if (response.status === 401) {
                window.location.href = '/signin';
                return;
            }
            return response.json();
        })
        .then(data => {
            if (data && data.success) {
                button.classList.toggle('in-wishlist');
            } else if (data && !data.success) {
                console.error('Error toggling wishlist:', data.message);
            }
        })
        .catch(error => console.error('Error toggling wishlist:', error));
    }

    // Cart count functionality
    function updateCartCount(count) {
        const cartIcon = document.querySelector('.cart-icon');
        let cartBadge = document.querySelector('.cart-badge');
        // If count is undefined/null/NaN, treat as 1 (first product added)
        let safeCount = (typeof count === 'number' && !isNaN(count)) ? count : 1;
        if (cartIcon) {
            if (!cartBadge) {
                cartBadge = document.createElement('span');
                cartBadge.className = 'cart-badge cart-badge-visible';
                cartIcon.appendChild(cartBadge);
            }
            cartBadge.textContent = safeCount;
            if (safeCount > 0) {
                cartBadge.style.display = 'block';
                cartBadge.classList.add('cart-badge-visible');
                cartIcon.classList.add('cart-has-items');
            } else {
                cartBadge.style.display = 'none';
                cartBadge.classList.remove('cart-badge-visible');
                cartIcon.classList.remove('cart-has-items');
            }
        }
    }

    function fetchAndUpdateCartCount() {
        fetch('/check_cart_status')
            .then(response => response.json())
            .then(data => {
                updateCartCount(data.items.length);
            })
            .catch(error => console.error('Error fetching cart status:', error));
    }

    // Initialize cart count
        fetchAndUpdateCartCount();
    window.addEventListener('pageshow', fetchAndUpdateCartCount);

    // Make functions globally available
    window.handleAddToCart = handleAddToCart;
    window.handleAddToWishlist = handleAddToWishlist;

    /* Add this CSS for wishlist animation */
    if (!document.getElementById('wishlist-animate-style')) {
        const style = document.createElement('style');
        style.id = 'wishlist-animate-style';
        style.textContent = `
        .add-to-wishlist.wishlist-animate {
            animation: wishlist-pop 0.5s;
        }
        @keyframes wishlist-pop {
            0% { transform: scale(1); }
            50% { transform: scale(1.3); }
            100% { transform: scale(1); }
        }
        `;
        document.head.appendChild(style);
    }

    // After rendering products, also update cart/wishlist state on browser back/forward
    window.addEventListener('pageshow', function() {
        // For each product slider, re-fetch cart state and update buttons
        document.querySelectorAll('.product-cards').forEach(container => {
            fetch('/check_cart_status')
                .then(response => response.json())
                .then(data => {
                    const cartItems = data.items || [];
                container.querySelectorAll('.product-card').forEach(card => {
                        const productId = parseInt(card.dataset.productId);
                        const btn = card.querySelector('.add-to-cart');
                        if (btn) {
                            if (cartItems.includes(productId)) {
                                btn.classList.add('go-to-cart');
                                btn.innerHTML = '<span class="material-symbols-outlined">shopping_cart</span> Go to Cart';
                                btn.style.backgroundColor = '#4caf50';
                                btn.style.color = '#fff';
                            } else {
                                btn.classList.remove('go-to-cart');
                                btn.innerHTML = '<span class="material-symbols-outlined">shopping_cart</span> <p class="cart-txt">Add to Cart</p>';
                                btn.style.backgroundColor = '';
                                btn.style.color = '';
                            }
                        }
                    });
                });
            // Also re-fetch wishlist state and update heart fill
            fetch('/check_wishlist_status')
                .then(response => response.json())
                .then(data => {
                    const wishlistItems = data.items || [];
                    container.querySelectorAll('.product-card').forEach(card => {
                        const productId = parseInt(card.dataset.productId);
                        const btn = card.querySelector('.add-to-wishlist');
                        const icon = btn.querySelector('.material-symbols-outlined');
                        if (wishlistItems.includes(productId)) {
                            btn.classList.add('in-wishlist');
                            icon.style.fontVariationSettings = "'FILL' 1";
                        } else {
                            btn.classList.remove('in-wishlist');
                            icon.style.fontVariationSettings = "'FILL' 0";
                        }
                    });
                });
        });
    });

    // Carousel functionality for home page
    const homeCarousel = document.querySelector('.carousel');
    const homeSlides = document.querySelectorAll('.carousel-slide');
    const homePrevButton = document.getElementById('prevBtn');
    const homeNextButton = document.getElementById('nextBtn');
    let homeCurrentSlide = 0;

    function homeShowSlide(index) {
      if (homeSlides.length === 0) return;
      homeSlides.forEach((slide, i) => {
        slide.style.display = i === index ? 'block' : 'none';
        slide.classList.toggle('active', i === index);
      });
    }

    function homeNextSlide() {
      if (homeSlides.length === 0) return;
      homeCurrentSlide = (homeCurrentSlide + 1) % homeSlides.length;
      homeShowSlide(homeCurrentSlide);
    }

    function homePrevSlide() {
      if (homeSlides.length === 0) return;
      homeCurrentSlide = (homeCurrentSlide - 1 + homeSlides.length) % homeSlides.length;
      homeShowSlide(homeCurrentSlide);
    }

    let homeAutoSlideTimer;
    if (homeSlides.length > 0) {
      homeShowSlide(homeCurrentSlide);
      homeAutoSlideTimer = setInterval(homeNextSlide, 5000);
    }

    function homeResetTimer() {
      if (homeSlides.length === 0) return;
      clearInterval(homeAutoSlideTimer);
      homeAutoSlideTimer = setInterval(homeNextSlide, 5000);
    }

    if (homePrevButton && homeNextButton && homeSlides.length > 0) {
      homePrevButton.addEventListener('click', () => {
        homePrevSlide();
        homeResetTimer();
      });
      homeNextButton.addEventListener('click', () => {
        homeNextSlide();
        homeResetTimer();
      });
    }

    // Testimonial/Review Carousel functionality
    const reviewCards = document.querySelectorAll('.reviews-carousel .reviews-card');
    const reviewPrevBtn = document.getElementById('reviews-prev-btn');
    const reviewNextBtn = document.getElementById('reviews-next-btn');
    let reviewCurrent = 0;

    function showReview(index) {
      if (reviewCards.length === 0) return;
      reviewCards.forEach((card, i) => {
        card.style.display = i === index ? 'block' : 'none';
        card.classList.toggle('active', i === index);
      });
    }

    function nextReview() {
      if (reviewCards.length === 0) return;
      reviewCurrent = (reviewCurrent + 1) % reviewCards.length;
      showReview(reviewCurrent);
    }

    function prevReview() {
      if (reviewCards.length === 0) return;
      reviewCurrent = (reviewCurrent - 1 + reviewCards.length) % reviewCards.length;
      showReview(reviewCurrent);
    }

    if (reviewCards.length > 0) {
      showReview(reviewCurrent);
    }
    if (reviewPrevBtn && reviewNextBtn && reviewCards.length > 0) {
      reviewPrevBtn.addEventListener('click', prevReview);
      reviewNextBtn.addEventListener('click', nextReview);
    }
});
