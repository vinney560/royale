// To use this, you need to have this 👇👇
// <canvas id="particles-canvas"></canvas>
// In your HTML. Also, there is CSS file
// need for position bt its optional.

(function() {
    const canvas = document.getElementById('particles-canvas');
    const ctx = canvas.getContext('2d');
    let w, h;
    const particles = [];
    const NUM = 80;

    function resize() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
    }
    window.addEventListener('resize', resize);
    resize();

    class Particle {
        constructor() {
            this.reset();
        }
        reset() {
            this.x = Math.random() * w;
            this.y = Math.random() * h;
            this.size = Math.random() * 2 + 1.2;
            this.speedX = (Math.random() - 0.5) * 0.3;
            this.speedY = (Math.random() - 0.5) * 0.3;
            this.opacity = Math.random() * 0.5 + 0.2;
        }
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            if (this.x < 0 || this.x > w) this.speedX *= -1;
            if (this.y < 0 || this.y > h) this.speedY *= -1;
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(120, 220, 200, ${this.opacity})`;
            ctx.fill();
        }
    }

    for (let i = 0; i < NUM; i++) {
        particles.push(new Particle());
    }

    function drawLines() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 150) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(80, 200, 180, ${0.12 * (1 - dist / 150)})`;
                    ctx.lineWidth = 0.6;
                    ctx.stroke();
                }
            }
        }
    }

    function animateParticles() {
        ctx.clearRect(0, 0, w, h);
        particles.forEach(p => {
            p.update();
            p.draw();
        });
        drawLines();
        requestAnimationFrame(animateParticles);
    }

    animateParticles();
})();