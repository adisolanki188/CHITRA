(function() {
  "use strict";

  // Page switching
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

  // Elements
  const promptInput = document.getElementById('promptInput');
  const generateBtn = document.getElementById('generateBtn');
  const imageResult = document.getElementById('imageResult');
  const galleryGrid = document.getElementById('galleryGrid');
  let imageHistory = [];

  // Load history from localStorage
  function loadHistory() {
    try {
      const saved = localStorage.getItem('chitra_history');
      if (saved) {
        imageHistory = JSON.parse(saved);
        renderGallery();
      }
    } catch (e) {
      console.log('No saved history');
    }
  }

  // Save history to localStorage
  function saveHistory() {
    try {
      localStorage.setItem('chitra_history', JSON.stringify(imageHistory));
    } catch (e) {
      console.log('Could not save history');
    }
  }

  async function generateImageFromPrompt(prompt) {
    const response = await fetch('/generate', {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ prompt })
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Server error: ${response.status} - ${errorText}`);
    }
    
    const data = await response.json();
    if (data.error) {
      throw new Error(data.error);
    }
    return data;
  }

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
          <span><i class="far fa-clock"></i> ${item.timestamp || 'just now'}</span>
        </div>
      `;
      galleryGrid.appendChild(div);
    });
  }

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

  function displayImage(dataUrl, prompt, timestamp) {
    imageResult.innerHTML = `<img src="${dataUrl}" alt="generated image">`;
    imageHistory.push({ 
      dataUrl, 
      prompt, 
      timestamp: timestamp || new Date().toLocaleString() 
    });
    if (imageHistory.length > 20) imageHistory.shift();
    saveHistory();
    renderGallery();
  }

  async function handleGenerate() {
    const prompt = promptInput.value.trim();
    if (!prompt) {
      alert('Please describe an image.');
      return;
    }

    setResultLoading(true);
    try {
      const result = await generateImageFromPrompt(prompt);
      displayImage(result.image, result.prompt, result.timestamp);
    } catch (error) {
      alert('Generation failed: ' + error.message);
      console.error('Error:', error);
    } finally {
      setResultLoading(false);
    }
  }

  // Event listeners
  generateBtn.addEventListener('click', handleGenerate);
  promptInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') handleGenerate();
  });

  document.getElementById('refreshHistory').addEventListener('click', function() {
    renderGallery();
    this.style.transform = 'rotate(360deg)';
    setTimeout(() => this.style.transform = '', 300);
  });

  // Load history on startup
  loadHistory();

  // Seed with demo image if no history
  if (imageHistory.length === 0) {
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
    imageHistory.push({ 
      dataUrl: demoUrl, 
      prompt: 'Welcome to CHITRA', 
      timestamp: new Date().toLocaleString() 
    });
    saveHistory();
    renderGallery();
    displayImage(demoUrl, 'Welcome to CHITRA', new Date().toLocaleString());
  }
})();
