const express = require('express');
const app = express();
const PORT = process.env.PORT || 8001;


const PRODUCTS = [
{ id: 'p1', name: 'Lenovo Ideapad 3', category: 'laptop', price: 52000, tags:['coding','budget'] },
{ id: 'p2', name: 'MacBook Air M1', category: 'laptop', price: 84990, tags:['coding','battery'] },
{ id: 'p3', name: 'Logitech MX Master 3S', category: 'accessory', price: 8990, tags:['productivity'] }
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


app.listen(PORT, () => console.log(`Product service on ${PORT}`));
