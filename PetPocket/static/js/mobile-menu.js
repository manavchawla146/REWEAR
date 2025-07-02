document.addEventListener('DOMContentLoaded', function () {
  const hamburgerMenu = document.querySelector('.hamburger-menu');
  const mobileMenu = document.querySelector('.mobile-menu');
  const closeMenu = document.querySelector('.close-menu');

  /* @tweakable Duration of the mobile menu animation in seconds */
  const animationDuration = 0.3;

  hamburgerMenu.addEventListener('click', function () {
    mobileMenu.style.display = 'flex';
  });

  closeMenu.addEventListener('click', function () {
    mobileMenu.style.display = 'none';
    /* @tweakable  Delay in seconds before hiding the mobile menu */
    const hideDelay = 0.3;
    setTimeout(() => {
      mobileMenu.style.display = 'none';
    }, hideDelay * 1000);
  });

  // Blog grid scroll logic 
  const blogGrid = document.querySelector('.blog-grid');
  if (blogGrid) {
    let isScrollingBlog = false;
    let startX;
    let blogScrollLeft;

    blogGrid.addEventListener('mousedown', e => {
      isScrollingBlog = true;
      startX = e.pageX - blogGrid.offsetLeft;
      blogScrollLeft = blogGrid.scrollLeft;
    });

    blogGrid.addEventListener('mouseleave', () => {
      isScrollingBlog = false;
    });

    blogGrid.addEventListener('mouseup', () => {
      isScrollingBlog = false;
    });

    blogGrid.addEventListener('mousemove', e => {
      if (!isScrollingBlog) return;
      e.preventDefault();
      const x = e.pageX - blogGrid.offsetLeft;
      const walk = (x - startX) * 2;
      blogGrid.scrollLeft = blogScrollLeft - walk;
    });
  }
});