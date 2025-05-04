export const fadeIn = {
    beforeEnter(el) {
      el.style.opacity = 0;
    },
    enter(el, done) {
      let opacity = 0;
      const interval = setInterval(() => {
        opacity += 0.1;
        el.style.opacity = opacity;
        if (opacity >= 1) {
          clearInterval(interval);
          done();
        }
      }, 30);
    },
    leave(el, done) {
      let opacity = 1;
      const interval = setInterval(() => {
        opacity -= 0.1;
        el.style.opacity = opacity;
        if (opacity <= 0) {
          clearInterval(interval);
          done();
        }
      }, 30);
    }
  };
  
  export const slideUp = {
    beforeEnter(el) {
      el.style.opacity = 0;
      el.style.transform = 'translateY(20px)';
    },
    enter(el, done) {
      let opacity = 0;
      let y = 20;
      const interval = setInterval(() => {
        opacity += 0.1;
        y -= 2;
        el.style.opacity = opacity;
        el.style.transform = `translateY(${y}px)`;
        if (opacity >= 1) {
          el.style.transform = 'translateY(0)';
          clearInterval(interval);
          done();
        }
      }, 30);
    },
    leave(el, done) {
      let opacity = 1;
      let y = 0;
      const interval = setInterval(() => {
        opacity -= 0.1;
        y -= 2;
        el.style.opacity = opacity;
        el.style.transform = `translateY(${y}px)`;
        if (opacity <= 0) {
          clearInterval(interval);
          done();
        }
      }, 30);
    }
  };