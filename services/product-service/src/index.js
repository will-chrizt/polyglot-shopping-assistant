//product-service
const express = require('express');
const app = express();
const PORT = 8001;

const PRODUCTS = [
    // --- Laptops (7 products) ---
    { id: 'p1', name: 'Lenovo Ideapad 3', category: 'laptop', price: 52000, tags: ['coding', 'budget', 'student'] },
    { id: 'p2', name: 'MacBook Air M1', category: 'laptop', price: 84990, tags: ['coding', 'battery', 'portable'] },
    { id: 'p3', name: 'Dell XPS 15', category: 'laptop', price: 150000, tags: ['power-user', 'coding', 'design', 'high-performance'] },
    { id: 'p4', name: 'HP Spectre x360', category: 'laptop', price: 135000, tags: ['2-in-1', 'touchscreen', 'creative'] },
    { id: 'p5', name: 'Acer Aspire 5', category: 'laptop', price: 45000, tags: ['budget', 'everyday-use', 'multimedia'] },
    { id: 'p6', name: 'Razer Blade 15', category: 'laptop', price: 180000, tags: ['gaming', 'high-refresh', 'powerful'] },
    { id: 'p7', name: 'Microsoft Surface Laptop 4', category: 'laptop', price: 110000, tags: ['sleek', 'portable', 'professional'] },

    // --- Accessories (7 products) ---
    { id: 'a1', name: 'Logitech MX Master 3S', category: 'accessory', price: 8990, tags: ['productivity', 'ergonomic', 'mouse'] },
    { id: 'a2', name: 'Keychron K2', category: 'accessory', price: 7500, tags: ['mechanical-keyboard', 'productivity', 'wireless'] },
    { id: 'a3', name: 'Anker PowerCore III', category: 'accessory', price: 4500, tags: ['portable', 'charging', 'power-bank'] },
    { id: 'a4', name: 'Samsung T7 SSD 1TB', category: 'accessory', price: 10500, tags: ['storage', 'external-drive', 'fast'] },
    { id: 'a5', name: 'Logitech C920 Webcam', category: 'accessory', price: 6000, tags: ['webcam', 'video-conferencing', 'hd'] },
    { id: 'a6', name: 'Corsair K70 RGB Pro', category: 'accessory', price: 12500, tags: ['mechanical-keyboard', 'gaming', 'rgb'] },
    { id: 'a7', name: 'Dual Monitor Stand', category: 'accessory', price: 5500, tags: ['desk-setup', 'ergonomic', 'stand'] },

    // --- Audio (7 products) ---
    { id: 'au1', name: 'Sony WH-1000XM5', category: 'audio', price: 29990, tags: ['noise-cancelling', 'travel', 'headphones'] },
    { id: 'au2', name: 'Bose QuietComfort Earbuds II', category: 'audio', price: 25900, tags: ['earbuds', 'noise-cancelling', 'wireless'] },
    { id: 'au3', name: 'JBL Flip 6', category: 'audio', price: 9000, tags: ['speaker', 'portable', 'waterproof'] },
    { id: 'au4', name: 'Apple AirPods Pro 2', category: 'audio', price: 24900, tags: ['earbuds', 'apple-ecosystem', 'wireless'] },
    { id: 'au5', name: 'Sennheiser HD 660S2', category: 'audio', price: 40000, tags: ['audiophile', 'open-back', 'headphones'] },
    { id: 'au6', name: 'HyperX QuadCast S', category: 'audio', price: 15000, tags: ['microphone', 'streaming', 'podcast'] },
    { id: 'au7', name: 'Marshall Stanmore II', category: 'audio', price: 28000, tags: ['speaker', 'bluetooth', 'retro'] },
];

app.get('/products', (req, res) => {
    const { q, category, priceMin, priceMax, limit } = req.query;
    let out = PRODUCTS;
    if (category) out = out.filter(p => p.category === category);
    if (q) out = out.filter(p => p.name.toLowerCase().includes(q.toLowerCase()));
    if (priceMin) out = out.filter(p => p.price >= Number(priceMin));
    if (priceMax) out = out.filter(p => p.price <= Number(priceMax));
    res.json(out.slice(0, Number(limit) || 20));
});

app.get('/products/:id', (req, res) => {
    const p = PRODUCTS.find(p => p.id === req.params.id);
    if (!p) return res.status(404).json({ error: 'Not found' });
    res.json(p);
});

const HOST = process.env.HOST || '0.0.0.0';
app.listen(PORT, HOST, () => {
  console.log(`✅ Product service running at ${HOST}:${PORT}`);
});
