(function() {
  "use strict";

  // ---------- PAGE SWITCH ----------
  const pageBtns = document.querySelectorAll('.page-btn');
  const pages = {
    page1: document.getElementById('page1'),
    page2: document.getElementById('page2')
  };

  pageBtns.forEach(btn => {
    btn.addEventListener('click', function() {
      const target = this.dataset.page;
      pageBtns.forEach(b => b.classList.remove('active'));
      this.classList.add('active');
      Object.keys(pages).forEach(key => {
        pages[key].classList.toggle('active-page', key === target);
      });
    });
  });

  // ---------- ELEMENTS ----------
  const promptInput = document.getElementById('promptInput');
  const generateBtn = document.getElementById('generateBtn');
  const imageResult = document.getElementById('imageResult');
  const galleryGrid = document.getElementById('galleryGrid');

  // In-memory history
  let imageHistory = [];

  // ---------- API CALL (connect to Python backend) ----------
  async function generateImageFromPrompt(prompt) {
    // In production: this calls your Flask/FastAPI backend
    // For demo, we simulate with canvas generation
    return new Promise((resolve) => {
      setTimeout(() => {
        const canvas = document.createElement('canvas');
        canvas.width = 512;
        canvas.height = 512;
        const ctx = canvas.getContext('2d');

        let hash = 0;
        for (let i = 0; i < prompt.length; i++) {
          hash = prompt.charCodeAt(i) + ((hash << 5) - hash);
        }
        const hue = Math.abs(hash % 360);
        const sat = 60 + (hash % 30);
        const lig = 50 + (hash % 20);

        const grd = ctx.createRadialGradient(256, 256, 30, 256, 256, 300);
        grd.addColorStop(0, `hsl(${hue}, ${sat}%, ${lig+20}%)`);
        grd.addColorStop(1, `hsl(${hue+40}, ${sat-10}%, ${lig-15}%)`);
        ctx.fillStyle = grd;
        ctx.fillRect(0, 0, 512, 512);

        for (let i = 0; i < 20; i++) {
          ctx.beginPath();
          const x = Math.random() * 512;
          const y = Math.random() * 512;
          const r = 20 + Math.random() * 80;
          const alpha = 0.1 + Math.random() * 0.3;
          ctx.arc(x, y, r, 0, Math.PI * 2);
          ctx.fillStyle = `hsla(${hue+60+i*20}, 80%, 70%, ${alpha})`;
          ctx.fill();
        }

        ctx.font = 'bold 28px Inter, sans-serif';
        ctx.fillStyle = 'rgba(255,255,255,0.7)';
        ctx.shadowColor = 'rgba(0,0,0,0.2)';
        ctx.shadowBlur = 12;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        const words = prompt.split(' ').slice(0, 3).join(' ');
        ctx.fillText('✨ ' + (words || 'AI'), 256, 256);

        const dataUrl = canvas.toDataURL('image/png');
        resolve(dataUrl);
      }, 900 + Math.random() * 600);
    });
  }

  // ---------- RENDER GALLERY ----------
  function renderGallery() {
    galleryGrid.innerHTML = '';
    if (imageHistory.length === 0) {
      galleryGrid.innerHTML = `<div class="empty-gallery"><i class="fas fa-box-open"></i><p>No images yet. Generate your first!</p></div>`;
      return;
    }
    const reversed = [...imageHistory].reverse();
    reversed.forEach((item) => {
      const div = document.createElement('div');
      div.className = 'gallery-item';
      div.innerHTML = `
        <img src="${item.dataUrl}" alt="generated">
        <div class="info">
          <p>${item.prompt}</p>
          <span><i class="far fa-clock"></i> just now</span>
        </div>
      `;
      galleryGrid.appendChild(div);
    });
  }

  // ---------- SHOW RESULT (with loading) ----------
  function setResultLoading(isLoading) {
    if (isLoading) {
      imageResult.innerHTML = `
        <div class="loading-spinner">
          <div class="spinner"></div>
          <span style="color:#4b5a6b; font-weight:500;">Generating...</span>
        </div>
      `;
      generateBtn.disabled = true;
      generateBtn.innerHTML = '<i class="fas fa-spinner fa-pulse"></i> Generating';
    } else {
      generateBtn.disabled = false;
      generateBtn.innerHTML = '<i class="fas fa-arrow-right"></i> Generate';
    }
  }

  function displayImage(dataUrl, prompt) {
    imageResult.innerHTML = `<img src="${dataUrl}" alt="generated image">`;
    imageHistory.push({ dataUrl, prompt });
    if (imageHistory.length > 20) imageHistory.shift();
    renderGallery();
  }

  // ---------- GENERATE ACTION ----------
  async function handleGenerate() {
    const prompt = promptInput.value.trim();
    if (!prompt) {
      alert('Please describe an image.');
      return;
    }

    setResultLoading(true);
    try {
      const dataUrl = await generateImageFromPrompt(prompt);
      displayImage(dataUrl, prompt);
    } catch (error) {
      alert('Generation failed. Please try again.');
      console.error(error);
    } finally {
      setResultLoading(false);
    }
  }

  // ---------- EVENT LISTENERS ----------
  generateBtn.addEventListener('click', handleGenerate);
  promptInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleGenerate();
  });

  document.getElementById('refreshHistory').addEventListener('click', function() {
    renderGallery();
    this.style.transform = 'rotate(360deg)';
    setTimeout(() => this.style.transform = '', 300);
  });

  // ---------- SEED WITH A DEMO IMAGE ----------
  window.addEventListener('load', function() {
    const demoCanvas = document.createElement('canvas');
    demoCanvas.width = 200;
    demoCanvas.height = 200;
    const ctx = demoCanvas.getContext('2d');
    const grd = ctx.createLinearGradient(0, 0, 200, 200);
    grd.addColorStop(0, '#4f7df3');
    grd.addColorStop(1, '#6c5ce7');
    ctx.fillStyle = grd;
    ctx.fillRect(0, 0, 200, 200);
    ctx.fillStyle = 'white';
    ctx.font = 'bold 22px Inter';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText('✨ CHITRA', 100, 100);
    const demoUrl = demoCanvas.toDataURL('image/png');
    imageHistory.push({ dataUrl: demoUrl, prompt: 'welcome to CHITRA' });
    renderGallery();
    displayImage(demoUrl, 'welcome to CHITRA');
  });

})();
